import logging
import time

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.services.vectorstore import VectorMatch

logger = logging.getLogger(__name__)
_settings = get_settings()
genai.configure(api_key=_settings.google_api_key)

_SYSTEM_INSTRUCTION = (
    "You are a precise research assistant answering questions using ONLY the "
    "provided context snippets from the user's saved notes and pages. "
    "Rules:\n"
    "1. Answer only from the given context. Do not use outside knowledge.\n"
    "2. If the context does not contain enough information to answer, say so "
    "plainly instead of guessing.\n"
    "3. Refer to sources by their [number] as given in the context.\n"
    "4. Be concise and direct."
)


class LLMError(Exception):
    """Raised when the LLM provider fails after retries."""


def _build_prompt(question: str, matches: list[VectorMatch]) -> str:
    context_blocks = []
    for i, match in enumerate(matches, start=1):
        label = match.title or match.item_id
        context_blocks.append(f"[{i}] Source: {label}\n{match.chunk_text}")
    context_str = (
        "\n\n".join(context_blocks) if context_blocks else "(no matching context found)"
    )

    return (
        f"Context snippets:\n\n{context_str}\n\n"
        f"Question: {question}\n\n"
        "Answer the question using only the context above, citing snippet "
        "numbers like [1] where relevant."
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
def _generate(prompt: str) -> str:

    start = time.perf_counter()

    model = genai.GenerativeModel(
        model_name=_settings.gemini_llm_model,
        system_instruction=_SYSTEM_INSTRUCTION,
    )

    response = model.generate_content(prompt)

    logger.info(
        "gemini_api_call_complete",
        extra={
            "duration_ms": round(
                (time.perf_counter() - start) * 1000,
                2,
            ),
            "prompt_chars": len(prompt),
        },
    )

    if not response.text:
        raise LLMError("Empty response from LLM")

    return response.text.strip()


def generate_answer(question: str, matches: list[VectorMatch]) -> str:
    prompt = _build_prompt(question, matches)
    try:
        return _generate(prompt)
    except Exception as exc:
        logger.error("llm_generation_failed", extra={"error_type": type(exc).__name__})
        raise LLMError(f"Failed to generate answer: {exc}") from exc
