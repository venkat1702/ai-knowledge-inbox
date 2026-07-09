import logging

from app.config import get_settings
from app.schemas import QueryRequest, SourceSnippet
from app.services import embeddings, llm, vectorstore

logger = logging.getLogger(__name__)
_settings = get_settings()


class QueryError(Exception):
    """Raised for any failure during the query pipeline."""


def answer_question(payload: QueryRequest) -> dict:
    top_k = payload.top_k or _settings.default_top_k

    try:
        query_vector = embeddings.embed_query(payload.question)
    except Exception as exc:
        raise QueryError(f"Failed to embed question: {exc}") from exc

    try:
        raw_matches = vectorstore.query(query_vector, top_k=top_k)
    except Exception as exc:
        raise QueryError(f"Failed to search vector store: {exc}") from exc

    # Pinecone always returns the top_k *nearest* vectors, even if none are
    # actually relevant -- similarity search has no built-in "no match"
    # concept. We filter out weak matches ourselves so an unrelated question
    # doesn't get answered from (or cite) barely-related chunks.
    matches = [m for m in raw_matches if m.score >= 0.65]

    if raw_matches and not matches:
        logger.info(
            "query_matches_below_threshold",
            extra={"route": "/query"},
        )

    if not matches:
        logger.info("query_no_matches", extra={"route": "/query"})
        return {
            "answer": "No saved content is relevant enough to answer this question. "
            "Try rephrasing, or add notes/URLs covering this topic.",
            "sources": [],
            "retrieved_chunk_count": 0,
        }

    try:
        answer_text = llm.generate_answer(payload.question, matches)
    except Exception as exc:
        raise QueryError(f"Failed to generate answer: {exc}") from exc

    sources = [
        SourceSnippet(
            item_id=m.item_id,
            title=m.title,
            chunk_index=m.chunk_index,
            chunk_text=m.chunk_text,
            score=round(m.score, 4),
        )
        for m in matches
    ]

    logger.info("query_answered", extra={"route": "/query"})

    return {
        "answer": answer_text,
        "sources": sources,
        "retrieved_chunk_count": len(matches),
    }
