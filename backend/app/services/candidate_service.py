from google.genai import errors
from pydantic import ValidationError

from app.services.gemini_service import client
from app.schemas.candidate import (
    CandidateProfile,
    CandidateProfileExtraction,
)


def analyze_resume(resume_text: str) -> CandidateProfile:
    prompt = f"""
Analyze the following resume and extract the candidate profile.

Extract only information explicitly supported by the resume.
Do not invent missing information.

Return:
- name
- education
- skills
- projects
- experience
- certifications

If a field is not present in the resume, return an empty list or null
as appropriate.

Resume:
{resume_text}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": CandidateProfileExtraction,
            },
        )

    except errors.APIError as exc:
        status_code = getattr(exc, "code", None)

        if status_code == 429:
            raise ValueError(
                "Gemini API quota exceeded. Please try again later."
            ) from exc

        if status_code == 503:
            raise ValueError(
                "Gemini API is temporarily unavailable. Please try again later."
            ) from exc

        raise ValueError(
            "Gemini API request failed. Please try again later."
        ) from exc

    if not response.text:
        raise ValueError(
            "Gemini returned an empty response."
        )

    try:
        extracted_profile = CandidateProfileExtraction.model_validate_json(
            response.text
        )

    except ValidationError as exc:
        raise ValueError(
            f"Gemini returned an invalid candidate profile: {exc}"
        ) from exc

    return CandidateProfile(
        name=extracted_profile.name,
        education=extracted_profile.education,
        skills=extracted_profile.skills,
        projects=extracted_profile.projects,
        experience=extracted_profile.experience,
        certifications=extracted_profile.certifications,
    )