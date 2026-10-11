
import json

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.interview_repository import (
    create_interview_session,
)
from app.repositories.resume_repository import (
    create_resume,
    get_resume,
    get_resumes_for_user,
)
from app.schemas.resume import ResumeUploadResponse
from app.services.resume_analysis_service import analyze_resume_pdf


router = APIRouter(prefix="/api/resume", tags=["Resume"])


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF files are allowed.")

    pdf_bytes = await file.read()

    if not pdf_bytes:
        raise HTTPException(400, "Uploaded PDF is empty.")

    try:
        resume_text, candidate_profile = analyze_resume_pdf(pdf_bytes)

        resume = create_resume(
            db=db,
            user_id=current_user.id,
            filename=file.filename or "resume.pdf",
            extracted_text=resume_text,
            candidate_profile=candidate_profile,
        )

        session = create_interview_session(
            db=db,
            user_id=current_user.id,
            resume_id=resume.id,
        )

        db.commit()

        return {
            "resume_id": resume.id,
            "session_id": session.id,
            "filename": resume.filename,
            "resume_text": resume_text,
            "candidate_profile": candidate_profile.model_dump(mode="json"),
        }

    except ValueError as exc:
        db.rollback()
        raise HTTPException(400, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            500,
            "Failed to save resume.",
        ) from exc


@router.get("/history")
def get_resume_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resumes = get_resumes_for_user(
        db=db,
        user_id=current_user.id,
    )

    return [
        {
            "resume_id": resume.id,
            "filename": resume.filename,
            "created_at": resume.created_at,
            "sessions": [
                {
                    "session_id": session.id,
                    "status": session.status,
                    "interview_type": session.interview_type,
                    "question_count": session.question_count,
                    "created_at": session.created_at,
                }
                for session in resume.interview_sessions
            ],
        }
        for resume in resumes
    ]


@router.get("/{resume_id}")
def get_saved_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = get_resume(
        db=db,
        resume_id=resume_id,
        user_id=current_user.id,
    )

    if resume is None:
        raise HTTPException(404, "Resume not found.")

    sessions = sorted(
        resume.interview_sessions,
        key=lambda item: item.id,
        reverse=True,
    )

    if not sessions:
        raise HTTPException(
            404,
            "No interview session exists for this resume.",
        )

    try:
        profile = json.loads(resume.candidate_profile_json)
    except (TypeError, json.JSONDecodeError) as exc:
        raise HTTPException(
            500,
            "Saved candidate profile could not be read.",
        ) from exc

    return {
        "resume_id": resume.id,
        "session_id": sessions[0].id,
        "filename": resume.filename,
        "resume_text": resume.extracted_text,
        "candidate_profile": profile,
    }
