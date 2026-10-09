from fastapi import APIRouter, HTTPException

from app.schemas.rag import (
    RAGQueryRequest,
    RAGQueryResponse,
)
from app.services.rag_service import query_rag


router = APIRouter(
    prefix="/api/rag",
    tags=["RAG"],
)


@router.post(
    "/query",
    response_model=RAGQueryResponse,
)
def query_rag_endpoint(
    request: RAGQueryRequest,
):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        answer, chunks, mode = query_rag(
            question=question,
            top_k=request.top_k,
        )

        sources = [
            {
                "chunk_id": chunk["chunk_id"],
                "source": chunk["source"],
                "text": chunk["text"],
                "score": chunk.get("score"),
            }
            for chunk in chunks
        ]

        return {
            "question": question,
            "answer": answer,
            "mode": mode,
            "source_label": (
                "Knowledge Base"
                if mode == "rag"
                else "Gemini General Knowledge"
            ),
            "sources": sources,
        }

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc