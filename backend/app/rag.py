import chromadb

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "smartstudy_docs"


def get_chroma_client():
    return chromadb.PersistentClient(path=CHROMA_PATH)


def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )


def add_documents(chunks: list, metadatas: list, ids: list):
    collection = get_collection()
    collection.add(documents=chunks, metadatas=metadatas, ids=ids)


def query_documents(query: str, n_results: int = 4) -> dict:
    collection = get_collection()
    count = collection.count()
    if count == 0:
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
    actual_n = min(n_results, count)
    return collection.query(query_texts=[query], n_results=actual_n)


def delete_collection():
    client = get_chroma_client()
    client.delete_collection(COLLECTION_NAME)