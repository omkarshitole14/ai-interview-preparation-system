from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_rag_query_rejects_empty_question():
    response = client.post(
        "/api/rag/query",
        json={
            "question": "",
            "top_k": 3,
        },
    )

    assert response.status_code == 422


def test_rag_query_rejects_invalid_top_k():
    response = client.post(
        "/api/rag/query",
        json={
            "question": "What is a Python list?",
            "top_k": 0,
        },
    )

    assert response.status_code == 422


def test_rag_query_falls_back_when_no_relevant_context():
    with patch(
        "app.services.rag_service.retrieve_relevant_documents",
        return_value=[],
    ), patch(
        "app.services.rag_service.generate_general_answer",
        return_value="General answer.",
    ):
        response = client.post(
            "/api/rag/query",
            json={
                "question": "What is quantum entanglement?",
                "top_k": 3,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == "What is quantum entanglement?"
    assert data["answer"] == "General answer."
    assert data["mode"] == "general"
    assert data["source_label"] == "Gemini General Knowledge"
    assert data["sources"] == []


def test_rag_query_returns_503_on_gemini_error():
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
        side_effect=RuntimeError(
            "Gemini API quota exceeded. Please try again later."
        ),
    ):
        response = client.post(
            "/api/rag/query",
            json={
                "question": "What is the difference between a list and a tuple?",
                "top_k": 3,
            },
        )

    assert response.status_code == 503

    assert response.json()["detail"] == (
        "Gemini API quota exceeded. Please try again later."
    )


def test_rag_query_success():
    fake_chunks = [
        {
            "chunk_id": 14,
            "source": "Python_Interview_Preparation_Detailed.pdf",
            "text": "A decorator modifies the behavior of a function.",
            "score": 0.61,
        }
    ]

    with patch(
        "app.api.rag.query_rag",
        return_value=(
            "A decorator modifies the behavior of a function.",
            fake_chunks,
            "rag",
        ),
    ) as mock_query:

        response = client.post(
            "/api/rag/query",
            json={
                "question": "What is a Python decorator?",
                "top_k": 3,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == "What is a Python decorator?"
    assert data["answer"] == (
        "A decorator modifies the behavior of a function."
    )
    assert data["mode"] == "rag"
    assert data["source_label"] == "Knowledge Base"

    assert len(data["sources"]) == 1

    assert data["sources"][0]["chunk_id"] == 14

    assert data["sources"][0]["source"] == (
        "Python_Interview_Preparation_Detailed.pdf"
    )

    assert data["sources"][0]["score"] == 0.61

    mock_query.assert_called_once_with(
        question="What is a Python decorator?",
        top_k=3,
    )