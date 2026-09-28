from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.ai.llm.providers import llm_provider
from app.core.config import settings
from app.db.session import engine
from app.db.session import AsyncSessionLocal


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    llm_provider.init_client()
    try:
        from app.ai.llm.budget import cleanup_usage_logs

        async with AsyncSessionLocal() as cleanup_session:
            await cleanup_usage_logs(cleanup_session)
            await cleanup_session.commit()
    except Exception as exc:
        # Retention maintenance is best-effort and must not make the API
        # unavailable. Only the exception type is logged; no payload exists in
        # this table and no database URL is exposed.
        logging.getLogger(__name__).warning(
            "ai_usage_cleanup_failed", extra={"error_type": type(exc).__name__}
        )
    try:
        yield
    finally:
        await llm_provider.close_client()
        await engine.dispose()


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def _cors_headers_for(request: Request) -> dict[str, str]:
    """Keep unexpected error responses readable by approved frontends.

    Starlette's server-error middleware sits outside middleware registered via
    ``add_middleware``. Without explicit headers here, a browser masks a JSON
    500 response as a generic CORS/network failure.
    """
    origin = request.headers.get("origin")
    if origin not in settings.FRONTEND_URLS:
        return {}
    return {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Credentials": "true",
        "Vary": "Origin",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("transaction_failure")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers=_cors_headers_for(request),
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_URLS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)
