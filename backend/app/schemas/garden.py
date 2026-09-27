from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class PlantCatalogItem(BaseModel):
    id: UUID
    species: str
    name: str
    description: str
    unlock_cost: int
    is_unlocked: bool
    is_selected: bool


class GardenStateResponse(BaseModel):
    water_balance: int = 0
    leaves_balance: int = 0
    selected_plant_id: UUID | None = None
    growth_points: int = Field(default=0, ge=0)
    growth_stage: Literal["SPROUTING", "GROWING", "BLOOMING", "FLOURISHING"] = (
        "SPROUTING"
    )
    vitality: int = 100
    catalog: list[PlantCatalogItem]


class WaterPlantRequest(BaseModel):
    operation_key: UUID

class WaterPlantResponse(BaseModel):
    water_balance: int
    last_watered_at: datetime
    vitality: int
