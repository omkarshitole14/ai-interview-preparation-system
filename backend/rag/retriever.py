from rag.vector_store import get_vector_store


MIN_RELEVANCE_SCORE = 0.61


def retrieve_relevant_documents(query: str, top_k: int = 3):
    query = query.strip()

    if not query:
        raise ValueError("Query cannot be empty.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    vector_store, client = get_vector_store()

    try:
        results = vector_store.similarity_search_with_score(
            query,
            k=top_k,
        )

        relevant_documents = []

        for document, score in results:
            if score < MIN_RELEVANCE_SCORE:
                continue

            relevant_documents.append(
                {
                    "chunk_id": document.metadata["chunk_id"],
                    "source": document.metadata["source"],
                    "text": document.page_content,
                    "score": float(score),
                }
            )

        return relevant_documents

    finally:
        client.close()