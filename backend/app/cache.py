"""Semantic response cache backed by Valkey + BetterDB (see docker-compose.yml).

Caches full agent results (not just raw LLM text) keyed by embedding similarity,
so a paraphrased question ("C'est quoi la mitose ?" vs "Peux-tu expliquer la
mitose ?") still hits the cache instead of re-billing the LLM. BetterDB Monitor
auto-discovers every cache registered here (via Valkey's `__betterdb:caches`
hash) and exposes hit-rate / cost-saved / threshold-recommendation metrics —
that's the "surveiller mon cache" half of the pipeline; BetterDB also watches
Valkey itself (slowlog, hot keys, memory) for the "surveiller mon rag" half.

Isolation: `chat` and `rag-qa` can echo private conversation history or a
user's own uploaded documents back in the answer, so they get one cache
namespace per user_id (same isolation model as the ChromaDB collections in
app/rag.py). `quiz`, `flashcards`, `explain` and `resume` are pure
topic -> content generations with nothing user-specific in them, so their
cache is shared across all users — that's where most of the cost/latency
saving actually happens.
"""
import os

import valkey.asyncio as valkey
from betterdb_semantic_cache import SemanticCache, SemanticCacheOptions

from app.rag import get_embedding_fn

VALKEY_HOST = os.getenv("VALKEY_HOST", "localhost")
VALKEY_PORT = int(os.getenv("VALKEY_PORT", "6379"))

CACHE_ENABLED = os.getenv("SEMANTIC_CACHE_ENABLED", "true").lower() == "true"
CACHE_THRESHOLD = float(os.getenv("SEMANTIC_CACHE_THRESHOLD", "0.12"))
CACHE_TTL = int(os.getenv("SEMANTIC_CACHE_TTL", "86400"))  # 24h

SHARED_CACHE_ACTIONS = {"quiz", "flashcards", "explain", "resume"}

_valkey_client = None
_caches: dict[str, SemanticCache] = {}


def _get_valkey_client():
    global _valkey_client
    if _valkey_client is None:
        _valkey_client = valkey.Valkey(host=VALKEY_HOST, port=VALKEY_PORT)
    return _valkey_client


async def _embed_fn(text: str) -> list:
    # Réutilise le modèle multilingue déjà chargé pour l'indexation RAG —
    # même espace vectoriel, pas de second modèle en mémoire.
    return get_embedding_fn()([text])[0]


def _namespace(action: str, user_id: str) -> str:
    return action if action in SHARED_CACHE_ACTIONS else f"{action}_{user_id}"


async def _get_cache(namespace: str) -> SemanticCache:
    if namespace not in _caches:
        cache = SemanticCache(SemanticCacheOptions(
            name=f"paperbrain_{namespace}",
            client=_get_valkey_client(),
            embed_fn=_embed_fn,
            default_threshold=CACHE_THRESHOLD,
            default_ttl=CACHE_TTL,
        ))
        await cache.initialize()
        _caches[namespace] = cache
    return _caches[namespace]


async def get_cached(action: str, prompt: str, user_id: str = "anonymous") -> str | None:
    if not CACHE_ENABLED or not prompt:
        return None
    try:
        cache = await _get_cache(_namespace(action, user_id))
        result = await cache.check(prompt)
        return result.response if result.hit else None
    except Exception:
        # Le cache est une optimisation, jamais une dépendance dure — si
        # Valkey/BetterDB est indisponible, on retombe sur un appel LLM normal.
        return None


async def set_cached(action: str, prompt: str, response: str, user_id: str = "anonymous") -> None:
    if not CACHE_ENABLED or not prompt or not response:
        return
    try:
        cache = await _get_cache(_namespace(action, user_id))
        await cache.store(prompt, response)
    except Exception:
        pass
