from datetime import datetime, timedelta, timezone

import jwt

from dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from pwdlib import PasswordHash
from sqlmodel import Session

from config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

from database import (
    User,
    get_session,
)

from schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse
)
from repositories.user_repository import (
    get_user_by_email
    )

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


password_hash = PasswordHash.recommended()

@router.get(
    "/me",
    response_model=UserResponse
)
def me(
    current_user: User = Depends(get_current_user)
):
    return current_user

def create_access_token(user_id: int):

    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )


@router.post(
    "/register",
    response_model=UserResponse
)
def register(
    request: RegisterRequest,
    session: Session = Depends(get_session)
):

    existing_user = get_user_by_email(
        session,
        request.email
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = password_hash.hash(
        request.password
    )

    user = User(
        name=request.name,
        email=request.email,
        hashed_password=hashed_password
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    request: LoginRequest,
    session: Session = Depends(get_session)
):

    user = get_user_by_email(
        session,
        request.email
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    password_correct = password_hash.verify(
        request.password,
        user.hashed_password
    )

    if not password_correct:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(
        user.id
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
