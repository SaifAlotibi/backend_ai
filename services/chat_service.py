import asyncio
import logging

from fastapi import HTTPException
from sqlmodel import Session

from agent import run_agent, stream_agent

from repositories.conversation_repository import get_conversation_for_user
from repositories.message_repository import get_messages, save_message

from services.memory_service import maybe_summarize_conversation

from request_context import get_request_id

from config import MAX_HISTORY_MESSAGES, RECENT_MESSAGES


logger = logging.getLogger(__name__)


# ==========================================
# 1. Build Conversation Context
# ==========================================

def build_conversation_context(
    session: Session,
    conversation
):
    messages = []

    # Include previous conversation summary
    if conversation.summary:
        messages.append({
            "role": "system",
            "content": (
                "Previous conversation summary:\n"
                + conversation.summary
            )
        })

    # Load recent conversation messages
    db_messages = get_messages(
        session,
        conversation.id
    )

    recent_messages = db_messages[-RECENT_MESSAGES:]

    for message in recent_messages:
        messages.append({
            "role": message.role,
            "content": message.content
        })

    return messages


# ==========================================
# 2. Normal Chat
# ==========================================

async def process_chat(
    session: Session,
    conversation_id: int,
    user_id: int,
    user_message: str
):
    logger.info(
    "Chat request started | request_id=%s | user_id=%s | conversation_id=%s",
    get_request_id(),
    user_id,
    conversation_id,
)

    # Verify conversation ownership
    conversation = get_conversation_for_user(
        session,
        conversation_id,
        user_id
    )

    if conversation is None:
        logger.warning(
            "Conversation not found or unauthorized | "
            "user_id=%s | conversation_id=%s",
            user_id,
            conversation_id,
        )

        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    # Build conversation context
    messages = build_conversation_context(
        session,
        conversation
    )

    # Add current user message
    messages.append({
        "role": "user",
        "content": user_message
    })

    # Save user message
    save_message(
        session,
        "user",
        user_message,
        conversation.id
    )

    logger.info(
        "Starting agent | conversation_id=%s",
        conversation_id,
    )

    # Run AI agent with timeout
    try:

        answer = await asyncio.wait_for(
            run_agent(messages),
            timeout=180
        )

    except asyncio.TimeoutError:

        logger.error(
            "Agent timeout | conversation_id=%s",
            conversation_id,
        )

        raise HTTPException(
            status_code=504,
            detail="AI request timed out"
        )

    logger.info(
    "Agent completed | request_id=%s | conversation_id=%s",
    get_request_id(),
    conversation_id,
)

    # Save assistant response
    save_message(
        session,
        "assistant",
        answer,
        conversation.id
    )

    # Update conversation memory
    try:
        await maybe_summarize_conversation(
            session=session,
            conversation=conversation,
            max_messages=MAX_HISTORY_MESSAGES,
            keep_recent=RECENT_MESSAGES,
    )
    except Exception:
        logger.exception(
            "Conversation memory update failed | "
            "request_id=%s | conversation_id=%s",
            get_request_id(),
            conversation_id,
    )

    logger.info(
    "Chat request started | request_id=%s | user_id=%s | conversation_id=%s",
    get_request_id(),
    user_id,
    conversation_id,
)

# ==========================================
# 3. Streaming Chat
# ==========================================

async def stream_process_chat(
    session: Session,
    conversation_id: int,
    user_id: int,
    user_message: str
):

    logger.info(
        "Streaming chat request started | "
        "user_id=%s | conversation_id=%s",
        user_id,
        conversation_id,
    )

    # Verify conversation ownership
    conversation = get_conversation_for_user(
        session,
        conversation_id,
        user_id
    )

    if conversation is None:
        logger.warning(
            "Streaming conversation not found or unauthorized | "
            "user_id=%s | conversation_id=%s",
            user_id,
            conversation_id,
        )

        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    # Build conversation context
    messages = build_conversation_context(
        session,
        conversation
    )

    # Add new user message
    messages.append({
        "role": "user",
        "content": user_message
    })

    # Save user message
    save_message(
        session,
        "user",
        user_message,
        conversation.id
    )

    logger.info(
        "Starting streaming agent | conversation_id=%s",
        conversation_id,
    )

    # Streaming generator
    async def generate():

        answer_parts = []
        completed = False

        try:

            # Maximum agent execution time
            async with asyncio.timeout(180):

                async for chunk in stream_agent(messages):

                    answer_parts.append(chunk)

                    yield chunk

            completed = True

        except asyncio.TimeoutError:

            logger.error(
                "Streaming agent timeout | conversation_id=%s",
                conversation_id,
            )

            yield "\nAI request timed out."

        except Exception:

            logger.exception(
                "Streaming agent failed | conversation_id=%s",
                conversation_id,
            )

            yield "\nAI request failed."

        # Save only completed assistant responses
        if completed:

            full_answer = "".join(answer_parts)

            save_message(
                session,
                "assistant",
                full_answer,
                conversation.id
            )

            logger.info(
                "Streaming agent completed | "
                "conversation_id=%s | response_length=%s",
                conversation_id,
                len(full_answer),
            )

            # Update conversation memory
                        # Update conversation memory without invalidating
            # an already-saved assistant response.
            try:
                await maybe_summarize_conversation(
                    session=session,
                    conversation=conversation,
                    max_messages=MAX_HISTORY_MESSAGES,
                    keep_recent=RECENT_MESSAGES,
                )
            except Exception:
                logger.exception(
                    "Streaming memory update failed | "
                    "request_id=%s | conversation_id=%s",
                    get_request_id(),
                    conversation_id,
                )

            logger.info(
                "Streaming chat request completed | "
                "user_id=%s | conversation_id=%s",
                user_id,
                conversation_id,
            )

    return generate()


# This is now the version to keep as your `chat_service.py`.

# One small design choice: I deliberately **don't log `user_message` or the generated answer**, because production logs shouldn't casually contain potentially sensitive conversation data. We log IDs, lifecycle events, failures, and response length instead.
