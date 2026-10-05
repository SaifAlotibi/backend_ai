import faiss
import numpy as np


def create_index(embeddings):

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(embeddings)

    return index


def search_index(
    index,
    query_embedding,
    k=3
):

    query_embedding = np.asarray(
        [query_embedding],
        dtype="float32"
    )

    scores, indices = index.search(
        query_embedding,
        k
    )

    return scores[0], indices[0]


def save_index(
    index,
    path: str
):

    faiss.write_index(
        index,
        path
    )


def load_index(
    path: str
):

    return faiss.read_index(
        path
    )