import logging
from fastapi import APIRouter, HTTPException
from app.schemas import IngestRequest, IngestResponse
from app.services.ingestion_service import ingest_item, IngestionError

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ingest"])


@router.post("/ingest", response_model=IngestResponse, status_code=201)
async def ingest(payload: IngestRequest) -> IngestResponse:
    try:
        result = await ingest_item(payload)
    except IngestionError as exc:
        # Bad/unreachable URL or unusable content -> client error, not server error
        logger.warning("ingest_rejected", extra={"route": "/ingest"})
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("ingest_unexpected_error", extra={"route": "/ingest", "error_type": type(exc).__name__})
        raise HTTPException(status_code=502, detail="Upstream embedding/vector store failure") from exc

    return IngestResponse(**result)
