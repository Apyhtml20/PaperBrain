import os
from huggingface_hub import InferenceClient

HF_TOKEN   = os.getenv("HF_TOKEN", "")
MODEL_NAME = os.getenv("HF_MODEL", "Qwen/Qwen2.5-72B-Instruct")

LEVEL_DESCRIPTIONS = {
    "beginner":     "de manière très simple, comme si tu expliquais à un lycéen, avec des analogies du quotidien",
    "intermediate": "de manière claire avec les concepts essentiels, pour un étudiant universitaire",
    "advanced":     "de manière approfondie et technique, pour un expert du domaine",
}

_client = None

def _get_client() -> InferenceClient:
    global _client
    if _client is None:
        _client = InferenceClient(token=HF_TOKEN or None)
    return _client


def _call_hf(system: str, user: str, max_tokens: int = 1024, temperature: float = 0.5) -> str:
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


def simple_explain(concept: str, level: str = "intermediate") -> str:
    level_desc = LEVEL_DESCRIPTIONS.get(level, LEVEL_DESCRIPTIONS["intermediate"])

    system = (
        "Tu es un professeur pédagogue expert. "
        "Réponds dans la même langue que le concept demandé."
    )
    user = (
        f"Explique le concept suivant {level_desc}.\n\n"
        "Structure ta réponse avec :\n"
        "1. Une définition courte et claire\n"
        "2. Les points clés à retenir\n"
        "3. Un exemple concret\n"
        "4. Les applications pratiques\n\n"
        f"Concept : {concept}"
    )

    return _call_hf(system, user, max_tokens=1024)