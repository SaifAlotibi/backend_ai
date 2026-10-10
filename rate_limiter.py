import time

from fastapi import Depends, HTTPException

from database import User
from dependencies import get_current_user


# =========================================
# Configuration
# =========================================

MAX_REQUESTS = 10
WINDOW_SECONDS = 60


# user_id -> list of request timestamps
request_history = {}


def rate_limit(
    current_user: User = Depends(
        get_current_user
    )
):
    now = time.monotonic()

    timestamps = request_history.get(
        current_user.id,
        []
    )

    # Keep only requests inside the current window
    timestamps = [
        timestamp
        for timestamp in timestamps
        if now - timestamp < WINDOW_SECONDS
    ]

    # Rate limit exceeded
    if len(timestamps) >= MAX_REQUESTS:

        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later."
        )

    timestamps.append(now)

    request_history[
        current_user.id
    ] = timestamps