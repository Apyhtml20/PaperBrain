import os
import re

import chromadb
from chromadb.utils import embedding_functions
from rank_bm25 import BM25Plus

CHROMA_PATH = "./chroma_db"
COLLECTION_PREFIX = "smartstudy_docs"

# Multilingual model (French content/queries need this — the default Chroma
# embedding function, MiniLM-L6-v2, is English-only and performs poorly on French).
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2"
)

# Reciprocal Rank Fusion constant (standard value from the RRF literature —
# large enough that a single method's #1 result doesn't totally dominate).
RRF_K = 60

_TOKEN_RE = re.compile(r"\w+", re.UNICODE)
_embedding_fn = None


def _tokenize(text: str) -> list:
    return _TOKEN_RE.findall(text.lower())


def get_embedding_fn():
    """Modèle multilingue partagé — aussi réutilisé par app.cache pour le
    cache sémantique, afin de ne charger le modèle qu'une seule fois."""
    global _embedding_fn
    if _embedding_fn is None:
        _embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
    return _embedding_fn


def get_chroma_client():
    return chromadb.PersistentClient(path=CHROMA_PATH)


def _safe_collection_name(user_id: str) -> str:
    """Chaque utilisateur a sa propre collection: isolation stricte des documents."""
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", str(user_id))
    return f"{COLLECTION_PREFIX}_{safe}"


def get_collection(user_id: str = "anonymous"):
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=_safe_collection_name(user_id),
        embedding_function=get_embedding_fn(),
        metadata={"hnsw:space": "cosine"},
    )


def add_documents(chunks: list, metadatas: list, ids: list, user_id: str = "anonymous"):
    collection = get_collection(user_id)
    collection.add(documents=chunks, metadatas=metadatas, ids=ids)


def query_documents(query: str, user_id: str = "anonymous", n_results: int = 4) -> dict:
    """Recherche hybride: fusionne le classement sémantique (embeddings) et le
    classement BM25 (mots-clés) par Reciprocal Rank Fusion. Le vectoriel seul
    rate les termes rares/exacts (sigles, noms propres, formules) que BM25
    retrouve; BM25 seul rate les reformulations. La fusion prend le meilleur
    des deux sans avoir à normaliser des scores sur des échelles différentes.
    """
    collection = get_collection(user_id)
    count = collection.count()
    if count == 0:
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    corpus = collection.get()
    ids       = corpus["ids"]
    documents = corpus["documents"]
    metadatas = corpus["metadatas"]
    doc_by_id  = dict(zip(ids, documents))
    meta_by_id = dict(zip(ids, metadatas))

    # Classement sémantique — interroger tout le corpus donne une distance
    # cosinus pour chaque chunk, pas seulement le top-k.
    vector = collection.query(query_texts=[query], n_results=count)
    vector_ids       = vector["ids"][0]
    vector_distances = vector["distances"][0]
    vector_rank      = {id_: rank for rank, id_ in enumerate(vector_ids)}
    distance_by_id   = dict(zip(vector_ids, vector_distances))

    # Classement BM25 — mots-clés exacts (sigles, termes techniques, chiffres).
    # BM25Plus (pas BM25Okapi): l'IDF classique tombe à zéro pour un terme
    # présent dans la moitié des documents ou plus — fréquent avec des chunks
    # courts et thématiquement proches — et le terme devient invisible pour
    # le score. BM25Plus garde un IDF toujours positif.
    bm25 = BM25Plus([_tokenize(doc) for doc in documents])
    bm25_scores = bm25.get_scores(_tokenize(query))
    bm25_order  = sorted(range(len(ids)), key=lambda i: bm25_scores[i], reverse=True)
    bm25_rank   = {ids[i]: rank for rank, i in enumerate(bm25_order)}

    fused = sorted(
        ids,
        key=lambda id_: 1 / (RRF_K + vector_rank.get(id_, count) + 1)
                       + 1 / (RRF_K + bm25_rank.get(id_, count) + 1),
        reverse=True,
    )

    # Over-fetch then dedupe/trim, so near-duplicate chunks don't crowd out
    # genuinely different context.
    top_ids = fused[: max(n_results * 3, n_results)]
    raw = {
        "documents": [[doc_by_id[id_] for id_ in top_ids]],
        "metadatas": [[meta_by_id[id_] for id_ in top_ids]],
        "distances": [[distance_by_id.get(id_, 2.0) for id_ in top_ids]],
    }
    return _dedupe_results(raw, keep=n_results)


def _dedupe_results(raw: dict, keep: int) -> dict:
    documents = raw.get("documents", [[]])[0]
    metadatas = raw.get("metadatas", [[]])[0]
    distances = raw.get("distances", [[]])[0]

    seen_sources_chunks = set()
    seen_text_prefixes = set()
    docs, metas, dists = [], [], []

    for doc, meta, dist in zip(documents, metadatas, distances):
        prefix = doc[:120].strip().lower()
        key = (meta.get("source"), meta.get("chunk_index"))
        if key in seen_sources_chunks or prefix in seen_text_prefixes:
            continue
        seen_sources_chunks.add(key)
        seen_text_prefixes.add(prefix)
        docs.append(doc)
        metas.append(meta)
        dists.append(dist)
        if len(docs) >= keep:
            break

    return {"documents": [docs], "metadatas": [metas], "distances": [dists]}


def delete_collection(user_id: str = "anonymous"):
    client = get_chroma_client()
    client.delete_collection(_safe_collection_name(user_id))
