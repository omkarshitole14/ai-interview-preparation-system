from app.services.gemini_service import generate_text
from rag.context import build_context


def generate_rag_answer(
    question: str,
    chunks: list[dict],
) -> str:
    question = question.strip()

    if not question:
        raise ValueError(
            "Question cannot be empty."
        )

    if not chunks:
        raise ValueError(
            "No relevant context was retrieved."
        )

    context = build_context(chunks)

    if not context:
        raise ValueError(
            "No relevant context was retrieved."
        )

    prompt = f"""
You are an interview preparation assistant using a curated knowledge base.

Answer the user's question using the retrieved context as the primary factual source.

Rules:
- Prefer information supported by the retrieved context.
- Do not claim that information came from the knowledge base if it is not supported by the context.
- If the context is insufficient for a detail, say that the knowledge base does not provide that detail.
- Do not invent facts.
- Give a clear and concise answer suitable for interview preparation.

Retrieved context:
{context}

User question:
{question}

Answer:
"""

    return generate_text(prompt).strip()


def generate_general_answer(
    question: str,
) -> str:
    question = question.strip()

    if not question:
        raise ValueError(
            "Question cannot be empty."
        )

    prompt = f"""
You are a general interview preparation assistant.

The user's question did not have sufficiently relevant information in the curated knowledge base.
Answer using your general knowledge.

Rules:
- Do not claim that the answer came from the knowledge base.
- Give a clear, accurate, concise answer suitable for interview preparation.
- If you are uncertain about a fact, say so instead of inventing information.

User question:
{question}

Answer:
"""

    return generate_text(prompt).strip()