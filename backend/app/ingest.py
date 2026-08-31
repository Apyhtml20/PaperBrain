import os
import re
import uuid

from app.rag import add_documents, get_collection

CHUNK_SIZE = 600
CHUNK_OVERLAP = 80

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])\s+")


def _split_sentences(text: str) -> list:
    return [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list:
    """Découpe le texte en chunks avec overlap, en respectant les limites de phrases."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    sentences = []
    for para in paragraphs:
        sentences.extend(_split_sentences(para))

    if not sentences:
        return []

    chunks = []
    current = ""

    for sentence in sentences:
        candidate = f"{current} {sentence}".strip() if current else sentence

        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current.strip())
            # Carry the tail of the previous chunk forward as overlap so
            # context isn't lost at chunk boundaries.
            current = (current[-overlap:] + " " + sentence).strip() if overlap else sentence
        else:
            current = sentence

        # A single sentence longer than chunk_size: hard-split by characters.
        while len(current) > chunk_size * 2:
            head, current = current[:chunk_size], current[chunk_size - overlap:]
            chunks.append(head.strip())

    if current:
        chunks.append(current.strip())

    return [c for c in chunks if c]


def read_file(file_path: str) -> str:
    """Lit un fichier PDF, DOCX ou TXT et retourne le texte."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    elif ext == ".pdf":
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                pages = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        pages.append(text)
                return "\n\n".join(pages)
        except ImportError:
            raise ImportError("pdfplumber requis: pip install pdfplumber")

    elif ext in [".docx", ".doc"]:
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except ImportError:
            raise ImportError("python-docx requis: pip install python-docx")

    else:
        raise ValueError(f"Format non supporté: {ext}. Acceptés: .pdf, .txt, .docx")


def check_duplicate(file_name: str, user_id: str = "anonymous") -> bool:
    """Vérifie si le document existe déjà dans la collection de l'utilisateur."""
    try:
        collection = get_collection(user_id)
        results = collection.get(where={"source": file_name})
        return len(results.get("ids", [])) > 0
    except Exception:
        return False


def ingest_document(file_path: str, subject: str = "general", user_id: str = "anonymous") -> int:
    """Ingère un document dans la collection de l'utilisateur. Retourne le nombre de chunks."""
    file_name = os.path.basename(file_path)

    # Supprimer les anciens chunks si le fichier existe déjà
    try:
        collection = get_collection(user_id)
        old = collection.get(where={"source": file_name})
        if old.get("ids"):
            collection.delete(ids=old["ids"])
            print(f"🗑️  Anciens chunks supprimés pour '{file_name}'")
    except Exception as e:
        print(f"Warning suppression: {e}")

    # Lire et découper
    text = read_file(file_path)
    if not text.strip():
        raise ValueError("Le document est vide ou illisible")

    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("Impossible de découper le document en chunks")

    # Préparer les métadonnées
    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [
        {
            "source": file_name,
            "subject": subject,
            "chunk_index": i,
            "total_chunks": len(chunks),
        }
        for i in range(len(chunks))
    ]

    add_documents(chunks, metadatas, ids, user_id=user_id)
    print(f"✅ {len(chunks)} chunks ingérés depuis '{file_name}' (matière: {subject}, user: {user_id})")
    return len(chunks)
