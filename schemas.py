from pydantic import BaseModel, Field


# =========================
# Authentication
# =========================

class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)

    email: str

    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: str

    password: str


class TokenResponse(BaseModel):
    access_token: str

    token_type: str


class UserResponse(BaseModel):
    id: int

    name: str

    email: str


# =========================
# Conversations
# =========================

class ConversationCreate(BaseModel):
    title: str = Field(
        default="New Conversation",
        max_length=200
    )


class ConversationResponse(BaseModel):
    id: int

    title: str

    user_id: int


# =========================
# Chat
# =========================

class ChatRequest(BaseModel):
    conversation_id: int

    message: str = Field(
        min_length=1
    )


class ChatResponse(BaseModel):
    answer: str