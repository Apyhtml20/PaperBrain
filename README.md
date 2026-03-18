# 🧠 PaperBrain — Your Intelligent Study Assistant

<p align="center">
  <img src="assets/logo.png" alt="PaperBrain Logo" width="200"/>
</p>

<p align="center">
  <a href="https://huggingface.co/spaces/ApyHtml20/PaperBrain">
    <img src="https://img.shields.io/badge/🤗%20Hugging%20Face-Space-orange" />
  </a>
  <a href="https://github.com/ApyHtml20/PaperBrain">
    <img src="https://img.shields.io/badge/GitHub-Repository-black" />
  </a>
  <img src="https://img.shields.io/badge/FastAPI-0.100+-green" />
  <img src="https://img.shields.io/badge/React-18+-blue" />
  <img src="https://img.shields.io/badge/n8n-local-purple" />
</p>

> AI-powered learning platform with RAG, Quiz, Flashcards, Explain, Resume — and local n8n AI Agent automation.

---

## 🌐 Spacy Demo Live :

🔗 **Hugging Face Space:** [https://huggingface.co/spaces/ApyHTML19/PaperBrainAI]

---

## ✨ Features

| Feature | Description |
|---|---|
| 💬 **General Chat** | AI-powered study assistant (Qwen 2.5-72B) |
| 📄 **RAG Mode** | Ask questions based on your uploaded documents |
| 🧪 **Quiz** | Auto-generated MCQ quizzes on any topic |
| 🃏 **Flashcards** | Smart flashcards for memorization |
| 💡 **Explain** | Concept explanations at beginner / intermediate / advanced level |
| 📝 **Resume** | Auto-summarize any text or document |
| 📁 **Document Manager** | Upload PDF, TXT, DOCX — indexed per user |
| 👤 **Auth** | JWT-based register/login with user isolation |
| 📊 **Profile & Stats** | Quiz history, streaks, progression tracking |
| 🔄 **n8n AI Agent** | Local AI Agent with Ollama llama3.1 + 5 tools |

---

## 🏗️ Architecture

```
PaperBrain/
├── backend/                  # FastAPI Python backend
│   ├── app/
│   │   ├── auth/
│   │   │   ├── jwt_handler.py     # JWT token creation/decoding
│   │   │   └── middleware.py      # get_current_user dependency
│   │   ├── db/
│   │   │   ├── database.py        # SQLite + SQLAlchemy setup
│   │   │   ├── models.py          # User, QuizResult, StudySession models
│   │   │   └── crud.py            # DB operations
│   │   ├── tools/                 # AI tool modules
│   │   ├── agent.py               # Main AI dispatcher
│   │   ├── ingest.py              # Document ingestion + chunking
│   │   ├── rag.py                 # ChromaDB vector store
│   │   ├── router_service.py      # All API routes
│   │   ├── schemas.py             # Pydantic request models
│   │   └── main.py                # FastAPI app entry point
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 # React frontend
│   └── src/
│       └── pages/
│           ├── Chat.jsx
│           ├── Quiz.jsx
│           ├── Flashcards.jsx
│           ├── Documents.jsx
│           └── Profile.jsx
├── n8n/                      # Local n8n AI Agent workflows
│   └── workflows/
│       └── PaperBrain.json
└── docs/
    ├── logo.png
    └── n8n-workflow.png
```

---

## 🔄 n8n AI Agent (Local)

<p align="center">
  <img src="assets/n8n.png" alt="n8n PaperBrain Workflow" width="100%"/>
</p>

PaperBrain includes a **local n8n AI Agent** powered by **Ollama llama3.1** that orchestrates all learning tools automatically.

### Workflow Architecture

```
[Input Postman / Frontend]
        ↓
  [AI Agent For RAG]  ←→  [Ollama - llama3.1]
        ↓
  ┌─────┴──────────────────────────────┐
  │                                    │
[Flashcards Tool]  [Explain Tool]  [RAG Tool]  [Resume Tool]  [Quiz Tool]
        ↓
[Output Frontend]
```

### Tools disponibles dans l'agent

| Tool | Description |
|---|---|
| 🃏 **Flashcards Tool** | Generate flashcards on any topic |
| 💡 **Explain Tool** | Explain a concept at any level |
| 📄 **RAG Tool** | Search course documents for answers |
| 📝 **Resume Tool** | Summarize topics automatically |
| 🧪 **Quiz Tool** | Generate MCQ quiz questions |

### Setup n8n local

```bash
# Install n8n
npm install -g n8n

# Start n8n
n8n start
# → Access at http://localhost:5678

# Install Ollama
# https://ollama.com/download

# Pull llama3.1
ollama pull llama3.1
```

### Import the workflow

1. Open n8n at `http://localhost:5678`
2. Go to **Workflows → Import**
3. Import `n8n/workflows/PaperBrain.json`
4. Configure the **Ollama** node with your local URL: `http://localhost:11434`
5. **Publish** the workflow

---

## 🚀 Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — REST API
- [SQLite](https://www.sqlite.org/) + [SQLAlchemy](https://www.sqlalchemy.org/) — Database
- [ChromaDB](https://www.trychroma.com/) — Vector store for RAG
- [HuggingFace InferenceClient](https://huggingface.co/docs/huggingface_hub) — Cloud AI (Qwen2.5-72B)
- [python-jose](https://python-jose.readthedocs.io/) — JWT authentication
- [pdfplumber](https://github.com/jsvine/pdfplumber) + [python-docx](https://python-docx.readthedocs.io/) — Document parsing

**Frontend**
- [React 18](https://reactjs.org/) — UI framework
- [Vite](https://vitejs.dev/) — Build tool

**Local AI Automation**
- [n8n](https://n8n.io/) — AI Agent workflow automation
- [Ollama](https://ollama.com/) — Local LLM runtime
- [llama3.1](https://ollama.com/library/llama3.1) — Local AI model

**Deployment**
- [Hugging Face Spaces](https://huggingface.co/spaces) — Docker deployment

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Ollama (for n8n local AI)

### 1. Clone the repo

```bash
git clone https://github.com/ApyHtml20/PaperBrain.git
cd PaperBrain
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
```

Create `.env`:
```env
HF_TOKEN=your_huggingface_token
HF_MODEL=Qwen/Qwen2.5-72B-Instruct
SECRET_KEY=your_secret_key_here
```

```bash
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. n8n + Ollama

```bash
ollama pull llama3.1
n8n start
```

---

## 🔌 API Endpoints

### Auth
| Method | Route | Description |
|---|---|---|
| POST | `/api/auth/register` | Create new account |
| POST | `/api/auth/login` | Login and get JWT token |

### Learning (🔒 Auth required)
| Method | Route | Description |
|---|---|---|
| POST | `/api/chat` | General AI chat |
| POST | `/api/rag-qa` | Chat with your documents |
| POST | `/api/quiz` | Generate MCQ quiz |
| POST | `/api/flashcards` | Generate flashcards |
| POST | `/api/explain` | Explain a concept |
| POST | `/api/resume` | Summarize text |

### Documents (🔒 Auth required)
| Method | Route | Description |
|---|---|---|
| GET | `/api/documents` | List your documents |
| POST | `/api/upload` | Upload PDF/TXT/DOCX |
| DELETE | `/api/documents/{filename}` | Delete a document |

---

## 🐳 Docker / HF Spaces

```dockerfile
FROM python:3.11-slim
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

**HF Spaces secrets** (Settings → Variables and secrets):
```
HF_TOKEN=...
HF_MODEL=Qwen/Qwen2.5-72B-Instruct
SECRET_KEY=...
```

---

## 🔐 Security

- Passwords hashed with SHA-256 + random salt
- JWT tokens expire after 24 hours
- All routes protected by auth middleware
- Documents isolated by `user_id` in ChromaDB
- Files stored in `documents/{user_id}/`

---
