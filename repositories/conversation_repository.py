from sqlmodel import Session, select

from database import Conversation


def get_conversation_for_user(
    session: Session,
    conversation_id: int,
    user_id: int
):
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )

    return session.exec(statement).first()