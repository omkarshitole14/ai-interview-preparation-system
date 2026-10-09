from unittest.mock import patch

from app.services.rag_service import query_rag


def test_rag_pipeline_connects_retrieval_to_generation():
    fake_chunks = [
        {
            "chunk_id": 14,
            "source": "Python_Interview_Preparation_Detailed.pdf",
            "text": "A decorator wraps a function or class to add or change behavior.",
            "score": 0.6136,
        }
    ]

    with patch(
        "app.services.rag_service.retrieve_relevant_documents",
        return_value=fake_chunks,
    ), patch(
        "app.services.rag_service.generate_rag_answer",
        return_value="A decorator wraps a function to add or change its behavior.",
    ) as mock_generator:

        answer, chunks, mode = query_rag(
            question="What is a Python decorator?",
            top_k=3,
        )

    assert answer == "A decorator wraps a function to add or change its behavior."
    assert chunks == fake_chunks
    assert mode == "rag"

    mock_generator.assert_called_once_with(
        question="What is a Python decorator?",
        chunks=fake_chunks,
    )