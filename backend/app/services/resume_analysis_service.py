from app.schemas.candidate import CandidateProfile
from app.services.candidate_service import analyze_resume
from app.services.resume_service import extract_resume_text

MAX_RESUME_TEXT_LENGTH=30000
def analyze_resume_pdf(pdf_bytes: bytes) -> tuple[str, CandidateProfile]:
    text = extract_resume_text(pdf_bytes)

    if not text:
        raise ValueError("Could not extract text from the PDF.")

    text=text.strip()

    if len(text.strip()) < 100:
        raise ValueError(
            "The resume contains too little readable text."
        )
    if len(text) > MAX_RESUME_TEXT_LENGTH:
        raise ValueError(
            "The resume text is too long to analyze."
        )

    candidate_profile=analyze_resume(text)
    return text, candidate_profile
