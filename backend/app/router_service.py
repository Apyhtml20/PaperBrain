import os
import shutil
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import crud
from app.auth.jwt_handler import create_token
from app.auth.middleware import get_current_user
from app.schemas import (
    RegisterRequest, LoginRequest, ChatRequest, QuizRequest,
    FlashcardRequest, ExplainRequest, ResumeRequest, RAGRequest, QuizResultRequest
)

# ── Router (TOUJOURS en premier)
router = APIRouter()
UPLOAD_DIR = "./documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ══════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════

@router.post("/auth/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, req.email):
        raise HTTPException(400, "Email déjà utilisé")
    if crud.get_user_by_username(db, req.username):
        raise HTTPException(400, "Nom d'utilisateur déjà pris")
    user = crud.create_user(db, req.username, req.email, req.password)
    token = create_token({"sub": str(user.id), "username": user.username})
    return {"access_token": token, "username": user.username, "user_id": user.id}


@router.post("/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, req.email)
    if not user or not crud.verify_password(req.password, user.password):
        raise HTTPException(401, "Email ou mot de passe incorrect")
    crud.update_streak(db, user)
    token = create_token({"sub": str(user.id), "username": user.username})
    return {"access_token": token, "username": user.username, "user_id": user.id}


# ══════════════════════════════════════════════════════════
# PROFILE
# ══════════════════════════════════════════════════════════

@router.get("/profile")
def get_profile(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_student_profile(db, current_user.id)


@router.get("/progress")
def get_progress(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_progress(db, current_user.id)


# ══════════════════════════════════════════════════════════
# QUIZ RESULT
# ══════════════════════════════════════════════════════════

@router.post("/quiz/result")
def save_quiz_result(req: QuizResultRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    result = crud.save_quiz_result(db, current_user.id, req)
    return {"message": "Résultat sauvegardé", "id": result.id}


# ══════════════════════════════════════════════════════════
# UPLOAD & DOCUMENTS
# ══════════════════════════════════════════════════════════

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    subject: str = Form(default="general")
):
    allowed = [".pdf", ".txt", ".docx"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(400, f"Format non supporté. Acceptés: {allowed}")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        from app.ingest import ingest_document
        chunks = ingest_document(file_path, subject)
        return {
            "message": f"Fichier '{file.filename}' ingéré avec succès",
            "chunks": chunks,
            "subject": subject,
            "filename": file.filename
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(500, f"Erreur ingestion: {str(e)}")


@router.get("/documents")
def list_documents():
    try:
        from app.rag import get_collection
        collection = get_collection()
        results = collection.get()
        sources = {}
        for meta in results.get("metadatas", []):
            if not meta:
                continue
            src  = meta.get("source", "inconnu")
            subj = meta.get("subject", "general")
            if src not in sources:
                sources[src] = {"filename": src, "subject": subj, "chunks": 0}
            sources[src]["chunks"] += 1
        return {"documents": list(sources.values()), "total": len(sources)}
    except Exception as e:
        return {"documents": [], "total": 0, "error": str(e)}


@router.delete("/documents/{filename}")
def delete_document(filename: str):
    try:
        from app.rag import get_collection
        collection = get_collection()
        results = collection.get(where={"source": filename})
        ids = results.get("ids", [])
        if ids:
            collection.delete(ids=ids)
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        return {"message": f"'{filename}' supprimé ({len(ids)} chunks)"}
    except Exception as e:
        raise HTTPException(500, str(e))


# ══════════════════════════════════════════════════════════
# AI ENDPOINTS
# ══════════════════════════════════════════════════════════

@router.post("/chat")
async def chat(req: ChatRequest):
    try:
        from app.agent import run_agent
        result = await run_agent("chat", req.dict())
        return result
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/quiz")
async def generate_quiz(req: QuizRequest):
    try:
        from app.agent import run_agent
        result = await run_agent("quiz", req.dict())
        return result
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/flashcards")
async def generate_flashcards(req: FlashcardRequest):
    try:
        from app.agent import run_agent
        result = await run_agent("flashcards", req.dict())
        return result
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/explain")
async def explain(req: ExplainRequest):
    try:
        from app.agent import run_agent
        result = await run_agent("explain", req.dict())
        return result
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/resume")
async def resume(req: ResumeRequest):
    try:
        from app.agent import run_agent
        result = await run_agent("resume", req.dict())
        return result
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/rag-qa")
async def rag_qa_endpoint(req: RAGRequest):
    try:
        from app.agent import run_agent
        result = await run_agent("rag-qa", req.dict())
        return result
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/health")
def health():
    return {"status": "ok", "service": "SmartStudyAI"}