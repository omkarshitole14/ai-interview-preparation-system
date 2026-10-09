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

    for chunk in data:
        text = chunk["text"].lower()

        if any(
            keyword in text
            for keyword in [
                "generator",
               "decorator",
                "context manager",
            ]
        ):            print(f"\n--- CHUNK {chunk['chunk_id']} ---")
        print(chunk["text"])


if __name__ == "__main__":
    main()
