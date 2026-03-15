import os
from huggingface_hub import InferenceClient

HF_TOKEN   = os.getenv("HF_TOKEN", "")
MODEL_NAME = os.getenv("HF_MODEL", "Qwen/Qwen2.5-72B-Instruct")

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


def generate_resume(text: str = None, file_path: str = None) -> str:
    if file_path and not text:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            return f"Erreur lors de la lecture du fichier : {e}"

    if not text:
        return "Aucun texte ou fichier fourni."

    system = (
        "Tu es un assistant pédagogique expert en synthèse de documents. "
        "Réponds dans la même langue que le texte fourni."
    )
    user = (
        "Résume le texte suivant de façon claire et structurée. "
        "Utilise des titres et des points clés.\n\n"
        f"Texte :\n{text[:4000]}"
    )

    return _call_hf(system, user, max_tokens=1024)