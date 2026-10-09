from rag.retriever import retrieve_relevant_documents


TEST_QUERIES = [
    "What is the difference between a list and a tuple in Python?",
    "Explain Python decorators.",
    "What is LEGB in Python?",
    "How do generators work in Python?",
    "What is FastAPI used for?",
    "Explain quantum entanglement.",
    "What is a Python context manager?",
    "What is shallow copy versus deep copy in Python?",
]


for query in TEST_QUERIES:
    print("\n" + "=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)

    results = retrieve_relevant_documents(
        query=query,
        top_k=3,
    )

    if not results:
        print("No sufficiently relevant chunks found.")
        continue

    for index, result in enumerate(results, start=1):
        print(
            f"\nResult {index}"
            f"\nChunk ID: {result['chunk_id']}"
            f"\nScore: {result['score']:.4f}"
            f"\nSource: {result['source']}"
        )

        print(f"Text:\n{result['text'][:500]}")