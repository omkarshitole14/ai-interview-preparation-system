from unittest.mock import patch

from app.services.rag_service import query_rag


def test_rag_rejects_empty_question():
    try:
        query_rag("")
        assert False
    except ValueError as exc:
        assert str(exc) == "Question cannot be empty."


def test_rag_falls_back_to_general_gemini_when_no_context():
    with patch(
        "app.services.rag_service.retrieve_relevant_documents",
        return_value=[],
    ), patch(
        "app.services.rag_service.generate_general_answer",
        return_value="General answer.",
    ):
        answer, chunks, mode = query_rag(
            "What is quantum entanglement?"
        )

    assert answer == "General answer."
    assert chunks == []
    assert mode == "general"


def test_rag_service_returns_answer_and_sources():
    mock_chunks = [
        {
            "chunk_id": 5,
            "source": "Python_Interview_Preparation_Detailed.pdf",
            "text": "Lists are mutable while tuples are immutable.",
            "score": 0.67,
        }
    ]

    with patch(
        "app.services.rag_service.retrieve_relevant_documents",
        return_value=mock_chunks,
    ), patch(
        "app.services.rag_service.generate_rag_answer",
        return_value="A list is mutable, while a tuple is immutable.",
    ):
        answer, chunks, mode = query_rag(
            question="What is the difference between a list and a tuple?",
            top_k=3,
        )

    assert answer == "A list is mutable, while a tuple is immutable."
    assert chunks == mock_chunks
    assert mode == "rag"


def test_query_rag_success():
    fake_chunks = [
        {
            "chunk_id": 14,
            "source": "Python_Interview_Preparation_Detailed.pdf",
            "text": "A decorator modifies the behavior of a function.",
            "score": 0.61,
        }
    ]

    with patch(
        "app.services.rag_service.retrieve_relevant_documents",
        return_value=fake_chunks,
    ) as mock_retrieve, patch(
        "app.services.rag_service.generate_rag_answer",
        return_value="A decorator modifies the behavior of a function.",
    ) as mock_generate:
        answer, chunks, mode = query_rag(
            question="What is a Python decorator?",
            top_k=3,
        )

    assert answer == "A decorator modifies the behavior of a function."
    assert chunks == fake_chunks
    assert mode == "rag"

    mock_retrieve.assert_called_once_with(
        query="What is a Python decorator?",
        top_k=3,
    )

    mock_generate.assert_called_once_with(
        question="What is a Python decorator?",
        chunks=fake_chunks,
    )