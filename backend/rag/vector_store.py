import json
import time
from pathlib import Path
from app.core.config import QDRANT_API_KEY, QDRANT_URL
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from rag.embedding import embeddings


BASE_DIR = Path(__file__).resolve().parents[2]

CHUNKS_PATH = (
    BASE_DIR
    / "knowledge_based"
    / "processed"
    / "all_interview_chunks.json"
)

VECTOR_STORE_PATH = (
    BASE_DIR
    / "knowledge_based"
    / "vector_store"
)

COLLECTION_NAME = "python_interview_knowledge"
USE_QDRANT_CLOUD = bool(QDRANT_URL and QDRANT_API_KEY)

EMBEDDING_BATCH_SIZE = 20
EMBEDDING_BATCH_DELAY = 65
MAX_RETRIES = 3


class ThrottledEmbeddings(Embeddings):
    """
    Wrapper used only during knowledge-base ingestion.

    Gemini's free embedding quota is rate-limited, so documents
    are processed in small batches with a delay between batches.
    """

    def __init__(
        self,
        base_embeddings: Embeddings,
        batch_size: int = EMBEDDING_BATCH_SIZE,
        batch_delay: int = EMBEDDING_BATCH_DELAY,
    ):
        self.base_embeddings = base_embeddings
        self.batch_size = batch_size
        self.batch_delay = batch_delay

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        all_embeddings = []

        total = len(texts)

        for start in range(0, total, self.batch_size):
            end = min(
                start + self.batch_size,
                total,
            )

            batch = texts[start:end]

            print(
                f"Embedding chunks "
                f"{start + 1}-{end} of {total}..."
            )

            embeddings_result = self._embed_batch_with_retry(
                batch
            )

            all_embeddings.extend(
                embeddings_result
            )

            if end < total:
                print(
                    f"Waiting {self.batch_delay} seconds "
                    "before the next embedding batch..."
                )

                time.sleep(self.batch_delay)

        return all_embeddings

    def embed_query(
        self,
        text: str,
    ) -> list[float]:
        return self.base_embeddings.embed_query(text)

    def _embed_batch_with_retry(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return self.base_embeddings.embed_documents(
                    texts
                )

            except Exception as exc:
                error_text = str(exc)

                if "429" not in error_text:
                    raise

                if attempt >= MAX_RETRIES:
                    raise

                wait_seconds = self._extract_retry_delay(
                    error_text
                )

                print(
                    f"Gemini embedding quota reached. "
                    f"Waiting {wait_seconds} seconds "
                    f"before retry "
                    f"({attempt}/{MAX_RETRIES - 1})..."
                )

                time.sleep(wait_seconds)

        raise RuntimeError(
            "Embedding batch failed after retries."
        )

    @staticmethod
    def _extract_retry_delay(
        error_text: str,
    ) -> int:
        """
        Extract Google's retry delay when present.

        Falls back to 65 seconds for the free-tier
        requests-per-minute limit.
        """

        import re

        match = re.search(
            r"retryDelay.*?(\d+)s",
            error_text,
        )

        if match:
            return max(
                int(match.group(1)) + 5,
                65,
            )

        match = re.search(
            r"retry in (\d+(?:\.\d+)?)s",
            error_text,
            re.IGNORECASE,
        )

        if match:
            return max(
                int(float(match.group(1))) + 5,
                65,
            )

        return 65


def load_documents() -> list[Document]:
    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            f"Chunks file not found: {CHUNKS_PATH}"
        )

    chunks = json.loads(
        CHUNKS_PATH.read_text(
            encoding="utf-8"
        )
    )

    documents = []

    for chunk in chunks:
        documents.append(
            Document(
                page_content=chunk["text"],
                metadata={
                    "chunk_id": chunk["chunk_id"],
                    "source": chunk["source"],
                },
            )
        )

    return documents



def delete_existing_collection() -> None:
    """Delete the existing collection from the configured Qdrant store."""

    if USE_QDRANT_CLOUD:
        client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            timeout=30,
        )
    else:
        if not VECTOR_STORE_PATH.exists():
            return

        client = QdrantClient(
            path=str(VECTOR_STORE_PATH)
        )

    try:
        if client.collection_exists(COLLECTION_NAME):
            print(
                f"Deleting existing Qdrant collection: "
                f"{COLLECTION_NAME}"
            )
            client.delete_collection(
                collection_name=COLLECTION_NAME
            )
            print("Existing Qdrant collection deleted.")
    finally:
        client.close()



def create_vector_store(
    documents: list[Document],
) -> QdrantVectorStore:
    if not documents:
        raise ValueError(
            "No documents available for indexing."
        )

    delete_existing_collection()

    ingestion_embeddings = ThrottledEmbeddings(
        base_embeddings=embeddings,
    )

    print()
    print("Creating a fresh Qdrant collection...")

    if USE_QDRANT_CLOUD:
        vector_store = QdrantVectorStore.from_documents(
            documents=documents,
            embedding=ingestion_embeddings,
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            collection_name=COLLECTION_NAME,
            batch_size=EMBEDDING_BATCH_SIZE,
        )
    else:
        vector_store = QdrantVectorStore.from_documents(
            documents=documents,
            embedding=ingestion_embeddings,
            path=str(VECTOR_STORE_PATH),
            collection_name=COLLECTION_NAME,
            batch_size=EMBEDDING_BATCH_SIZE,
        )

    return vector_store


def get_vector_store() -> tuple[
    QdrantVectorStore,
    QdrantClient,
]:
    if USE_QDRANT_CLOUD:
        client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            timeout=30,
        )
    else:
        client = QdrantClient(
            path=str(VECTOR_STORE_PATH)
        )

    try:
        if not client.collection_exists(COLLECTION_NAME):
            raise RuntimeError(
                f"Qdrant collection '{COLLECTION_NAME}' "
                "does not exist. Run knowledge-base ingestion first."
            )

        vector_store = QdrantVectorStore(
            client=client,
            collection_name=COLLECTION_NAME,
            embedding=embeddings,
        )

        return vector_store, client

    except Exception:
        client.close()
        raise


def build_vector_store() -> QdrantVectorStore:
    documents = load_documents()

    if not documents:
        raise ValueError(
            "No documents found in the processed knowledge base."
        )

    vector_store = create_vector_store(
        documents
    )

    return vector_store


if __name__ == "__main__":
    vector_store = build_vector_store()

    documents = load_documents()

    print()
    print("=" * 60)
    print(
        "LangChain Qdrant vector store created successfully."
    )
    print(
        "Collection:",
        COLLECTION_NAME,
    )
    print(
        "Documents indexed:",
        len(documents),
    )
    print("=" * 60)