import asyncio
import json
import re
import os

from app.llm import complete as _llm_complete
from app.cache import get_cached, set_cached

conversation_store: dict[str, list] = {}

# Champ de la requête qui sert de clé au cache sémantique, par action.
# "chat" est volontairement absent : sa réponse dépend aussi de l'historique
# de conversation (voir _get_history ci-dessous), que la seule "query" ne
# capture pas — la mettre en cache renverrait la réponse d'une conversation
# précédente sans rapport avec la question actuelle.
CACHE_KEY_FIELD = {
    "rag-qa":     "query",
    "quiz":       "topic",
    "flashcards": "topic",
    "explain":    "concept",
    "resume":     "text",
}


# ── Core call — route via LiteLLM (cascade Groq → HuggingFace → OpenAI) ────────
def _call_llm(
    system: str,
    user: str,
    max_tokens: int = 1024,
    temperature: float = 0.4,
) -> str:
    try:
        return _llm_complete(system, user, max_tokens=max_tokens, temperature=temperature)
    except Exception as e:
        raise Exception(f"LLM error: {str(e)}")


# ── JSON helpers ──────────────────────────────────────────────────────────────
def _fix_json(s: str) -> str:
    s = re.sub(r',\s*([}\]])', r'\1', s)
    s = re.sub(r'[\x00-\x1f\x7f]', ' ', s)
    return s


def _extract_json_array(raw: str) -> list:
    cleaned = re.sub(r'```(?:json)?\s*', '', raw)
    cleaned = re.sub(r'```', '', cleaned).strip()

    try:
        result = json.loads(cleaned)
        if isinstance(result, list):
            return result
    except Exception:
        pass

    start = cleaned.find('[')
    if start != -1:
        depth = 0
        for i, ch in enumerate(cleaned[start:], start):
            if ch == '[':
                depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    candidate = cleaned[start:i + 1]
                    for attempt in (candidate, _fix_json(candidate)):
                        try:
                            result = json.loads(attempt)
                            if isinstance(result, list):
                                return result
                        except Exception:
                            pass
                    break

    match = re.search(r'\[[\s\S]*\]', cleaned)
    if match:
        for attempt in (match.group(), _fix_json(match.group())):
            try:
                return json.loads(attempt)
            except Exception:
                pass

    return []


# ── Conversation history ──────────────────────────────────────────────────────
def _get_history(user_id: str) -> list:
    return conversation_store.get(user_id, [])


def _save_history(user_id: str, user_msg: str, ai_msg: str) -> None:
    if user_id not in conversation_store:
        conversation_store[user_id] = []
    conversation_store[user_id].append({"user": user_msg, "assistant": ai_msg})
    conversation_store[user_id] = conversation_store[user_id][-5:]


# ── Async entry point ─────────────────────────────────────────────────────────
async def run_agent(action: str, data: dict) -> dict:
    user_id = data.get("user_id", "anonymous")
    field = CACHE_KEY_FIELD.get(action)
    prompt = str(data.get(field, "")).strip() if field else ""

    if prompt:
        cached = await get_cached(action, prompt, user_id)
        if cached is not None:
            try:
                result = json.loads(cached)
                result["cached"] = True
                return result
            except Exception:
                pass  # entrée corrompue: on ignore et on régénère normalement

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _run_sync, action, data)

    if prompt and isinstance(result, dict) and not result.get("error"):
        await set_cached(action, prompt, json.dumps(result), user_id)

    return result


def _run_sync(action: str, data: dict) -> dict:
    dispatch = {
        "chat":       _chat,
        "quiz":       _quiz,
        "flashcards": _flashcards,
        "explain":    _explain,
        "resume":     _resume,
        "rag-qa":     _rag_qa,
    }
    handler = dispatch.get(action)
    if handler:
        return handler(data)
    return {"answer": f"Unknown action: {action}", "action": action}


# ── Action handlers ───────────────────────────────────────────────────────────

def _chat(data: dict) -> dict:
    query   = data.get("query", "")
    user_id = data.get("user_id", "anonymous")
    history = _get_history(user_id)

    history_text = ""
    if history:
        history_text = "Conversation récente :\n" + "\n".join(
            f"Utilisateur: {h['user']}\nAssistant: {h['assistant']}"
            for h in history
        ) + "\n\n"

    system = (
        "Tu es PaperBrain AI, un assistant pédagogique pour les étudiants. "
        "Aide les étudiants à comprendre leurs cours, préparer leurs examens et apprendre efficacement. "
        "Réponds toujours dans la même langue que la question. "
        "Sois clair, structuré et pédagogique."
    )
    user = f"{history_text}Utilisateur : {query}"

    answer = _call_llm(system, user, max_tokens=1024, temperature=0.5)
    _save_history(user_id, query, answer)
    return {"answer": answer, "user_id": user_id}


def _quiz(data: dict) -> dict:
    topic         = data.get("topic", "")
    num_questions = data.get("num_questions", 5)
    difficulty    = data.get("difficulty", "medium")

    difficulty_map = {
        "easy":   "simples et directes, pour débutants",
        "medium": "de difficulté intermédiaire",
        "hard":   "difficiles et approfondies, pour experts",
    }
    level_desc = difficulty_map.get(difficulty, "de difficulté intermédiaire")

    system = (
        "Tu es un générateur de quiz pédagogique. "
        "Tu réponds UNIQUEMENT avec un tableau JSON valide, sans texte avant ni après, sans balises markdown."
    )
    user = (
        f"Génère {num_questions} questions QCM ({level_desc}) sur : \"{topic}\".\n\n"
        "Chaque objet JSON doit contenir : question, options (tableau de 4 chaînes "
        "\"A) ...\", \"B) ...\", \"C) ...\", \"D) ...\"), correct_answer (A/B/C/D), explanation.\n\n"
        "Réponds UNIQUEMENT avec le tableau JSON."
    )

    raw = _call_llm(system, user, max_tokens=1500, temperature=0.3)
    questions = _extract_json_array(raw)

    if questions:
        clean = [
            {
                "question":       str(q.get("question", "")),
                "options":        list(q.get("options", [])),
                "correct_answer": str(q.get("correct_answer", "A")),
                "explanation":    str(q.get("explanation", "")),
            }
            for q in questions
            if isinstance(q, dict) and q.get("question") and q.get("options")
        ]
        if clean:
            return {"questions": clean, "topic": topic, "difficulty": difficulty}

    return {"questions": [], "topic": topic, "error": "JSON invalide.", "raw_preview": raw[:300]}


def _flashcards(data: dict) -> dict:
    topic     = data.get("topic", "")
    num_cards = data.get("num_cards", 8)

    system = (
        "Tu es un générateur de flashcards pédagogiques. "
        "Tu réponds UNIQUEMENT avec un tableau JSON valide, sans texte avant ni après, sans balises markdown."
    )
    user = (
        f"Génère {num_cards} flashcards sur : \"{topic}\".\n\n"
        "Chaque objet JSON doit contenir : front (question/terme) et back (réponse/définition).\n\n"
        "Réponds UNIQUEMENT avec le tableau JSON."
    )

    raw   = _call_llm(system, user, max_tokens=1024, temperature=0.3)
    cards = _extract_json_array(raw)

    if cards:
        clean = [
            {"front": str(c.get("front", "")), "back": str(c.get("back", ""))}
            for c in cards
            if isinstance(c, dict) and c.get("front") and c.get("back")
        ]
        if clean:
            return {"flashcards": clean, "topic": topic}

    return {"flashcards": [], "topic": topic, "error": "Impossible de parser les flashcards."}


def _explain(data: dict) -> dict:
    concept = data.get("concept", "")
    level   = data.get("level", "intermediate")

    level_map = {
        "beginner":     "de manière très simple, avec des analogies du quotidien, pour un lycéen",
        "intermediate": "clairement avec les concepts essentiels, pour un étudiant universitaire",
        "advanced":     "de manière approfondie et technique, pour un expert du domaine",
    }
    level_desc = level_map.get(level, level_map["intermediate"])

    system = (
        "Tu es un professeur pédagogue expert. "
        "Réponds dans la même langue que le concept demandé."
    )
    user = (
        f"Explique le concept suivant {level_desc}.\n\n"
        "Structure ta réponse avec :\n"
        "1. Définition courte et claire\n"
        "2. Points clés à retenir\n"
        "3. Exemple concret\n"
        "4. Applications pratiques\n\n"
        f"Concept : {concept}"
    )

    explanation = _call_llm(system, user, max_tokens=1024, temperature=0.5)
    return {"explanation": explanation, "concept": concept, "level": level}


def _resume(data: dict) -> dict:
    text = data.get("text", "")
    if not text:
        return {"summary": "Aucun texte fourni."}

    system = (
        "Tu es un assistant pédagogique expert en synthèse de documents. "
        "Réponds dans la même langue que le texte fourni."
    )
    user = (
        "Résume le texte suivant de façon claire et structurée.\n"
        "Utilise des titres et des points clés.\n\n"
        f"Texte :\n{text[:3000]}"
    )

    summary = _call_llm(system, user, max_tokens=1024, temperature=0.4)
    return {"summary": summary}


RAG_DISTANCE_THRESHOLD = float(os.getenv("RAG_DISTANCE_THRESHOLD", "0.8"))
RAG_CONTEXT_BUDGET = 3000


def _build_context(relevant: list) -> str:
    """Ajoute des chunks entiers jusqu'au budget, sans jamais couper un chunk
    au milieu (contrairement à un simple context[:N])."""
    parts = []
    budget = RAG_CONTEXT_BUDGET
    for doc, _ in relevant:
        if budget <= 0:
            break
        if len(doc) > budget and parts:
            break
        parts.append(doc)
        budget -= len(doc)
    return "\n\n---\n\n".join(parts)


def _rag_qa(data: dict) -> dict:
    query   = data.get("query", "")
    user_id = data.get("user_id", "anonymous")

    try:
        from app.rag import query_documents

        results   = query_documents(query, user_id=user_id, n_results=4)
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas",  [[]])[0]
        distances = results.get("distances",  [[]])[0]

        relevant = [
            (doc, meta)
            for doc, meta, dist in zip(documents, metadatas, distances)
            if dist < RAG_DISTANCE_THRESHOLD
        ]

        if not relevant:
            return {
                "answer":  "Aucune information pertinente trouvée dans vos documents.",
                "sources": [],
            }

        context = _build_context(relevant)
        sources = sorted(set(meta.get("source", "inconnu") for _, meta in relevant))

        system = (
            "Tu es un assistant pédagogique RAG. "
            "Réponds à la question en te basant UNIQUEMENT sur le contexte fourni. "
            "Si la réponse n'est pas dans le contexte, dis-le clairement. "
            "Réponds dans la même langue que la question."
        )
        user = f"Contexte :\n{context}\n\nQuestion : {query}"

        answer = _call_llm(system, user, max_tokens=1024, temperature=0.4)
        return {"answer": answer, "sources": sources}

    except Exception as e:
        return {"answer": f"Erreur RAG : {str(e)}", "sources": [], "error": str(e)}