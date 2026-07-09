import logging
import uuid
from datetime import datetime, timezone
from app.database import get_connection
from app.schemas import IngestRequest, SourceType
from app.services import chunking, embeddings, vectorstore
from app.services.scraper import fetch_url_text, ScrapeError

logger = logging.getLogger(__name__)


class IngestionError(Exception):
    """Raised for any failure during the ingest pipeline; carries an HTTP-friendly message."""


async def ingest_item(payload: IngestRequest) -> dict:
    item_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    source_url = None
    if payload.source_type == SourceType.url:
        try:
            raw_content, scraped_title = await fetch_url_text(payload.url)
        except ScrapeError as exc:
            logger.warning("url_fetch_failed", extra={"item_id": item_id})
            raise IngestionError(str(exc)) from exc
        source_url = payload.url
        title = payload.title or scraped_title or payload.url
    else:
        raw_content = payload.content
        title = payload.title

    chunks = chunking.chunk_text(raw_content)
    if not chunks:
        raise IngestionError("Content produced no chunks (empty after cleaning)")

    try:
        vectors = embeddings.embed_documents(chunks)
        vectorstore.upsert_chunks(item_id=item_id, title=title, chunks=chunks, embeddings=vectors)
    except Exception as exc:
        logger.error("ingestion_pipeline_failed", extra={"item_id": item_id, "error_type": type(exc).__name__})
        raise IngestionError(f"Failed to index content: {exc}") from exc

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO items (id, source_type, title, source_url, raw_content, chunk_count, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (item_id, payload.source_type.value, title, source_url, raw_content, len(chunks), created_at),
        )
        for i, chunk in enumerate(chunks):
            conn.execute(
                """
                INSERT INTO chunks (id, item_id, chunk_index, chunk_text, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (f"{item_id}::{i}", item_id, i, chunk, created_at),
            )

    logger.info(
        "item_ingested",
        extra={"item_id": item_id, "route": "/ingest"},
    )

    return {
        "id": item_id,
        "source_type": payload.source_type,
        "title": title,
        "chunk_count": len(chunks),
        "created_at": created_at,
    }


def list_items() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, source_type, title, source_url, raw_content, chunk_count, created_at "
            "FROM items ORDER BY created_at DESC"
        ).fetchall()

    items = []
    for row in rows:
        preview = row["raw_content"][:200]
        items.append(
            {
                "id": row["id"],
                "source_type": row["source_type"],
                "title": row["title"],
                "source_url": row["source_url"],
                "chunk_count": row["chunk_count"],
                "created_at": row["created_at"],
                "content_preview": preview + ("..." if len(row["raw_content"]) > 200 else ""),
            }
        )
    return items
