from rag.retriever import retrieve_relevant_documents
from rag.generator import (
    generate_general_answer,
    generate_rag_answer,
)


def query_rag(
    question: str,
    top_k: int = 3,
) -> tuple[str, list[dict], str]:
    question = question.strip()

    if not question:
        raise ValueError(
            "Question cannot be empty."
        )

    chunks = retrieve_relevant_documents(
        query=question,
        top_k=top_k,
    )

    if chunks:
        answer = generate_rag_answer(
            question=question,
            chunks=chunks,
        )

        return answer, chunks, "rag"

    answer = generate_general_answer(
        question=question,
    )

    return answer, [], "general"