import re


def tokenize(text: str):

    return set(
        re.findall(
            r"\b\w+\b",
            text.lower()
        )
    )


def lexical_score(
    query: str,
    text: str
):

    query_tokens = tokenize(query)
    text_tokens = tokenize(text)

    if not query_tokens:
        return 0.0

    matching_tokens = (
        query_tokens & text_tokens
    )

    return (
        len(matching_tokens)
        / len(query_tokens)
    )


def rerank(
    query: str,
    results,
    semantic_weight: float = 0.7,
    lexical_weight: float = 0.3
):

    for result in results:

        lexical = lexical_score(
            query,
            result["text"]
        )

        semantic = result["score"]

        result["lexical_score"] = lexical

        result["rerank_score"] = (
            semantic * semantic_weight
            + lexical * lexical_weight
        )

    results.sort(
        key=lambda result:
            result["rerank_score"],
        reverse=True
    )

    return results