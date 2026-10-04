from sqlmodel import Session, select

from database import Message


def save_message(
    session: Session,
    role: str,
    content: str,
    conversation_id: int
):
    message = Message(
        role=role,
        content=content,
        conversation_id=conversation_id
    )

    session.add(message)
    session.commit()
    session.refresh(message)

    return message


def get_messages(
    session: Session,
    conversation_id: int
):
    statement = (
        select(Message)
        .where(
            Message.conversation_id == conversation_id
        )
        .order_by(Message.id)
    )

    return session.exec(statement).all()