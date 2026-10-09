from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True
    )

    status: Mapped[str] = mapped_column(
        String(50), default="created", nullable=False
    )

    interview_type: Mapped[str] = mapped_column(
        String(50), default="mixed", nullable=False
    )

    question_count: Mapped[int] = mapped_column(
        Integer, default=10, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="interview_sessions")
    resume: Mapped["Resume"] = relationship(back_populates="interview_sessions")
    questions: Mapped[list["InterviewQuestion"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )