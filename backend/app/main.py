from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.api.main import api_router
from app.core.config import settings
from app.db.session import engine


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    yield
    await engine.dispose()


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
