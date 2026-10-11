# AI Interview Preparation System with RAG

An AI-powered interview preparation platform that helps candidates analyze their resumes, practice interview questions, receive AI-generated feedback, and explore technical interview concepts using Retrieval-Augmented Generation (RAG).

**Live Demo:** https://ai-interview-preparation-system-os.vercel.app/

**GitHub Repository:** https://github.com/omkarshitole14/ai-interview-preparation-system

## Overview

Preparing for technical interviews requires more than memorizing answers. Candidates need to understand their own resumes, practice relevant questions, identify weaknesses, and learn concepts clearly.

This project brings these activities together in one web application. It combines resume analysis, AI-assisted interview practice, persistent interview history, and a RAG-based assistant for technical learning.

## Features

### Resume Analysis
- Upload a resume in PDF format.
- Extract and display resume text.
- Analyze candidate information, including education, skills, projects, experience, and certifications.
- Save and restore resume analysis through the backend.

### AI Interview Practice
- Generate interview questions based on the selected interview type.
- Practice technical, HR, resume-based, coding, machine learning, and Generative AI/RAG interviews.
- Submit answers for AI-based evaluation.
- Review scores, feedback, strengths, and areas for improvement.
- Retrieve saved interview questions, answers, and evaluations.

### RAG Assistant
- Retrieve relevant information from an interview-preparation knowledge base.
- Generate context-aware responses using retrieved content and a language model.
- Support learning and revision of technical interview concepts.

### Progress Tracking
- View interview question counts and evaluation progress.
- Restore saved work after signing in again.
- Review the progress of the currently restored interview session.

### Authentication and Responsive UI
- User authentication and protected API requests.
- Frontend and backend separation.
- Responsive interface for desktop and mobile devices.

## Technology Stack

| Area | Technologies |
|---|---|
| Frontend | Next.js, React, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI |
| AI / LLM | Google Gemini |
| Retrieval-Augmented Generation | LangChain and Qdrant |
| Relational database | Neon PostgreSQL |
| Vector database | Qdrant Cloud |
| Resume processing | PDF text extraction and candidate-profile parsing |
| Deployment | Vercel and Render |
| Version control | Git and GitHub |

## Architecture

The application uses a separate frontend and backend. The frontend communicates with FastAPI through HTTP API requests. The backend handles authentication, resume processing, interview workflows, persistence, and RAG operations.

```text
                 Candidate
                    |
                    v
          Next.js Frontend
             (Vercel)
                    |
              HTTP / REST
                    |
                    v
            FastAPI Backend
               (Render)
              /     |     \
             /      |      \
            v       v       v
         Neon    Gemini   Qdrant
       PostgreSQL  API    Cloud
                    ^
                    |
             Retrieved Context
                    |
          Interview Knowledge Base
```

**Typical RAG workflow**

1. The user asks a technical question.
2. The backend converts the query into a retrieval request.
3. Relevant knowledge-base content is retrieved from the vector database.
4. The retrieved context is supplied to the language model.
5. The model generates a response grounded in the available context.

## Project Structure

```text
ai-interview-preparation-system/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── repositories/
│   │   └── ...
│   ├── tests/
│   ├── migrate_qdrant_to_cloud.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── services/
│   │   └── ...
│   └── package.json
├── knowledge_based/
│   ├── documents/
│   └── processed/
└── README.md
```

*The tree highlights the main project areas; individual files may differ as the project evolves.*

## Live Deployment

| Component | Deployment |
|---|---|
| Frontend | [Open the application](https://ai-interview-preparation-system-os.vercel.app/) |
| Backend API | [Open API documentation](https://ai-interview-preparation-system-api.onrender.com/docs) |
| Source code | [GitHub repository](https://github.com/omkarshitole14/ai-interview-preparation-system) |

The frontend is deployed on Vercel, and the FastAPI backend is deployed on Render. The backend uses hosted database and AI services configured through environment variables.

## Run Locally

### Prerequisites

Install the following before starting:

- Python compatible with the backend dependencies
- Node.js and npm
- Git
- Access credentials for the external AI and database services required by the application

### 1. Clone the repository

```bash
git clone https://github.com/omkarshitole14/ai-interview-preparation-system.git
cd ai-interview-preparation-system
```

### 2. Set up the backend

From the repository root:

```powershell
cd backend
python -m venv venv
```

Activate the virtual environment on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install the backend dependencies:

```powershell
pip install -r requirements.txt
```

Configure the required environment variables using the names expected by `backend/app/core/config.py`. These may include AI-provider credentials, the PostgreSQL connection string, and Qdrant Cloud credentials.

Start the backend using the application's configured FastAPI entry point. For example, if the entry point is `app.main:app`:

```powershell
uvicorn app.main:app --reload
```

The API documentation is typically available at `http://127.0.0.1:8000/docs`.

### 3. Set up the frontend

Open another terminal from the repository root:

```powershell
cd frontend
npm install
```

Create a local `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Ensure this URL matches the port on which your backend is running.

Start the frontend:

```powershell
npm run dev
```

Open `http://localhost:3000` in your browser.

**Configuration note:** Verify the backend entry point and required environment-variable names against the current source code before running the application. Never commit `.env`, `.env.local`, API keys, passwords, or database credentials to GitHub.

## API Overview

The backend exposes API endpoints for the main application workflows, including:

- Authentication and current-user information.
- Resume upload, analysis, history, and retrieval.
- Interview question generation and session retrieval.
- Answer evaluation.
- RAG-based question answering.

Open the [deployed API documentation](https://ai-interview-preparation-system-api.onrender.com/docs) to inspect the available endpoints, request schemas, and response formats.

## Engineering Considerations

This project demonstrates practical experience with:

- Separating a Next.js frontend from a FastAPI backend.
- Designing REST API integrations.
- Handling authentication and authenticated requests.
- Persisting application data in a relational database.
- Using vector search for retrieval-augmented generation.
- Integrating an external LLM API.
- Deploying and debugging a multi-service application.
- Managing application state and restoring saved work.
- Building a responsive interface for desktop and mobile devices.

## Current Scope

The Reports section currently provides an interview progress summary. A downloadable PDF interview report should only be considered implemented once report generation and download functionality have been added and verified.

AI-generated feedback may occasionally be inaccurate. Candidates should use it as a practice aid rather than as a definitive assessment of their skills.

## Future Improvements

Potential future enhancements include:

- Downloadable interview performance reports.
- More detailed performance analytics across interview sessions.
- Improved retrieval quality and knowledge-base coverage.
- Additional interview categories and coding exercises.
- More comprehensive automated testing.

## Author

**Omkar Shitole**

Final-semester B.Tech student in Electronics and Telecommunication Engineering, building projects in AI/ML, Generative AI, Python, and software development.

- **GitHub:** https://github.com/omkarshitole14
- **LinkedIn:** https://www.linkedin.com/in/omkarshitole14/
- **Portfolio:** https://omkarshitole-portfolio.vercel.app/

---

*Built as a practical project to explore AI-assisted interview preparation, RAG, backend API development, data persistence, and full-stack deployment.*