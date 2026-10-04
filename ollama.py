import httpx

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

    async with httpx.AsyncClient() as client:

        response = await client.post(
            url,
            json=data,
            timeout=120
        )

        response.raise_for_status()

        return response.json()