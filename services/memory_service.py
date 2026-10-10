import logging

from opentelemetry import trace
from sqlmodel import Session

from database import Conversation
from repositories.message_repository import get_messages
from ollama import chat_with_ollama


logger = logging.getLogger(__name__)

tracer = trace.get_tracer(__name__)


# ==========================================
# Summarize Conversation
# ==========================================

async def summarize_conversation(
    session: Session,
    conversation: Conversation,
    messages,
):

    request_span = trace.get_current_span()

    if not messages:
        return conversation.summary

    # ==========================================
    # Memory Summarization Span
    # ==========================================

    with tracer.start_as_current_span(
        "memory.summarize"
    ) as span:

        span.set_attribute(
            "conversation.id",
            conversation.id,
        )

        span.set_attribute(
            "memory.messages_count",
            len(messages),
        )

        conversation_text = "\n".join(
            f"{message.role}: {message.content}"
            for message in messages
        )

        summary_prompt = [
            {
                "role": "system",
                "content": (
                    "Update the conversation summary using "
                    "the existing summary and the new messages. "
                    "Keep important facts, user preferences, "
                    "goals, decisions, and useful context. "
                    "Do not invent information."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Existing summary:\n"
                    f"{conversation.summary or 'None'}\n\n"
                    f"New messages to incorporate:\n"
                    f"{conversation_text}"
                ),
            },
        ]

        logger.info(
            "Conversation summarization started | "
            "conversation_id=%s | messages=%s",
            conversation.id,
            len(messages),
        )

        try:

            response = await chat_with_ollama(
                summary_prompt
            )

            summary = (
                response["message"]
                .get("content", "")
                .strip()
            )

            if summary:

                conversation.summary = summary

                conversation.summary_message_count += len(
                    messages
                )

                session.add(conversation)

                session.commit()

                session.refresh(conversation)

                span.set_attribute(
                    "memory.summary_updated",
                    True,
                )

                span.set_attribute(
                    "memory.summary_message_count",
                    conversation.summary_message_count,
                )

                logger.info(
                    "Conversation summary updated | "
                    "conversation_id=%s",
                    conversation.id,
                )

            else:

                span.set_attribute(
                    "memory.summary_updated",
                    False,
                )

                logger.warning(
                    "Conversation summarization returned empty summary | "
                    "conversation_id=%s",
                    conversation.id,
                )

            return conversation.summary

        except Exception as exc:

            span.record_exception(exc)

            span.set_status(
                trace.Status(
                    trace.StatusCode.ERROR,
                    str(exc),
                )
            )

            logger.exception(
                "Conversation summarization failed | "
                "conversation_id=%s",
                conversation.id,
            )

            raise


# ==========================================
# Maybe Summarize Conversation
# ==========================================

async def maybe_summarize_conversation(
    session: Session,
    conversation: Conversation,
    max_messages: int = 20,
    keep_recent: int = 10,
):

    # ==========================================
    # Memory Check Span
    # ==========================================

    with tracer.start_as_current_span(
        "memory.check"
    ) as span:

        span.set_attribute(
            "conversation.id",
            conversation.id,
        )

        span.set_attribute(
            "memory.max_messages",
            max_messages,
        )

        span.set_attribute(
            "memory.keep_recent",
            keep_recent,
        )

        messages = get_messages(
            session,
            conversation.id,
        )

        total_messages = len(messages)

        span.set_attribute(
            "memory.total_messages",
            total_messages,
        )

        # ==========================================
        # No Summarization Needed
        # ==========================================

        if total_messages <= max_messages:

            span.set_attribute(
                "memory.summarization_needed",
                False,
            )

            return conversation.summary

        # ==========================================
        # Find Messages Already Summarized
        # ==========================================

        summarized_count = (
            conversation.summary_message_count
        )

        old_messages_end = (
            total_messages - keep_recent
        )

        # ==========================================
        # Everything Already Summarized
        # ==========================================

        if summarized_count >= old_messages_end:

            span.set_attribute(
                "memory.summarization_needed",
                False,
            )

            return conversation.summary

        # ==========================================
        # Select New Old Messages
        # ==========================================

        new_old_messages = messages[
            summarized_count:old_messages_end
        ]

        if not new_old_messages:

            span.set_attribute(
                "memory.summarization_needed",
                False,
            )

            return conversation.summary

        # ==========================================
        # Summarize
        # ==========================================

        span.set_attribute(
            "memory.summarization_needed",
            True,
        )

        span.set_attribute(
            "memory.messages_to_summarize",
            len(new_old_messages),
        )

        logger.info(
            "Conversation summarization triggered | "
            "conversation_id=%s | "
            "total_messages=%s | "
            "messages_to_summarize=%s",
            conversation.id,
            total_messages,
            len(new_old_messages),
        )

    return await summarize_conversation(
        session=session,
        conversation=conversation,
        messages=new_old_messages,
    )