import logging
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_TIMEOUT_SECONDS = 15
_MAX_CONTENT_CHARS = 50_000  # guard against pathologically large pages
_STRIP_TAGS = ["script", "style", "nav", "footer", "header", "noscript", "svg", "form"]


class ScrapeError(Exception):
    """Raised when a URL cannot be fetched or contains no usable text."""


async def fetch_url_text(url: str) -> tuple[str, str | None]:
    """Returns (extracted_text, page_title)."""
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=_TIMEOUT_SECONDS) as client:
            response = await client.get(url, headers={"User-Agent": "AIKnowledgeInbox/1.0"})
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise ScrapeError(f"URL returned HTTP {exc.response.status_code}") from exc
    except httpx.RequestError as exc:
        raise ScrapeError(f"Failed to reach URL: {exc}") from exc

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type and "text/plain" not in content_type:
        raise ScrapeError(f"Unsupported content-type for scraping: {content_type or 'unknown'}")

    soup = BeautifulSoup(response.text, "html.parser")

    for tag_name in _STRIP_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else None

    text = soup.get_text(separator=" ")
    text = " ".join(text.split())  # collapse whitespace

    if not text:
        raise ScrapeError("No extractable text content found at URL")

    return text[:_MAX_CONTENT_CHARS], title
