from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from database import User, get_session

from dependencies import get_current_user

from schemas import (
    ChatRequest,
    ChatResponse
)

from services.chat_service import process_chat


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
    )
):

    answer = await process_chat(
        session=session,
        conversation_id=request.conversation_id,
        user_id=current_user.id,
        user_message=request.message
    )

    if answer is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    return {
        "answer": answer
    }