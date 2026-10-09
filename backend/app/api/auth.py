from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config import (
    REFRESH_TOKEN_COOKIE_NAME,
    REFRESH_TOKEN_COOKIE_SAMESITE,
    REFRESH_TOKEN_COOKIE_SECURE,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.auth_service import (
    authenticate_user,
    refresh_access_token,
    register_user,
    revoke_refresh_token,
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


def _set_refresh_cookie(
    response: Response,
    refresh_token: str,
) -> None:

    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=REFRESH_TOKEN_COOKIE_SECURE,
        samesite=REFRESH_TOKEN_COOKIE_SAMESITE,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/auth",
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        user = register_user(
            db=db,
            email=request.email,
            password=request.password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: UserLoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    try:
        access_token, refresh_token = authenticate_user(
            db=db,
            email=request.email,
            password=request.password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
            headers={
                "WWW-Authenticate": "Bearer"
            },
        ) from exc

    _set_refresh_cookie(
        response=response,
        refresh_token=refresh_token,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh(
    response: Response,
    db: Session = Depends(get_db),
    refresh_token: str | None = Cookie(
        default=None,
        alias=REFRESH_TOKEN_COOKIE_NAME,
    ),
):
    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Refresh token is missing.",
        )

    try:
        access_token, new_refresh_token = (
            refresh_access_token(
                db=db,
                refresh_token=refresh_token,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        ) from exc

    _set_refresh_cookie(
        response=response,
        refresh_token=new_refresh_token,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(
    response: Response,
    db: Session = Depends(get_db),
    refresh_token: str | None = Cookie(
        default=None,
        alias=REFRESH_TOKEN_COOKIE_NAME,
    ),
):
    if refresh_token:
        revoke_refresh_token(
            db=db,
            refresh_token=refresh_token,
        )

    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        path="/api/auth",
    )

    return {
        "message": "Logged out successfully."
    }


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user