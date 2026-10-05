from rag.pipeline import RAGPipeline


rag = RAGPipeline(
    "documents"
)


def search_knowledge(query: str):

    results = rag.search(
        query,
        k=3,
        min_similarity=0.4
    )

    if not results:
        return "No relevant information was found."

    formatted_results = []

    for i, result in enumerate(
        results,
        start=1
    ):

        formatted_results.append(
            f"Source {i}\n"
            f"Document: {result['source']}\n"
            f"Page: {result['page']}\n"
            f"Similarity: {result['score']:.4f}\n"
            f"Content:\n{result['text']}"
        )

    return "\n\n".join(
        formatted_results
    )