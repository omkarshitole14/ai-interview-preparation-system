import json

from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.schemas.candidate import CandidateProfile


def create_resume(
    db: Session,
    user_id: int,
    filename: str,
    extracted_text: str,
    candidate_profile: CandidateProfile,
) -> Resume:
    resume = Resume(
        user_id=user_id,
        filename=filename,
        extracted_text=extracted_text,
        candidate_profile_json=json.dumps(candidate_profile.model_dump(mode="json")),
    )

    db.add(resume)
    db.flush()

    return resume


def get_resume(
    db: Session,
    resume_id: int,
    user_id: int,
) -> Resume | None:
    return (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == user_id,
        )
        .first()
    )


def get_candidate_profile(
    db: Session,
    resume_id: int,
    user_id: int,
) -> CandidateProfile | None:
    resume = get_resume(
        db=db,
        resume_id=resume_id,
        user_id=user_id,
    )

    if resume is None:
        return None

    data = json.loads(resume.candidate_profile_json)

    return CandidateProfile.model_validate(data)