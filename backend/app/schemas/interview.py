from typing import Literal

from pydantic import BaseModel, Field


InterviewType = Literal[
    "mixed",
    "technical",
    "hr",
    "resume",
    "coding",
    "ml_ai",
    "genai_rag",
]


class InterviewQuestion(BaseModel):
    id: int | None = None
    question: str
    category: str
    difficulty: str
    expected_topics: list[str]


class InterviewQuestionResponse(BaseModel):
    questions: list[InterviewQuestion]


class InterviewQuestionRequest(BaseModel):
    session_id: int
    interview_type: InterviewType = "mixed"
    question_count: Literal[5, 10, 15] = 10


class InterviewAnswerRequest(BaseModel):
    question_id: int
    answer: str = Field(min_length=1, max_length=10000)


class InterviewAnswerEvaluation(BaseModel):
    score: int = Field(ge=0, le=10)
    feedback: str
    strengths: list[str]
    improvements: list[str]
    time_complexity: str | None = None
    space_complexity: str | None = None