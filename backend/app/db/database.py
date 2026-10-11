
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from app.core.config import (
    DATABASE_URL,
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_PORT,
    DB_USER,
)


if DATABASE_URL:
    database_url = DATABASE_URL.replace(
        "postgres://",
        "postgresql+psycopg://",
        1,
    ).replace(
        "postgresql://",
        "postgresql+psycopg://",
        1,
    )
else:
    if not DB_PASSWORD:
        raise ValueError("DB_PASSWORD is not set in .env")

    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_NAME,
    )


engine = create_engine(
    database_url,
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)
