import hashlib
import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.models import User, QuizResult, StudySession


# ── Password
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(plain: str, hashed: str) -> bool:
    try:
        salt, hash_val = hashed.split(":")
        return hashlib.sha256((plain + salt).encode()).hexdigest() == hash_val
    except:
        return False


# ── User CRUD
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, username: str, email: str, password: str):
    user = User(
        username=username,
        email=email,
        password=hash_password(password),
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_streak(db: Session, user: User):
    now = datetime.utcnow()
    if user.last_login:
        diff = (now.date() - user.last_login.date()).days
        if diff == 1:
            user.streak_days += 1
        elif diff > 1:
            user.streak_days = 1
    else:
        user.streak_days = 1
    user.last_login = now
    db.commit()


# ── Quiz Results
def save_quiz_result(db: Session, user_id: int, req):
    result = QuizResult(
        user_id=user_id,
        topic=req.topic,
        score=req.score,
        total_questions=req.total_questions,
        correct_answers=req.correct_answers,
        difficulty=req.difficulty,
        duration_sec=req.duration_sec
    )
    db.add(result)

    # Mise à jour du niveau utilisateur
    user = get_user_by_id(db, user_id)
    if user:
        results = db.query(QuizResult).filter(QuizResult.user_id == user_id).all()
        if len(results) > 0:
            avg = sum(r.score for r in results) / len(results)
            if avg >= 80:
                user.niveau = "expert"
            elif avg >= 60:
                user.niveau = "intermédiaire"
            else:
                user.niveau = "débutant"

    db.commit()
    db.refresh(result)
    return result


# ── Profile
def get_student_profile(db: Session, user_id: int) -> dict:
    user = get_user_by_id(db, user_id)
    if not user:
        return {}

    quiz_results = db.query(QuizResult).filter(
        QuizResult.user_id == user_id
    ).order_by(QuizResult.created_at.desc()).all()

    sessions = db.query(StudySession).filter(
        StudySession.user_id == user_id
    ).all()

    scores = [r.score for r in quiz_results]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0
    best_score = max(scores) if scores else 0

    # Top matières
    subjects = {}
    for s in sessions:
        subjects[s.subject] = subjects.get(s.subject, 0) + 1
    top_subjects = sorted(
        [{"subject": k, "count": v} for k, v in subjects.items()],
        key=lambda x: x["count"], reverse=True
    )[:5]

    recent_quiz = [
        {
            "topic": r.topic,
            "score": r.score,
            "date": r.created_at.strftime("%d/%m/%Y"),
            "difficulty": r.difficulty
        }
        for r in quiz_results[:10]
    ]

    return {
        "user": {
            "username": user.username,
            "email": user.email,
            "niveau": user.niveau,
            "streak_days": user.streak_days,
            "member_since": user.created_at.strftime("%d/%m/%Y") if user.created_at else "N/A"
        },
        "stats": {
            "total_sessions": len(sessions),
            "total_quiz": len(quiz_results),
            "average_score": avg_score,
            "best_score": best_score,
            "top_subjects": top_subjects
        },
        "recent_quiz": recent_quiz
    }


def get_progress(db: Session, user_id: int) -> dict:
    results = db.query(QuizResult).filter(
        QuizResult.user_id == user_id
    ).order_by(QuizResult.created_at.asc()).all()

    return {
        "progression": [
            {"date": r.created_at.strftime("%d/%m"), "score": r.score, "topic": r.topic}
            for r in results
        ]
    }