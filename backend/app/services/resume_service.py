from io import BytesIO

from pypdf import PdfReader


def extract_resume_text(pdf_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(pdf_bytes))

    extracted_text = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            extracted_text.append(text)

    return "\n".join(extracted_text).strip()