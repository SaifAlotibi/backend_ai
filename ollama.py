import asyncio
import logging
import random
import time
import json

from circuit_breaker import circuit_breaker
import httpx
from fastapi import HTTPException
from opentelemetry import trace

from config import OLLAMA_URL, MODEL_NAME


logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

MAX_RETRIES = 3
BASE_DELAY = 1

async def chat_with_ollama(messages, tools=None, format=None):
    """Send a non-streaming chat request to Ollama."""
    if not circuit_breaker.allow_request():
        logger.warning("Circuit breaker is OPEN | Ollama request rejected")
        raise HTTPException(
            status_code=503,
            detail="AI service temporarily unavailable",
        )

    url = f"{OLLAMA_URL}/api/chat"
    data = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
    }

    if tools:
        data["tools"] = tools

    if format:
        data["format"] = format

    with tracer.start_as_current_span("ollama.chat") as span:
        start_time = time.perf_counter()
        span.set_attribute("llm.provider", "ollama")
        span.set_attribute("llm.model", MODEL_NAME)
        span.set_attribute("llm.max_retries", MAX_RETRIES)

        for attempt in range(MAX_RETRIES):
            try:
                logger.info(
                    "LLM request attempt | model=%s | attempt=%s/%s",
                    MODEL_NAME,
                    attempt + 1,
                    MAX_RETRIES,
                )

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url,
                        json=data,
                        timeout=120,
                    )
                    response.raise_for_status()
                    result = response.json()

                elapsed = time.perf_counter() - start_time
                span.set_attribute("llm.latency_seconds", elapsed)
                span.set_attribute("llm.attempts", attempt + 1)

                logger.info(
                    "LLM request completed | model=%s | attempts=%s | latency=%.3fs",
                    MODEL_NAME,
                    attempt + 1,
                    elapsed,
                )
                return result

            except (httpx.ConnectError, httpx.TimeoutException) as exc:
                if attempt == MAX_RETRIES - 1:
                    span.record_exception(exc)
                    span.set_status(
                        trace.Status(
                            trace.StatusCode.ERROR,
                            "Ollama request failed after retries",
                        )
                    )
                    logger.exception(
                        "Ollama request failed after %s attempts",
                        MAX_RETRIES,
                    )
                    raise HTTPException(
                        status_code=503,
                        detail="AI service unavailable",
                    ) from exc

                delay = BASE_DELAY * (2 ** attempt)
                total_delay = delay + random.uniform(0, 0.5)

                logger.warning(
                    "Ollama request failed | attempt=%s/%s | retrying in %.2fs",
                    attempt + 1,
                    MAX_RETRIES,
                    total_delay,
                )
                await asyncio.sleep(total_delay)

            except httpx.HTTPStatusError as exc:
                span.record_exception(exc)
                span.set_status(
                    trace.Status(
                        trace.StatusCode.ERROR,
                        "Ollama returned an HTTP error",
                    )
                )
                logger.exception(
                    "Ollama returned HTTP error | status=%s",
                    exc.response.status_code,
                )
                raise HTTPException(
                    status_code=503,
                    detail=f"Ollama returned an error: {exc.response.status_code}",
                ) from exc

async def stream_chat_with_ollama(messages, tools=None, format=None):

    """Stream newline-delimited JSON responses from Ollama."""
    if not circuit_breaker.allow_request():
        logger.warning("Circuit breaker is OPEN | Ollama stream rejected")
        raise HTTPException(
            status_code=503,
            detail="AI service temporarily unavailable",
        )

    url = f"{OLLAMA_URL}/api/chat"
    data = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": True,
    }

    if tools:
        data["tools"] = tools

    if format:
        data["format"] = format

    with tracer.start_as_current_span("ollama.stream") as span:
        start_time = time.perf_counter()
        span.set_attribute("llm.provider", "ollama")
        span.set_attribute("llm.model", MODEL_NAME)
        span.set_attribute("llm.max_retries", MAX_RETRIES)

        for attempt in range(MAX_RETRIES):
            received_chunk = False

            try:
                logger.info(
                    "LLM stream attempt | model=%s | attempt=%s/%s",
                    MODEL_NAME,
                    attempt + 1,
                    MAX_RETRIES,
                )

                async with httpx.AsyncClient() as client:
                    async with client.stream(
                        "POST",
                        url,
                        json=data,
                        timeout=120,
                    ) as response:
                        response.raise_for_status()

                        async for line in response.aiter_lines():
                            if not line.strip():
                                continue

                            chunk = json.loads(line)
                            received_chunk = True
                            yield line

                            if chunk.get("done", False):
                                elapsed = time.perf_counter() - start_time
                                span.set_attribute(
                                    "llm.latency_seconds", elapsed
                                )
                                span.set_attribute(
                                    "llm.attempts", attempt + 1
                                )
                                logger.info(
                                    "LLM stream completed | model=%s | "
                                    "attempts=%s | latency=%.3fs",
                                    MODEL_NAME,
                                    attempt + 1,
                                    elapsed,
                                )
                                return

                # A cleanly closed stream without a done marker is unexpected.
                raise HTTPException(
                    status_code=502,
                    detail="Ollama stream ended unexpectedly",
                )

            except (httpx.ConnectError, httpx.TimeoutException) as exc:
                if received_chunk or attempt == MAX_RETRIES - 1:
                    span.record_exception(exc)
                    span.set_status(
                        trace.Status(
                            trace.StatusCode.ERROR,
                            "Ollama stream failed",
                        )
                    )
                    logger.exception(
                        "Ollama stream failed | attempt=%s/%s",
                        attempt + 1,
                        MAX_RETRIES,
                    )
                    raise HTTPException(
                        status_code=503,
                        detail="AI streaming service unavailable",
                    ) from exc

                delay = BASE_DELAY * (2 ** attempt)
                total_delay = delay + random.uniform(0, 0.5)

                logger.warning(
                    "Ollama stream connection failed | "
                    "attempt=%s/%s | retrying in %.2fs",
                    attempt + 1,
                    MAX_RETRIES,
                    total_delay,
                )
                await asyncio.sleep(total_delay)

            except httpx.HTTPStatusError as exc:
                span.record_exception(exc)
                span.set_status(
                    trace.Status(
                        trace.StatusCode.ERROR,
                        "Ollama returned an HTTP error",
                    )
                )
                logger.exception(
                    "Ollama stream HTTP error | status=%s",
                    exc.response.status_code,
                )
                raise HTTPException(
                    status_code=503,
                    detail=(
                        "Ollama returned an error: "
                        f"{exc.response.status_code}"
                    ),
                ) from exc
