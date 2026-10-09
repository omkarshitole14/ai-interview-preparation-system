import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

CHUNKS_PATH = (
    BASE_DIR
    / "knowledge_based"
    / "processed"
    / "python_interview_chunks.json"
)


def main():
    data = json.loads(
        CHUNKS_PATH.read_text(encoding="utf-8")
    )

    print("Total chunks:", len(data))

    for chunk in data:
        print(
            f"Chunk {chunk['chunk_id']} | "
            f"{len(chunk['text'])} chars | "
            f"Source: {chunk['source']}"
        )


if __name__ == "__main__":
    main()