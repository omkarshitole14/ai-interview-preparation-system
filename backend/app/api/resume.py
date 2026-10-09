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
from app.repositories.resume_repository import create_resume
from app.schemas.resume import (
    ResumeAnalysisRequest,
    ResumeUploadResponse,
)
from app.services.candidate_service import analyze_resume
from app.services.resume_analysis_service import (
    analyze_resume_pdf,
)


router = APIRouter(
    prefix="/api/resume",
    tags=["Resume"],
)


@router.post(
    "/upload",
    response_model=ResumeUploadResponse,
)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    pdf_bytes = await file.read()

    if not pdf_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded PDF is empty.",
        )

    try:
        resume_text, candidate_profile = analyze_resume_pdf(
            pdf_bytes
        )

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
            "filename": file.filename,
            "resume_text": resume_text,
            "candidate_profile": candidate_profile.model_dump(
                mode="json"
            ),
        }

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to save resume.",
        ) from exc