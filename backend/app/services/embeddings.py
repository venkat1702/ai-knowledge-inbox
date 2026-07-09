import logging

import google.generativeai as genai
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import get_settings

logger = logging.getLogger(__name__)
_settings = get_settings()
genai.configure(api_key=_settings.google_api_key)


class EmbeddingError(Exception):
    """Raised when the embedding provider fails after retries."""


_RETRYABLE = (
    Exception,
)  # network/5xx errors from the SDK don't have a stable base class

_RETRY_CONFIG = dict(
    stop=stop_after_attempt(2),  # 1 retry only, was 3
    wait=wait_exponential(multiplier=1, min=1, max=3),  # capped at 3s, was 8s
    retry=retry_if_exception_type(_RETRYABLE),
    reraise=True,
)


@retry(**_RETRY_CONFIG)
def _embed_batch(texts: list[str], task_type: str) -> list[list[float]]:
    result = genai.embed_content(
        model=_settings.gemini_embedding_model,
        content=texts,
        task_type=task_type,
        output_dimensionality=_settings.embedding_dimensions,
    )
    return result["embedding"]


@retry(**_RETRY_CONFIG)
def _embed_single(text: str, task_type: str) -> list[float]:
    result = genai.embed_content(
        model=_settings.gemini_embedding_model,
        content=text,
        task_type=task_type,
        output_dimensionality=_settings.embedding_dimensions,
    )
    return result["embedding"]


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Embed a batch of chunk texts for storage, in a single API call."""
    if not texts:
        return []
    try:
        return _embed_batch(texts, task_type="retrieval_document")
    except Exception as exc:
        logger.error("embedding_failed", extra={"error_type": type(exc).__name__})
        raise EmbeddingError(f"Failed to embed content: {exc}") from exc


def embed_query(text: str) -> list[float]:
    """Embed a user question for retrieval."""
    try:
        return _embed_single(text, task_type="retrieval_query")
    except Exception as exc:
        logger.error("query_embedding_failed", extra={"error_type": type(exc).__name__})
        raise EmbeddingError(f"Failed to embed query: {exc}") from exc
