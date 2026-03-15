import json
import re
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


def _call_hf(system: str, user: str, max_tokens: int = 1500, temperature: float = 0.3) -> str:
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


def _extract_json_array(raw: str) -> list:
    cleaned = re.sub(r'```(?:json)?\s*|```', '', raw).strip()
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
            if ch == '[': depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    candidate = re.sub(r',\s*([}\]])', r'\1', cleaned[start:i+1])
                    try:
                        return json.loads(candidate)
                    except Exception:
                        pass
                    break
    return []


def generate_quiz(topic: str, num_questions: int = 5, difficulty: str = "medium") -> list[dict]:
    difficulty_map = {
        "easy":   "simples et directes, pour débutants",
        "medium": "de difficulté intermédiaire",
        "hard":   "difficiles et approfondies, pour experts",
    }
    level_desc = difficulty_map.get(difficulty, "de difficulté intermédiaire")

    system = (
        "Tu es un générateur de quiz pédagogique. "
        "Tu réponds UNIQUEMENT avec un tableau JSON valide, sans texte avant ni après."
    )
    user = (
        f"Génère {num_questions} questions QCM ({level_desc}) sur : \"{topic}\".\n"
        "Chaque objet : question, options (4 chaînes A/B/C/D), correct_answer (A/B/C/D), explanation.\n"
        "Réponds UNIQUEMENT avec le tableau JSON."
    )

    raw       = _call_hf(system, user)
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
            return clean

    return [{"question": f"Question sur {topic}", "options": ["A) -", "B) -", "C) -", "D) -"], "correct_answer": "A", "explanation": "Erreur de génération."}]