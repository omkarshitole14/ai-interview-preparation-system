from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    answer_id: Mapped[int] = mapped_column(
        ForeignKey("interview_answers.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    feedback: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    strengths: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    improvements: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    answer: Mapped["InterviewAnswer"] = relationship(
        back_populates="evaluation",
    )