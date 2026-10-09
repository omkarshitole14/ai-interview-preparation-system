"""add interview configuration to sessions

Revision ID: ef7b4a3c2d11
Revises: d630ff51741b
Create Date: 2026-10-05

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ef7b4a3c2d11"
down_revision: Union[str, Sequence[str], None] = "d630ff51741b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "interview_sessions",
        sa.Column(
            "interview_type",
            sa.String(length=50),
            nullable=False,
            server_default="mixed",
        ),
    )

    op.add_column(
        "interview_sessions",
        sa.Column(
            "question_count",
            sa.Integer(),
            nullable=False,
            server_default="10",
        ),
    )

    op.alter_column(
        "interview_sessions",
        "interview_type",
        server_default=None,
    )

    op.alter_column(
        "interview_sessions",
        "question_count",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column(
        "interview_sessions",
        "question_count",
    )

    op.drop_column(
        "interview_sessions",
        "interview_type",
    )