from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id           = Column(Integer, primary_key=True, index=True)
    username     = Column(String, unique=True, index=True)
    email        = Column(String, unique=True, index=True)
    password     = Column(String)
    niveau       = Column(String, default="débutant")
    streak_days  = Column(Integer, default=0)
    last_login   = Column(DateTime, default=datetime.utcnow)
    created_at   = Column(DateTime, default=datetime.utcnow)
    is_active    = Column(Boolean, default=True)

    quiz_results  = relationship("QuizResult", back_populates="user")
    study_sessions = relationship("StudySession", back_populates="user")


class QuizResult(Base):
    __tablename__ = "quiz_results"

    id               = Column(Integer, primary_key=True, index=True)
    user_id          = Column(Integer, ForeignKey("users.id"))
    topic            = Column(String)
    score            = Column(Float)
    total_questions  = Column(Integer)
    correct_answers  = Column(Integer)
    difficulty       = Column(String, default="medium")
    duration_sec     = Column(Integer, default=0)
    created_at       = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="quiz_results")


class StudySession(Base):
    __tablename__ = "study_sessions"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"))
    action     = Column(String)  # chat, quiz, flashcards, explain, rag-qa
    subject    = Column(String, default="general")
    duration   = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="study_sessions")


class FlashcardProgress(Base):
    __tablename__ = "flashcard_progress"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"))
    topic      = Column(String)
    known      = Column(Integer, default=0)
    unknown    = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)