import logging
import time
from uuid import uuid4

from fastapi import Request

from app.core.logging import request_id_context

logger = logging.getLogger(__name__)


async def request_logging(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    context_token = request_id_context.set(request_id)
    started = time.perf_counter()
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request_completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            },
        )
        return response
    finally:
        request_id_context.reset(context_token)
