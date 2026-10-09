from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class CandidateProfileExtraction(BaseModel):
    name: str | None = None
    education: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)


class CandidateProfile(CandidateProfileExtraction):
    id: UUID = Field(default_factory=uuid4)