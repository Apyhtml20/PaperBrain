import os
from huggingface_hub import InferenceClient

HF_TOKEN   = os.getenv("HF_TOKEN", "")
MODEL_NAME = os.getenv("HF_MODEL", "Qwen/Qwen2.5-72B-Instruct")
RELEVANCE_THRESHOLD = 0.4

_client = None

def _get_client() -> InferenceClient:
    global _client
    if _client is None:
        _client = InferenceClient(token=HF_TOKEN or None)
    return _client


def _call_hf(system: str, user: str, max_tokens: int = 1024, temperature: float = 0.4) -> str:
    client = _get_client()
    response = client.chat_completion(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


def rag_qa(query: str, history_text: str = "") -> tuple[str, list[str]]:
    from app.rag import query_documents

    results   = query_documents(query, n_results=3)
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas",  [[]])[0]
    distances = results.get("distances",  [[]])[0]

    relevant_docs = [
        (doc, meta)
        for doc, meta, dist in zip(documents, metadatas, distances)
        if dist < RELEVANCE_THRESHOLD
    ]

    if not relevant_docs:
        return ("Je n'ai pas trouvé d'information pertinente dans vos cours.", [])

    context = "\n\n---\n\n".join([doc for doc, _ in relevant_docs])
    sources  = list(set([meta.get("source", "inconnu") for _, meta in relevant_docs]))

    system = (
        "Tu es un assistant pédagogique RAG. "
        "Réponds à la question en te basant UNIQUEMENT sur le contexte fourni. "
        "Si la réponse n'est pas dans le contexte, dis-le clairement. "
        "Réponds dans la même langue que la question."
    )
    history_section = f"Historique:\n{history_text}\n\n" if history_text else ""
    user = f"{history_section}Contexte :\n{context[:3000]}\n\nQuestion : {query}"

    answer = _call_hf(system, user)
    return answer, sources