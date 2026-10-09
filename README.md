# AI Interview Preparation System with RAG

An AI-powered interview preparation application built with FastAPI, Next.js, Google Gemini, and Retrieval-Augmented Generation (RAG).

The system combines resume analysis, candidate profile extraction, interview question generation, answer evaluation, and retrieval from a PDF-based knowledge base.

## Features

- User authentication and refresh-token session management
- Resume upload and analysis
- Candidate profile extraction
- AI-generated interview questions
- Interview answer evaluation
- RAG-based retrieval from PDF documents
- Local, file-based Qdrant vector search
- PostgreSQL database with SQLAlchemy and Alembic migrations
- Next.js frontend and FastAPI backend

## Tech Stack

### Backend
- Python
- FastAPI
- SQLAlchemy and Alembic
- PostgreSQL
- Google Gemini API
- LangChain
- Qdrant

### Frontend
- Next.js
- React
- TypeScript

## Project Structure

```text
.
├── backend/
│   ├── app/
│   ├── alembic/
│   ├── rag/
│   ├── tests/
│   └── requirements.txt
├── frontend/
├── knowledge_based/
│   └── documents/
├── .gitignore
└── README.md
```

## Prerequisites

- Python version compatible with `backend/requirements.txt`
- Node.js and npm
- PostgreSQL, with the application database created
- A Google Gemini API key

Qdrant runs locally using a file-based store under `knowledge_based/vector_store`; a separate Qdrant server is not required by the current implementation.

## Environment Configuration

Create a root `.env` file. Do not commit it.

```env
GEMINI_API_KEY=
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_interview_db

JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30
REFRESH_TOKEN_COOKIE_NAME=refresh_token
REFRESH_TOKEN_COOKIE_SECURE=false
REFRESH_TOKEN_COOKIE_SAMESITE=lax

FRONTEND_URL=http://localhost:3000
```

The values above are local-development examples. Use a strong, randomly generated `JWT_SECRET_KEY` and valid credentials for your environment.

The frontend uses `frontend/.env.local`. Set `NEXT_PUBLIC_API_URL` to the backend API base URL expected by the frontend.

Never commit `.env` files, API keys, database passwords, or JWT secrets.

## Backend Setup

From the project root, activate your existing virtual environment and install the backend dependencies:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

Ensure PostgreSQL is running, the database exists, and the root `.env` contains valid settings.

Run the database migrations:

```powershell
Set-Location backend
alembic upgrade head
```

Start the backend from the `backend` directory:

```powershell
python -m uvicorn app.main:app --reload
```

Local endpoints:

- API root: `http://127.0.0.1:8000/`
- Health check: `http://127.0.0.1:8000/health`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

## Frontend Setup

Open a second terminal in the project root:

```powershell
Set-Location frontend
npm install
npm run dev
```

The frontend development server normally runs at `http://localhost:3000`.

Available npm scripts:

```powershell
npm run dev
npm run build
npm run start
npm run lint
```

## Knowledge Base Ingestion

The ingestion pipeline processes PDF documents, creates chunks, and indexes them in the local Qdrant store.

The PDF source directory is `knowledge_based/documents`. From the project root, run:

```powershell
Set-Location backend
python -m rag.ingest
```

**Warning:** ingestion recreates the configured Qdrant collection. It may call the Gemini embedding API and incur API usage or quota limits. Run it only when you intend to rebuild the index.

Generated chunks and the local vector store are excluded from Git.

## Testing

From the project root:

```powershell
Set-Location backend
python -m pytest
```

## Security and Deployment Notes

- Keep API keys and database credentials in environment variables.
- Use a strong JWT secret and rotate it if it has been exposed.
- Configure CORS for the intended frontend origin before deployment; verify the backend CORS implementation rather than assuming `FRONTEND_URL` is already applied.
- Configure secure refresh-token cookies and HTTPS for production.
- Do not commit virtual environments, environment files, caches, generated vector stores, or local databases.

## Project Status

This project is under active development. Features, setup instructions, and deployment configuration may evolve.
