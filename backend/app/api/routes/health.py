import logging

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import SessionDep
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "blooming-api"}


@router.get("/db")
async def health_db(session: SessionDep) -> dict[str, str]:
    try:
        await session.execute(select(1))
    except SQLAlchemyError as exc:
        # Driver errors can carry host/user details, so only the type is logged.
        logger.error("Database health check failed: %s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unavailable",
        ) from None
    return {"status": "ok", "database": "reachable"}


@router.get("/ready")
async def health_ready(session: SessionDep) -> dict[str, str]:
    try:
        version = await session.scalar(
            text("SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1")
        )
    except SQLAlchemyError as exc:
        logger.error("readiness_database_unavailable", extra={"error_type": type(exc).__name__})
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="service not ready",
        ) from None
    if version != settings.LATEST_SCHEMA_MIGRATION:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database migrations are not current",
        )
    return {
        "status": "ready",
        "database": "reachable",
        "migration": str(version),
        "build": settings.GIT_SHA,
    }
