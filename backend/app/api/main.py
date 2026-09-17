from fastapi import APIRouter

from app.api.routes import (
    assistant,
    auth,
    focus,
    garden,
    goals,
    health,
    planning,
    statistics,
    today,
    user_settings,
    users,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(user_settings.router)
api_router.include_router(assistant.router)
api_router.include_router(planning.router)
api_router.include_router(focus.router)
api_router.include_router(goals.router)
api_router.include_router(garden.router)
api_router.include_router(today.router)
api_router.include_router(statistics.router)
