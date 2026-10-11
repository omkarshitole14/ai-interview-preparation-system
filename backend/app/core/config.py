import os

from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ai_interview_db")


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30")
)

REFRESH_TOKEN_COOKIE_NAME = os.getenv(
    "REFRESH_TOKEN_COOKIE_NAME",
    "refresh_token",
)

REFRESH_TOKEN_COOKIE_SECURE = (
    os.getenv(
        "REFRESH_TOKEN_COOKIE_SECURE",
        "false",
    ).lower()
    == "true"
)

REFRESH_TOKEN_COOKIE_SAMESITE = os.getenv(
    "REFRESH_TOKEN_COOKIE_SAMESITE",
    "lax",
)

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:3000",
)


if not JWT_SECRET_KEY:
    raise ValueError(
        "JWT_SECRET_KEY is not set in .env"
    )