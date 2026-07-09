import logging
from fastapi import APIRouter, HTTPException
from app.schemas import QueryRequest, QueryResponse
from app.services.query_service import answer_question, QueryError

logger = logging.getLogger(__name__)
router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
async def query(payload: QueryRequest) -> QueryResponse:
    try:
        result = answer_question(payload)
    except QueryError as exc:
        logger.error("query_failed", extra={"route": "/query"})
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("query_unexpected_error", extra={"route": "/query", "error_type": type(exc).__name__})
        raise HTTPException(status_code=500, detail="Unexpected error answering question") from exc

    return QueryResponse(**result)
