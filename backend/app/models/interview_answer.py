from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    question_id: Mapped[int] = mapped_column(
        ForeignKey("interview_questions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    question: Mapped["InterviewQuestion"] = relationship(
        back_populates="answer",
    )

    evaluation: Mapped["Evaluation | None"] = relationship(
        back_populates="answer",
        uselist=False,
        cascade="all, delete-orphan",
    )