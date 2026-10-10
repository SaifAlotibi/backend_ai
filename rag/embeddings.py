import httpx
import numpy as np

from config import (
    OLLAMA_URL,
    EMBEDDING_MODEL
)


def normalize_embeddings(
    embeddings: np.ndarray
):
    norms = np.linalg.norm(
        embeddings,
        axis=1,
        keepdims=True
    )

    return embeddings / np.maximum(
        norms,
        1e-12
    )


def create_embeddings(
    texts: list[str]
):

    if not texts:
        return np.empty(
            (0, 0),
            dtype="float32"
        )

    embeddings = []

    with httpx.Client(
        timeout=120
    ) as client:

        for text in texts:

            response = client.post(
                f"{OLLAMA_URL}/api/embed",
                json={
                    "model": EMBEDDING_MODEL,
                    "input": text
                }
            )

            response.raise_for_status()

            data = response.json()

            embeddings.append(
                data["embeddings"][0]
            )

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    return normalize_embeddings(
        embeddings
    )


def create_query_embedding(
    query: str
):

    with httpx.Client(
        timeout=120
    ) as client:

        response = client.post(
            f"{OLLAMA_URL}/api/embed",
            json={
                "model": EMBEDDING_MODEL,
                "input": query
            }
        )

        response.raise_for_status()

        data = response.json()

        embedding = np.asarray(
            data["embeddings"][0],
            dtype="float32"
        )

    embedding = embedding.reshape(
        1,
        -1
    )

    embedding = normalize_embeddings(
        embedding
    )

    return embedding[0]