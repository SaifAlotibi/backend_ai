from typing import Generator

from sqlmodel import (
    SQLModel,
    Field,
    Session,
    create_engine,
    select
)

from config import DATABASE_URL


engine = create_engine(
    DATABASE_URL
)

# =========================
# User
# =========================

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    name: str
    email: str = Field(index=True, unique=True)

    hashed_password: str


# =========================
# Conversation
# =========================

class Conversation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    user_id: int = Field(foreign_key="user.id", index=True)
    summary: str | None = None
    summary_message_count: int = 0

# =========================
# Message
# =========================

class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    role: str

    content: str

    conversation_id: int = Field(
        foreign_key="conversation.id",
        index=True
    )


# =========================
# Database setup
# =========================

def create_tables():
    SQLModel.metadata.create_all(engine)


# =========================
# Session dependency
# =========================

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
