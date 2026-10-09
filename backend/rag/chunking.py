import json
from pathlib import Path
import re

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter


CHUNK_SIZE = 900
CHUNK_OVERLAP = 120

BASE_DIR = Path(__file__).resolve().parents[2]

DOCUMENTS_PATH = BASE_DIR / "knowledge_based" / "documents"

OUTPUT_PATH = (
    BASE_DIR
    / "knowledge_based"
    / "processed"
    / "all_interview_chunks.json"
)


def extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    return "\n".join(pages).strip()


def create_chunks(text: str) -> list[str]:
    text = text.strip()

    if not text:
        return []

    sections = re.split(
        r"(?=\n?\d+\. )",
        text,
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
    )

    chunks = []

    for section in sections:
        section = section.strip()

        if not section:
            continue

        section_chunks = splitter.split_text(section)

        for chunk in section_chunks:
            cleaned_chunk = chunk.strip()

            if not cleaned_chunk:
                continue

            if not any(char.isalnum() for char in cleaned_chunk):
                continue

            if len(cleaned_chunk) < 20:
                continue

            chunks.append(cleaned_chunk)

    return chunks


def build_all_chunks() -> list[dict]:
    if not DOCUMENTS_PATH.exists():
        raise FileNotFoundError(
            f"Knowledge-base directory not found: {DOCUMENTS_PATH}"
        )

    pdf_files = sorted(DOCUMENTS_PATH.glob("*.pdf"))

    if not pdf_files:
        raise ValueError(
            f"No PDF files found in: {DOCUMENTS_PATH}"
        )

    all_chunks = []
    global_chunk_id = 0

    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path.name}")

        text = extract_pdf_text(pdf_path)

        if not text:
            print("  WARNING: No extractable text found.")
            continue

        chunks = create_chunks(text)

        print(f"  Characters: {len(text)}")
        print(f"  Chunks: {len(chunks)}")

        for chunk in chunks:
            all_chunks.append(
                {
                    "chunk_id": global_chunk_id,
                    "source": pdf_path.name,
                    "text": chunk,
                }
            )

            global_chunk_id += 1

    return all_chunks


def save_chunks(chunks: list[dict]) -> None:
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            chunks,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    chunks = build_all_chunks()

    save_chunks(chunks)

    print()
    print("=" * 60)
    print("PDF processing completed.")
    print("Total PDFs:", len(list(DOCUMENTS_PATH.glob("*.pdf"))))
    print("Total chunks:", len(chunks))
    print("Saved to:", OUTPUT_PATH)
    print("=" * 60)