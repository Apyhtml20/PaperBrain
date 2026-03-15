from pydantic import BaseModel
from typing import Optional

# ── Auth
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

# ── AI Requests
class ChatRequest(BaseModel):
    query: str
    user_id: Optional[str] = "anonymous"

class QuizRequest(BaseModel):
    topic: str
    num_questions: Optional[int] = 5
    difficulty: Optional[str] = "medium"

class FlashcardRequest(BaseModel):
    topic: str
    num_cards: Optional[int] = 8

class ExplainRequest(BaseModel):
    concept: str
    level: Optional[str] = "intermediate"

class ResumeRequest(BaseModel):
    text: str

class RAGRequest(BaseModel):
    query: str
    user_id: Optional[str] = "anonymous"

# ── Quiz Result
class QuizResultRequest(BaseModel):
    topic: str
    score: int
    total_questions: int
    correct_answers: int
    difficulty: Optional[str] = "medium"
    duration_sec: Optional[int] = 0
class RAGEvalRequest(BaseModel):
    question: str
    context: str
    answer: str