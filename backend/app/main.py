from fastapi import FastAPI, Request
from app.api.resume import router as resume_router
from app.core.exceptions import general_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from app.api.interview import router as interview_router
from app.api.rag import router as rag_router
from app.api.auth import router as auth_router

from app.core.config import FRONTEND_URL




app = FastAPI(title="AI Interview Preparation System")

app.include_router(rag_router)
app.include_router(auth_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(Exception,general_exception_handler)
app.include_router(resume_router)
app.include_router(interview_router)

@app.get("/")
def root():
    return {"message": "AI Interview Preparation System"}

@app.get("/health")
def health_check():
    return {"status": "ok"}