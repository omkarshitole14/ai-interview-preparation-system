from rag.chunking import build_all_chunks, save_chunks
from rag.vector_store import build_vector_store


def main() -> None:
    print("=" * 60)
    print("STARTING KNOWLEDGE BASE INGESTION")
    print("=" * 60)

    print()
    print("Step 1: Processing PDFs...")
    chunks = build_all_chunks()

    if not chunks:
        raise ValueError(
            "No chunks were generated from the PDF files."
        )

    save_chunks(chunks)

    print()
    print(f"Generated chunks: {len(chunks)}")

    print()
    print("Step 2: Creating Qdrant vector store...")

    vector_store = build_vector_store()

    if vector_store is None:
        raise RuntimeError(
            "Vector store creation failed."
        )

    print()
    print("=" * 60)
    print("KNOWLEDGE BASE INGESTION COMPLETED")
    print("=" * 60)
    print(f"Total chunks indexed: {len(chunks)}")


if __name__ == "__main__":
    main()