import hashlib
import secrets
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import REFRESH_TOKEN_EXPIRE_DAYS
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.auth_session import AuthSession
from app.models.user import User


def register_user(
    db: Session,
    email: str,
    password: str,
) -> User:

    normalized_email = email.strip().lower()

    existing_user = (
        db.query(User)
        .filter(User.email == normalized_email)
        .first()
    )

    if existing_user is not None:
        raise ValueError(
            "A user with this email already exists."
        )

    user = User(
        email=normalized_email,
        password_hash=hash_password(password),
        is_active=True,
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)

    except IntegrityError as exc:
        db.rollback()

        raise ValueError(
            "A user with this email already exists."
        ) from exc

    return user


def _hash_refresh_token(
    refresh_token: str,
) -> str:
    return hashlib.sha256(
        refresh_token.encode("utf-8")
    ).hexdigest()


def _create_refresh_session(
    db: Session,
    user_id: int,
) -> str:

    refresh_token = secrets.token_urlsafe(64)

    refresh_token_hash = _hash_refresh_token(
        refresh_token
    )

    expires_at = (
        datetime.utcnow()
        + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    session = AuthSession(
        user_id=user_id,
        refresh_token_hash=refresh_token_hash,
        expires_at=expires_at,
    )

    db.add(session)

    return refresh_token


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> tuple[str, str]:

    normalized_email = email.strip().lower()

    user = (
        db.query(User)
        .filter(User.email == normalized_email)
        .first()
    )

    if user is None:
        raise ValueError(
            "Invalid email or password."
        )

    if not user.is_active:
        raise ValueError(
            "User account is inactive."
        )

    if not verify_password(
        password,
        user.password_hash,
    ):
        raise ValueError(
            "Invalid email or password."
        )

    access_token = create_access_token(
        user.id
    )

    refresh_token = _create_refresh_session(
        db=db,
        user_id=user.id,
    )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return access_token, refresh_token


def refresh_access_token(
    db: Session,
    refresh_token: str,
) -> tuple[str, str]:

    refresh_token_hash = _hash_refresh_token(
        refresh_token
    )

    session = (
        db.query(AuthSession)
        .filter(
            AuthSession.refresh_token_hash
            == refresh_token_hash,
            AuthSession.revoked_at.is_(None),
        )
        .first()
    )

    if session is None:
        raise ValueError(
            "Invalid or revoked refresh token."
        )

    now = datetime.utcnow()

    if session.expires_at <= now:
        session.revoked_at = now
        db.commit()

        raise ValueError(
            "Refresh token has expired."
        )

    user = (
        db.query(User)
        .filter(
            User.id == session.user_id,
            User.is_active.is_(True),
        )
        .first()
    )

    if user is None:
        session.revoked_at = now
        db.commit()

        raise ValueError(
            "Authenticated user was not found."
        )

    session.revoked_at = now

    new_refresh_token = _create_refresh_session(
        db=db,
        user_id=user.id,
    )

    new_access_token = create_access_token(
        user.id
    )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return (
        new_access_token,
        new_refresh_token,
    )


def revoke_refresh_token(
    db: Session,
    refresh_token: str,
) -> None:

    refresh_token_hash = _hash_refresh_token(
        refresh_token
    )

    session = (
        db.query(AuthSession)
        .filter(
            AuthSession.refresh_token_hash
            == refresh_token_hash,
            AuthSession.revoked_at.is_(None),
        )
        .first()
    )

    if session is None:
        return

    session.revoked_at = datetime.utcnow()

    db.commit()