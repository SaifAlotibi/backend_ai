from .embeddings import model
from .vector_store import search_index


def retrieve(
    query: str,
    index,
    chunks,
    k: int = 3,
    min_similarity: float = 0.4
):

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )[0]

    scores, indices = search_index(
        index,
        query_embedding,
        k
    )

    results = []

    for score, index_id in zip(
        scores,
        indices
    ):

        if index_id == -1:
            continue

        if score < min_similarity:
            continue

        chunk = chunks[index_id]

        results.append({
            "text": chunk["text"],
            "page": chunk["page"],
            "source": "company_handbook.pdf",
            "score": float(score)
        })

    return results