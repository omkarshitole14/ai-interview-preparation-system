from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config import GEMINI_API_KEY


if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in .env")


EMBEDDING_MODEL = "gemini-embedding-001"


embeddings = GoogleGenerativeAIEmbeddings(
    model=EMBEDDING_MODEL,
    google_api_key=GEMINI_API_KEY,
)
