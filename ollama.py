import httpx

from fastapi import HTTPException

from config import OLLAMA_URL, MODEL_NAME


async def chat_with_ollama(
    messages,
    tools=None
):
    url = f"{OLLAMA_URL}/api/chat"

    data = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False
    }

    if tools:
        data["tools"] = tools

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=data,
                timeout=120
            )

            response.raise_for_status()

            return response.json()

    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="AI service unavailable"
        )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=503,
            detail="AI service timed out"
        )