from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import (
    User,
    Conversation,
    get_session
)

from dependencies import get_current_user

from schemas import (
    ConversationCreate,
    ConversationResponse
)


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"]
)


@router.post(
    "",
    response_model=ConversationResponse
)
def create_conversation(
    request: ConversationCreate,
    current_user: User = Depends(
        get_current_user
    ),
    session: Session = Depends(
        get_session
    )
):

    conversation = Conversation(
        title=request.title,
        user_id=current_user.id
    )

    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    return conversation


@router.get(
    "",
    response_model=list[ConversationResponse]
)
def list_conversations(
    current_user: User = Depends(
        get_current_user
    ),
    session: Session = Depends(
        get_session
    )
):

    statement = select(
        Conversation
    ).where(
        Conversation.user_id == current_user.id
    )

    return session.exec(
        statement
    ).all()