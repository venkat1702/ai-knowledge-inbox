import logging
from fastapi import APIRouter, HTTPException
from app.schemas import ItemListResponse
from app.services.ingestion_service import list_items

logger = logging.getLogger(__name__)
router = APIRouter(tags=["items"])


@router.get("/items", response_model=ItemListResponse)
async def get_items() -> ItemListResponse:
    try:
        items = list_items()
    except Exception as exc:
        logger.error("list_items_failed", extra={"route": "/items", "error_type": type(exc).__name__})
        raise HTTPException(status_code=500, detail="Failed to load items") from exc

    return ItemListResponse(items=items, count=len(items))
