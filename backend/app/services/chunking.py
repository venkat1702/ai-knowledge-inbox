from app.config import get_settings

_settings = get_settings()


def chunk_text(text: str, chunk_size_words: int | None = None, overlap_words: int | None = None) -> list[str]:
    chunk_size = chunk_size_words or _settings.chunk_size_words
    overlap = overlap_words if overlap_words is not None else _settings.chunk_overlap_words

    if chunk_size <= 0:
        raise ValueError("chunk_size_words must be > 0")
    if overlap >= chunk_size:
        raise ValueError("chunk_overlap_words must be smaller than chunk_size_words")

    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    step = chunk_size - overlap
    for start in range(0, len(words), step):
        window = words[start : start + chunk_size]
        if not window:
            break
        chunks.append(" ".join(window))
        if start + chunk_size >= len(words):
            break
    return chunks
