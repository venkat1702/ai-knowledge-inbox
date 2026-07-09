import logging
from dataclasses import dataclass

from pinecone import Pinecone, ServerlessSpec

from app.config import get_settings

logger = logging.getLogger(__name__)
_settings = get_settings()

_pc = Pinecone(api_key=_settings.pinecone_api_key)


@dataclass
class VectorMatch:
    chunk_id: str
    score: float
    item_id: str
    title: str | None
    chunk_index: int
    chunk_text: str


def ensure_index() -> None:
    """Create the Pinecone index on startup if it doesn't already exist."""
    existing = {idx["name"] for idx in _pc.list_indexes()}
    if _settings.pinecone_index_name in existing:
        return
    logger.info(
        "creating_pinecone_index",
        extra={"route": "startup"},
    )
    _pc.create_index(
        name=_settings.pinecone_index_name,
        dimension=_settings.embedding_dimensions,
        metric="cosine",
        spec=ServerlessSpec(
            cloud=_settings.pinecone_cloud, region=_settings.pinecone_region
        ),
    )


def _get_index():
    return _pc.Index(_settings.pinecone_index_name)


def upsert_chunks(
    item_id: str,
    title: str | None,
    chunks: list[str],
    embeddings: list[list[float]],
) -> None:
    if len(chunks) != len(embeddings):
        raise ValueError("chunks and embeddings length mismatch")
    if not chunks:
        return

    index = _get_index()
    vectors = []
    for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
        vectors.append(
            {
                "id": f"{item_id}::{i}",
                "values": vector,
                "metadata": {
                    "item_id": item_id,
                    "title": title or "",
                    "chunk_index": i,
                    # Storing chunk_text in metadata avoids a second round-trip
                    # to SQLite on the query path. Fine at this scale; see
                    # README "what breaks at scale" for the tradeoff.
                    "chunk_text": chunk,
                },
            }
        )
    index.upsert(vectors=vectors)


def query(vector: list[float], top_k: int) -> list[VectorMatch]:
    index = _get_index()
    result = index.query(vector=vector, top_k=top_k, include_metadata=True)
    matches: list[VectorMatch] = []
    for match in result.get("matches", []):
        metadata = match.get("metadata", {}) or {}
        matches.append(
            VectorMatch(
                chunk_id=match["id"],
                score=match["score"],
                item_id=metadata.get("item_id", ""),
                title=metadata.get("title") or None,
                chunk_index=metadata.get("chunk_index", -1),
                chunk_text=metadata.get("chunk_text", ""),
            )
        )
    return matches
