from pydantic import BaseModel 
from typing import Optional 
 
class RegisterRequest(BaseModel): 
    username: str 
    email: str 
    password: str 
 
class LoginRequest(BaseModel): 
    email: str 
    password: str 
 
class ChatRequest(BaseModel): 
    query: str 
    user_id: str = "anonymous" 
 
class QuizRequest(BaseModel): 
    topic: str 
    num_questions: int = 5 
    difficulty: str = "medium" 
 
class FlashcardRequest(BaseModel): 
    topic: str 
    num_cards: int = 8 
 
class ExplainRequest(BaseModel): 
    concept: str 
    level: str = "intermediate" 
 
class ResumeRequest(BaseModel): 
    text: str 
 
class RAGRequest(BaseModel): 
    query: str 
    user_id: str = "anonymous" 
 
class QuizResultRequest(BaseModel): 
    topic: str 
    score: int 
    total_questions: int 
    correct_answers: int 
    difficulty: str = "medium" 
    duration_sec: int = 0 
