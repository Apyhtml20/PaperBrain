"""LLM routing via LiteLLM: cascading fallback across Groq, HuggingFace and
OpenAI. Only providers with a configured API key are added to the chain, so
the app keeps working with whichever subset of keys is set. If the first
provider errors (quota, timeout, outage), LiteLLM retries with the next one
in the chain automatically.
"""
import os

from litellm import Router

GROQ_MODEL = os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile")
HF_MODEL = os.getenv("HF_MODEL", "Qwen/Qwen2.5-72B-Instruct")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Priority order for the fallback chain (first available wins).
FALLBACK_ORDER = [
    p.strip()
    for p in os.getenv("LLM_FALLBACK_ORDER", "groq,huggingface,openai").split(",")
    if p.strip()
]

_PROVIDERS = {
    "groq": {
        "model": GROQ_MODEL,
        "api_key": os.getenv("GROQ_API_KEY"),
    },
    "huggingface": {
        "model": f"huggingface/{HF_MODEL}",
        "api_key": os.getenv("HF_TOKEN"),
    },
    "openai": {
        "model": OPENAI_MODEL,
        "api_key": os.getenv("OPENAI_API_KEY"),
    },
}

_router = None
_primary_model_name = None


def _build_router() -> tuple[Router, str]:
    model_list = []
    for provider in FALLBACK_ORDER:
        cfg = _PROVIDERS.get(provider)
        if not cfg or not cfg["api_key"]:
            continue  # pas de clé configurée: on saute ce provider
        model_list.append({
            "model_name": f"paperbrain-{provider}",
            "litellm_params": {"model": cfg["model"], "api_key": cfg["api_key"]},
        })

    if not model_list:
        raise RuntimeError(
            "Aucune clé API configurée pour le LLM. "
            "Définir au moins GROQ_API_KEY, HF_TOKEN ou OPENAI_API_KEY."
        )

    names = [m["model_name"] for m in model_list]
    fallbacks = [{names[0]: names[1:]}] if len(names) > 1 else []

    router = Router(model_list=model_list, fallbacks=fallbacks, num_retries=0)
    return router, names[0]


def _get_router() -> tuple[Router, str]:
    global _router, _primary_model_name
    if _router is None:
        _router, _primary_model_name = _build_router()
    return _router, _primary_model_name


def complete(system: str, user: str, max_tokens: int = 1024, temperature: float = 0.4) -> str:
    router, primary = _get_router()
    response = router.completion(
        model=primary,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()
