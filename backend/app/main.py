import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import init_db
from app.logging_config import configure_logging
from app.routers import ingest, items, query
from app.services.vectorstore import ensure_index

configure_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup_begin")
    init_db()
    ensure_index()
    logger.info("startup_complete")
    yield
    logger.info("shutdown")


app = FastAPI(
    title="AI Knowledge Inbox",
    description="Save notes/URLs, ask questions, get RAG-powered answers with cited sources.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    """Attaches a request_id + timing to every access log line for traceability."""
    request_id = str(uuid.uuid4())
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "request_completed",
        extra={
            "request_id": request_id,
            "route": request.url.path,
            "duration_ms": duration_ms,
            "status_code": response.status_code,
        },
    )
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("validation_error", extra={"route": request.url.path})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "validation_error", "detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(
        "unhandled_exception",
        extra={"route": request.url.path, "error_type": type(exc).__name__},
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_server_error",
            "detail": "An unexpected error occurred",
        },
    )


app.include_router(ingest.router)
app.include_router(items.router)
app.include_router(query.router)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
