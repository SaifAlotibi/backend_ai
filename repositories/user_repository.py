from sqlmodel import Session, select

from database import User


def get_user_by_email(
    session: Session,
    email: str
):
    statement = select(User).where(
        User.email == email
    )

    return session.exec(statement).first()


def get_user_by_id(
    session: Session,
    user_id: int
):
    return session.get(User, user_id)