import json
import re
import os
from huggingface_hub import InferenceClient

HF_TOKEN   = os.getenv("HF_TOKEN", "")
MODEL_NAME = os.getenv("HF_MODEL", "Qwen/Qwen2.5-72B-Instruct")

_client: InferenceClient | None = None


def _get_client() -> InferenceClient:
    global _client
    if _client is None:
        _client = InferenceClient(model=MODEL_NAME, token=HF_TOKEN or None)
    return _client


def _call_hf(prompt: str, max_tokens: int = 256, temperature: float = 0.1) -> str:
    client = _get_client()
    response = client.text_generation(
        prompt,
        max_new_tokens=max_tokens,
        temperature=temperature,
        do_sample=False,        # deterministic for evaluation
        return_full_text=False,
    )
    return response.strip()


def _extract_score(raw: str) -> float:
    try:
        cleaned = re.sub(r'```(?:json)?\s*|```', '', raw).strip()
        data = json.loads(cleaned)
        if isinstance(data, dict):
            for key in ["score", "value", "result", "rating"]:
                if key in data:
                    val = float(data[key])
                    return max(0.0, min(1.0, val if val <= 1.0 else val / 10.0))
    except Exception:
        pass

    matches = re.findall(r'\b(0\.\d+|1\.0|[0-9](?:\.[0-9]+)?)\b', raw)
    for m in matches:
        val = float(m)
        if 0.0 <= val <= 1.0:
            return val
        if 1.0 < val <= 10.0:
            return val / 10.0

    raw_lower = raw.lower()
    if any(w in raw_lower for w in ["excellent", "perfect", "fully", "completely"]):
        return 0.9
    if any(w in raw_lower for w in ["good", "mostly", "largely"]):
        return 0.7
    if any(w in raw_lower for w in ["partial", "somewhat", "moderate"]):
        return 0.5
    if any(w in raw_lower for w in ["poor", "barely", "little"]):
        return 0.3
    if any(w in raw_lower for w in ["no", "none", "not", "fail"]):
        return 0.1

    return 0.5


def _parse_result(raw: str) -> tuple[float, str]:
    score  = _extract_score(raw)
    reason = "No reason provided."
    try:
        cleaned = re.sub(r'```(?:json)?\s*|```', '', raw).strip()
        data    = json.loads(cleaned)
        reason  = data.get("reason", reason)
    except Exception:
        m = re.search(r'"reason"\s*:\s*"([^"]+)"', raw)
        if m:
            reason = m.group(1)
    return round(score, 2), reason


# ── Evaluation functions ──────────────────────────────────────────────────────

def evaluate_faithfulness(question: str, context: str, answer: str) -> dict:
    prompt = f"""<s>[INST] Tu es un évaluateur RAG expert. Évalue la FIDÉLITÉ de la réponse.
La fidélité mesure si la réponse est entièrement fondée sur le contexte fourni.

Question : {question}
Contexte : {context[:2000]}
Réponse : {answer[:1000]}

Note de 0.0 à 1.0 (1.0 = entièrement fondée sur le contexte, 0.0 = totalement hallucinée).
Réponds UNIQUEMENT avec : {{"score": <float 0.0-1.0>, "reason": "<une phrase>"}} [/INST]
"""
    raw   = _call_hf(prompt)
    score, reason = _parse_result(raw)
    return {"score": score, "reason": reason, "raw": raw[:200]}


def evaluate_answer_relevancy(question: str, answer: str) -> dict:
    prompt = f"""<s>[INST] Tu es un évaluateur RAG expert. Évalue la PERTINENCE DE LA RÉPONSE.
La pertinence mesure si la réponse répond directement à la question posée.

Question : {question}
Réponse : {answer[:1000]}

Note de 0.0 à 1.0 (1.0 = répond parfaitement, 0.0 = hors sujet).
Réponds UNIQUEMENT avec : {{"score": <float 0.0-1.0>, "reason": "<une phrase>"}} [/INST]
"""
    raw   = _call_hf(prompt)
    score, reason = _parse_result(raw)
    return {"score": score, "reason": reason, "raw": raw[:200]}


def evaluate_context_recall(question: str, context: str) -> dict:
    prompt = f"""<s>[INST] Tu es un évaluateur RAG expert. Évalue le RAPPEL DU CONTEXTE.
Mesure si le contexte récupéré contient les informations nécessaires pour répondre à la question.

Question : {question}
Contexte récupéré : {context[:2000]}

Note de 0.0 à 1.0 (1.0 = contexte idéal, 0.0 = contexte inutile).
Réponds UNIQUEMENT avec : {{"score": <float 0.0-1.0>, "reason": "<une phrase>"}} [/INST]
"""
    raw   = _call_hf(prompt)
    score, reason = _parse_result(raw)
    return {"score": score, "reason": reason, "raw": raw[:200]}


def evaluate_hallucination(question: str, context: str, answer: str) -> dict:
    prompt = f"""<s>[INST] Tu es un évaluateur RAG expert. Détecte les HALLUCINATIONS dans la réponse.
Une hallucination = information présente dans la réponse mais ABSENTE du contexte et non-connaissance générale.

Question : {question}
Contexte : {context[:2000]}
Réponse : {answer[:1000]}

Note de 0.0 à 1.0 (1.0 = aucune hallucination, 0.0 = totalement hallucinée).
Réponds UNIQUEMENT avec : {{"score": <float 0.0-1.0>, "reason": "<une phrase>"}} [/INST]
"""
    raw   = _call_hf(prompt)
    score, reason = _parse_result(raw)
    return {"score": score, "reason": reason, "raw": raw[:200]}


def evaluate_rag_response(question: str, context: str, answer: str) -> dict:
    print(f"[RAG EVAL] Démarrage pour : {question[:80]}")

    results: dict[str, dict] = {}

    for key, fn, args in [
        ("faithfulness",      evaluate_faithfulness,     (question, context, answer)),
        ("answer_relevancy",  evaluate_answer_relevancy, (question, answer)),
        ("context_recall",    evaluate_context_recall,   (question, context)),
        ("hallucination",     evaluate_hallucination,    (question, context, answer)),
    ]:
        try:
            results[key] = fn(*args)
            print(f"[RAG EVAL] {key}: {results[key]['score']}")
        except Exception as e:
            results[key] = {"score": 0.0, "reason": str(e), "error": True}

    weights = {
        "faithfulness":     0.35,
        "answer_relevancy": 0.30,
        "context_recall":   0.20,
        "hallucination":    0.15,
    }
    overall = round(sum(
        results[k]["score"] * w
        for k, w in weights.items()
        if not results[k].get("error")
    ), 2)

    grade = "A" if overall >= 0.85 else "B" if overall >= 0.70 else "C" if overall >= 0.55 else "D" if overall >= 0.40 else "F"
    print(f"[RAG EVAL] Overall: {overall} ({grade})")

    return {
        "question":      question,
        "overall_score": overall,
        "grade":         grade,
        "metrics":       results,
        "summary":       _generate_summary(overall, results),
    }


def _generate_summary(overall: float, results: dict) -> str:
    label_map = {
        "faithfulness":     "Fidélité",
        "answer_relevancy": "Pertinence",
        "context_recall":   "Rappel contexte",
        "hallucination":    "Hallucination",
    }
    weak   = [label_map[k] for k, v in results.items() if v["score"] < 0.5  and not v.get("error")]
    strong = [label_map[k] for k, v in results.items() if v["score"] >= 0.8 and not v.get("error")]

    if overall >= 0.85:
        verdict = "Excellente réponse RAG."
    elif overall >= 0.70:
        verdict = "Bonne réponse avec quelques défauts mineurs."
    elif overall >= 0.50:
        verdict = "Réponse acceptable — qualité du contexte à améliorer."
    else:
        verdict = "Réponse insuffisante — uploadez des documents plus pertinents."

    parts = []
    if strong:
        parts.append(f"Points forts : {', '.join(strong)}.")
    if weak:
        parts.append(f"À améliorer : {', '.join(weak)}.")

    return verdict + (" " + " ".join(parts) if parts else "")