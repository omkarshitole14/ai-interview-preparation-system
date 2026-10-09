from unittest.mock import MagicMock, patch

from langchain_core.documents import Document

from rag.retriever import retrieve_relevant_documents


def test_retriever_rejects_score_below_threshold():
    document = Document(
        page_content="Unrelated Python interview content.",
        metadata={
            "chunk_id": 1,
            "source": "01_Python_Interview_Knowledge.pdf",
        },
    )

    vector_store = MagicMock()
    client = MagicMock()

    vector_store.similarity_search_with_score.return_value = [
        (document, 0.607),
    ]

    with patch(
        "rag.retriever.get_vector_store",
        return_value=(vector_store, client),
    ):
        results = retrieve_relevant_documents(
            query="What is India?",
            top_k=3,
        )

    assert results == []
    client.close.assert_called_once()


def test_retriever_accepts_score_at_threshold():
    document = Document(
        page_content="A decorator modifies the behavior of a function.",
        metadata={
            "chunk_id": 14,
            "source": "Python_Interview_Preparation_Detailed.pdf",
        },
    )

    vector_store = MagicMock()
    client = MagicMock()

    vector_store.similarity_search_with_score.return_value = [
        (document, 0.61),
    ]

    with patch(
        "rag.retriever.get_vector_store",
        return_value=(vector_store, client),
    ):
        results = retrieve_relevant_documents(
            query="What is a Python decorator?",
            top_k=3,
        )

    assert len(results) == 1
    assert results[0]["chunk_id"] == 14
    assert results[0]["score"] == 0.61
    client.close.assert_called_once()