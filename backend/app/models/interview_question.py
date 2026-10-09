from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    session_id: Mapped[int] = mapped_column(
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    difficulty: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    expected_topics: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    question_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    session: Mapped["InterviewSession"] = relationship(
        back_populates="questions",
    )

    answer: Mapped["InterviewAnswer | None"] = relationship(
        back_populates="question",
        uselist=False,
        cascade="all, delete-orphan",
    )