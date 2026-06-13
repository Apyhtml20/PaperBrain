<p align="center">
  <img src="assets/logo.png" alt="PaperBrain Logo" width="160"/>
</p>

<h1 align="center">PaperBrain</h1>
<p align="center"><strong>Your AI-powered study assistant — chat, quiz, explain, summarize, and more.</strong></p>

<p align="center">
  <a href="https://huggingface.co/spaces/ApyHTML19/PaperBrainAI">
    <img src="https://img.shields.io/badge/🤗%20Hugging%20Face-Live%20Demo-orange" />
  </a>
  <a href="https://github.com/ApyHtml20/PaperBrain">
    <img src="https://img.shields.io/badge/GitHub-Repository-black" />
  </a>
  <img src="https://img.shields.io/badge/FastAPI-0.100+-green" />
  <img src="https://img.shields.io/badge/React-18+-blue" />
  <img src="https://img.shields.io/badge/n8n-local%20agent-purple" />
</p>

<p align="center">
  <img src="assets/PaperBrain.png" alt="PaperBrain screenshot" width="100%"/>
</p>

---

## What is PaperBrain?

PaperBrain turns your documents into an interactive study session. Upload a PDF, ask questions about it, generate a quiz, get flashcards, or request a plain-English explanation — all in one place.

It runs on a **FastAPI + React** stack with **Qwen 2.5-72B** via HuggingFace for cloud inference, **ChromaDB** for document retrieval (RAG), and an optional **local n8n AI Agent** powered by Ollama for fully offline automation.

---

## Features

| | Feature | Description |
|---|---|---|
| 💬 | **General Chat** | Study assistant backed by Qwen 2.5-72B |
| 📄 | **RAG Mode** | Ask questions directly about your uploaded documents |
| 🧪 | **Quiz** | Auto-generated multiple-choice quizzes on any topic |
| 🃏 | **Flashcards** | Smart cards for active recall and memorization |
| 💡 | **Explain** | Concept breakdowns at beginner / intermediate / advanced level |
| 📝 | **Summarize** | Auto-summarize any text or uploaded document |
| 📁 | **Document Manager** | Upload PDF, TXT, DOCX — indexed per user with isolation |
| 👤 | **Auth** | JWT-based register/login with per-user data separation |
| 📊 | **Profile & Stats** | Quiz history, streaks, and progression tracking |
| 🔄 | **n8n AI Agent** | Local agent with Ollama (llama3.1 / Qwen 2.5) + 5 tools |

---

## Architecture

```
PaperBrain/
├── backend/                        # FastAPI Python backend
│   ├── app/
│   │   ├── auth/
│   │   │   ├── jwt_handler.py      # JWT token creation/decoding
│   │   │   └── middleware.py       # get_current_user dependency
│   │   ├── db/
│   │   │   ├── database.py         # SQLite + SQLAlchemy setup
│   │   │   ├── models.py           # User, QuizResult, StudySession
│   │   │   └── crud.py             # DB operations
│   │   ├── tools/                  # AI tool modules
│   │   ├── agent.py                # Main AI dispatcher
│   │   ├── ingest.py               # Document ingestion + chunking
│   │   ├── rag.py                  # ChromaDB vector store
│   │   ├── router_service.py       # API routes
│   │   ├── schemas.py              # Pydantic request models
│   │   └── main.py                 # FastAPI app entry point
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                       # React frontend
│   └── src/
│       └── pages/
│           ├── Chat.jsx
│           ├── Quiz.jsx
│           ├── Flashcards.jsx
│           ├── Documents.jsx
│           └── Profile.jsx
├── n8n/                            # Local n8n AI Agent
│   └── workflows/
│       └── PaperBrain.json
└── docs/
    ├── logo.png
    └── n8n-workflow.png
```

---

## Local Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Ollama *(only required for the n8n local agent)*

### 1 — Clone the repository

```bash
git clone https://github.com/ApyHtml20/PaperBrain.git
cd PaperBrain
```

### 2 — Backend

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file:

```env
HF_TOKEN=your_huggingface_token
HF_MODEL=Qwen/Qwen2.5-72B-Instruct
SECRET_KEY=your_secret_key_here
```

Start the server:

```bash
uvicorn app.main:app --reload --port 8000
```

### 3 — Frontend

```bash
cd frontend
npm install
npm run dev
```

### 4 — n8n + Ollama *(optional)*

```bash
# Install and start Ollama, then pull the model
ollama pull llama3.1

# Install and start n8n
npm install -g n8n
n8n start
# → http://localhost:5678
```

Then in n8n:
1. Go to **Workflows → Import**
2. Import `n8n/workflows/PaperBrain.json`
3. Set the Ollama node URL to `http://localhost:11434`
4. Click **Publish**

---

## n8n AI Agent

<p align="center">
  <img src="assets/n8n.png" alt="n8n PaperBrain Workflow" width="100%"/>
</p>

The local n8n agent orchestrates all learning tools automatically using **Ollama llama3.1** — no cloud required.

```
[Postman / Frontend]
        ↓
  [AI Agent (RAG)]  ←→  [Ollama — llama3.1]
        ↓
  ┌─────┴─────────────────────────────────┐
  │           │           │        │       │
[Flashcards] [Explain] [RAG] [Summarize] [Quiz]
        ↓
[Frontend Output]
```

| Tool | What it does |
|---|---|
| 🃏 Flashcards | Generate flashcards on any topic |
| 💡 Explain | Explain a concept at any depth |
| 📄 RAG | Search your uploaded documents |
| 📝 Summarize | Summarize topics automatically |
| 🧪 Quiz | Generate multiple-choice questions |

---

## API Reference

### Auth

| Method | Route | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Create a new account |
| `POST` | `/api/auth/login` | Log in and receive a JWT token |

### Learning *(requires auth)*

| Method | Route | Description |
|---|---|---|
| `POST` | `/api/chat` | General AI chat |
| `POST` | `/api/rag-qa` | Chat with your documents |
| `POST` | `/api/quiz` | Generate an MCQ quiz |
| `POST` | `/api/flashcards` | Generate flashcards |
| `POST` | `/api/explain` | Explain a concept |
| `POST` | `/api/resume` | Summarize text |

### Documents *(requires auth)*

| Method | Route | Description |
|---|---|---|
| `GET` | `/api/documents` | List your documents |
| `POST` | `/api/upload` | Upload a PDF, TXT, or DOCX file |
| `DELETE` | `/api/documents/{filename}` | Delete a document |

---

## Deploying to Hugging Face Spaces

```dockerfile
FROM python:3.11-slim
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

Add these under **Settings → Variables and secrets**:

```
HF_TOKEN=...
HF_MODEL=Qwen/Qwen2.5-72B-Instruct
SECRET_KEY=...
```

---

## Tech Stack

**Backend** — FastAPI · SQLite + SQLAlchemy · ChromaDB · HuggingFace InferenceClient · python-jose · pdfplumber · python-docx

**Frontend** — React 18 · Vite

**Local AI** — n8n · Ollama · llama3.1

**Deployment** — Hugging Face Spaces (Docker)

---

## Security

- Passwords hashed with SHA-256 + random salt
- JWT tokens expire after 24 hours
- All routes protected by auth middleware
- Documents and ChromaDB collections isolated by `user_id`
- Files stored under `documents/{user_id}/`

---

## Live Demo

🔗 [huggingface.co/spaces/ApyHTML19/PaperBrainAI](https://huggingface.co/spaces/ApyHTML19/PaperBrainAI)
