from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session

import jwt
from jwt import InvalidTokenError

from config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM
)

from database import (
    User,
    get_session
)


security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        user = session.get(
            User,
            int(user_id)
        )

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        return user

    except (InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )