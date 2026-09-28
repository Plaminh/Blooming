from fastapi import APIRouter
from uuid import UUID

from app.api.deps import SessionDep, CurrentUser
from app.schemas.garden import (
    GardenStateResponse,
    WaterPlantResponse,
    WaterPlantRequest,
)
from app.services import garden_service

router = APIRouter(prefix="/garden", tags=["garden"])


@router.get("", response_model=GardenStateResponse)
async def get_garden(db: SessionDep, current_user: CurrentUser):
    return await garden_service.get_garden_state(db, current_user.id)


@router.post("/plants/{plant_id}/unlock", response_model=GardenStateResponse)
async def unlock_plant(plant_id: UUID, db: SessionDep, current_user: CurrentUser):
    return await garden_service.unlock_plant(db, current_user.id, plant_id)


@router.post("/plants/{plant_id}/select", response_model=GardenStateResponse)
async def select_plant(plant_id: UUID, db: SessionDep, current_user: CurrentUser):
    return await garden_service.select_plant(db, current_user.id, plant_id)


@router.post("/water", response_model=WaterPlantResponse)
async def water_plant(
    request: WaterPlantRequest, db: SessionDep, current_user: CurrentUser
):
    return await garden_service.water_plant(db, current_user.id, request.operation_key)
