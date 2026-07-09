import sqlite3
import os
from contextlib import contextmanager
from pathlib import Path
from app.config import get_settings

_settings = get_settings()


def _ensure_parent_dir(path: str) -> None:
    parent = Path(path).parent
    if str(parent) not in ("", "."):
        os.makedirs(parent, exist_ok=True)


@contextmanager
def get_connection():
    _ensure_parent_dir(_settings.sqlite_db_path)
    conn = sqlite3.connect(_settings.sqlite_db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY,
                source_type TEXT NOT NULL CHECK (source_type IN ('text', 'url')),
                title TEXT,
                source_url TEXT,
                raw_content TEXT NOT NULL,
                chunk_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                item_id TEXT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
                chunk_index INTEGER NOT NULL,
                chunk_text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_item_id ON chunks(item_id)")
