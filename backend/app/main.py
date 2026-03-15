from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.router_service import router
from app.db.database import create_tables
import os

app = FastAPI(
    title="PaperBrain API BY HICHAM",
    description="API d'assistance à l'apprentissage avec auth et profils",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    create_tables()
    print("Tables créées avec succès")

app.include_router(router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok"}

# Servir le frontend React — DOIT être en dernier
if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
else:
    @app.get("/")
    def root():
        return {"message": "SmartStudyAI v2.0 running"}