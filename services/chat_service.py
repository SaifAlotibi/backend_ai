from sqlmodel import Session

from agent import run_agent

from repositories.conversation_repository import (
    get_conversation_for_user
)

from repositories.message_repository import (
    get_messages,
    save_message
)

async def process_chat(
    session: Session,
    conversation_id: int,
    user_id: int,
    user_message: str
):

    # 1. Find the conversation
    conversation = get_conversation_for_user(
        session,
        conversation_id,
        user_id
    )

    if conversation is None:
        return None

    # 2. Get previous messages
    db_messages = get_messages(
        session,
        conversation.id
    )

    messages = [
        {
            "role": message.role,
            "content": message.content
        }
        for message in db_messages
    ]

    # 3. Add the new user message
    messages.append({
        "role": "user",
        "content": user_message
    })

    # 4. Save user message
    save_message(
        session,
        "user",
        user_message,
        conversation.id
    )

    # 5. Ask the AI agent
    answer = await run_agent(
        messages
    )

    # 6. Save AI response
    save_message(
        session,
        "assistant",
        answer,
        conversation.id
    )

    return answer