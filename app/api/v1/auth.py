"""Authentication endpoints: register, login (OAuth2 password flow), me."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, DbSession
from app.core.security import create_access_token
from app.crud import user as user_crud
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: DbSession) -> UserRead:
    if user_crud.get_by_email(db, payload.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    user = user_crud.create(db, payload)
    return user  # type: ignore[return-value]


@router.post("/login", response_model=Token)
def login(
    db: DbSession,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """OAuth2 password flow. ``username`` field carries the email."""
    user = user_crud.authenticate(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(subject=user.id)
    return Token(access_token=token)


@router.get("/me", response_model=UserRead)
def read_me(current_user: CurrentUser) -> UserRead:
    return current_user  # type: ignore[return-value]
