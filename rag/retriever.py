import logging

from opentelemetry import trace

from .embeddings import create_query_embedding
from .vector_store import search_index
from .reranker import rerank


logger = logging.getLogger(__name__)

tracer = trace.get_tracer(__name__)


def retrieve(
    query: str,
    index,
    chunks,
    k: int = 3,
    min_similarity: float = 0.4,
):

    # ==========================================
    # Main RAG Span
    # ==========================================

    with tracer.start_as_current_span(
        "rag.retrieve"
    ) as rag_span:

        candidate_k = min(
            k * 3,
            len(chunks)
        )

        rag_span.set_attribute(
            "rag.top_k",
            k
        )

        rag_span.set_attribute(
            "rag.candidate_k",
            candidate_k
        )

        rag_span.set_attribute(
            "rag.min_similarity",
            min_similarity
        )

        # ==========================================
        # Query Embedding
        # ==========================================

        with tracer.start_as_current_span(
            "rag.embed_query"
        ) as embedding_span:

            query_embedding = create_query_embedding(
                query
            )

            embedding_span.set_attribute(
                "rag.embedding_model",
                "nomic-embed-text"
            )

        # ==========================================
        # Vector Search
        # ==========================================

        with tracer.start_as_current_span(
            "rag.vector_search"
        ) as search_span:

            scores, indices = search_index(
                index,
                query_embedding,
                candidate_k
            )

            search_span.set_attribute(
                "rag.candidate_count",
                candidate_k
            )

        # ==========================================
        # Build Candidates
        # ==========================================

        candidates = []

        for score, index_id in zip(
            scores,
            indices
        ):

            if index_id == -1:
                continue

            if score < min_similarity:
                continue

            chunk = chunks[index_id]

            candidates.append(
                {
                    "text": chunk["text"],
                    "page": chunk["page"],
                    "source": chunk["source"],
                    "score": float(score),
                }
            )

        rag_span.set_attribute(
            "rag.filtered_candidates",
            len(candidates)
        )

        # ==========================================
        # Reranking
        # ==========================================

        with tracer.start_as_current_span(
            "rag.rerank"
        ) as rerank_span:

            candidates = rerank(
                query,
                candidates
            )

            rerank_span.set_attribute(
                "rag.reranked_count",
                len(candidates)
            )

        results = candidates[:k]

        # ==========================================
        # Final RAG Metrics
        # ==========================================

        rag_span.set_attribute(
            "rag.results",
            len(results)
        )

        logger.info(
            "RAG retrieval completed | "
            "results=%s | candidates=%s",
            len(results),
            len(candidates),
        )

        return results