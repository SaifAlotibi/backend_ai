from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from database import User, get_session

from dependencies import get_current_user

from rate_limiter import rate_limit

from schemas import (
    ChatRequest,
    ChatResponse
)

from services.chat_service import (
    process_chat,
    stream_process_chat
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post(
    "",
    response_model=ChatResponse
)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(
        get_current_user
    ),
    session: Session = Depends(
        get_session
    ),
    _: None = Depends(
        rate_limit
    )
):

    answer = await process_chat(
        session=session,
        conversation_id=request.conversation_id,
        user_id=current_user.id,
        user_message=request.message
    )

    return {
        "answer": answer
    }


@router.post(
    "/stream"
)
async def stream_chat(
    request: ChatRequest,
    current_user: User = Depends(
        get_current_user
    ),
    session: Session = Depends(
        get_session
    ),
    _: None = Depends(
        rate_limit
    )
):
    generator = await stream_process_chat(
        session=session,
        conversation_id=request.conversation_id,
        user_id=current_user.id,
        user_message=request.message
    )

    return StreamingResponse(
        generator,
        media_type="text/plain"
    )