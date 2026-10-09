from pydantic import BaseModel

from app.schemas.candidate import CandidateProfile


class ResumeAnalysisRequest(BaseModel):
    resume_text: str


class ResumeUploadResponse(BaseModel):
    resume_id: int
    session_id: int
    filename: str
    resume_text: str
    candidate_profile: CandidateProfile