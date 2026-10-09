from typing import Literal

from pydantic import BaseModel, Field


class RAGQueryRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=5000,
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
    )


class RAGSource(BaseModel):
    chunk_id: int
    source: str
    text: str
    score: float | None = None


class RAGQueryResponse(BaseModel):
    question: str
    answer: str
    mode: Literal["rag", "general"]
    source_label: str
    sources: list[RAGSource] = Field(
        default_factory=list
    )