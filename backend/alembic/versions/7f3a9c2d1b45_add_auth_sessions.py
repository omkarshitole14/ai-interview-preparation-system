"""add auth sessions for refresh tokens

Revision ID: 7f3a9c2d1b45
Revises: ef7b4a3c2d11
Create Date: 2026-10-07

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7f3a9c2d1b45"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "ef7b4a3c2d11"

branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auth_sessions",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "refresh_token_hash",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "revoked_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "refresh_token_hash"
        ),
    )

    op.create_index(
        "ix_auth_sessions_user_id",
        "auth_sessions",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_auth_sessions_refresh_token_hash",
        "auth_sessions",
        ["refresh_token_hash"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_auth_sessions_refresh_token_hash",
        table_name="auth_sessions",
    )

    op.drop_index(
        "ix_auth_sessions_user_id",
        table_name="auth_sessions",
    )

    op.drop_table("auth_sessions")