import os
import uuid
from app.rag import add_documents, get_collection

CHUNK_SIZE = 600
CHUNK_OVERLAP = 80


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list:
    """Découpe le texte en chunks avec overlap."""
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) < chunk_size:
            current += ("\n\n" + para) if current else para
        else:
            if current:
                chunks.append(current.strip())
            current = para

    if current:
        chunks.append(current.strip())

    # Si les paragraphes sont trop grands, découper par caractères
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > chunk_size * 2:
            for i in range(0, len(chunk), chunk_size - overlap):
                part = chunk[i:i + chunk_size]
                if part.strip():
                    final_chunks.append(part.strip())
        else:
            final_chunks.append(chunk)

    return final_chunks


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


def check_duplicate(file_name: str) -> bool:
    """Vérifie si le document existe déjà dans ChromaDB."""
    try:
        collection = get_collection()
        results = collection.get(where={"source": file_name})
        return len(results.get("ids", [])) > 0
    except:
        return False


def ingest_document(file_path: str, subject: str = "general") -> int:
    """Ingère un document dans ChromaDB. Retourne le nombre de chunks."""
    file_name = os.path.basename(file_path)

    # Supprimer les anciens chunks si le fichier existe déjà
    try:
        collection = get_collection()
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
            "total_chunks": len(chunks)
        }
        for i in range(len(chunks))
    ]

    add_documents(chunks, metadatas, ids)
    print(f"✅ {len(chunks)} chunks ingérés depuis '{file_name}' (matière: {subject})")
    return len(chunks)