import os
import re

import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = "./chroma_db"
COLLECTION_PREFIX = "smartstudy_docs"

# Multilingual model (French content/queries need this — the default Chroma
# embedding function, MiniLM-L6-v2, is English-only and performs poorly on French).
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2"
)

_embedding_fn = None


def _get_embedding_fn():
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
        embedding_function=_get_embedding_fn(),
        metadata={"hnsw:space": "cosine"},
    )


def add_documents(chunks: list, metadatas: list, ids: list, user_id: str = "anonymous"):
    collection = get_collection(user_id)
    collection.add(documents=chunks, metadatas=metadatas, ids=ids)


def query_documents(query: str, user_id: str = "anonymous", n_results: int = 4) -> dict:
    collection = get_collection(user_id)
    count = collection.count()
    if count == 0:
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
    # Over-fetch then dedupe/trim, so near-duplicate chunks don't crowd out
    # genuinely different context.
    actual_n = min(max(n_results * 3, n_results), count)
    raw = collection.query(query_texts=[query], n_results=actual_n)
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
