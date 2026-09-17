from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

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
    vitality: int = 100
    catalog: list[PlantCatalogItem]

class WaterPlantResponse(BaseModel):
    water_balance: int
    last_watered_at: datetime
    vitality: int
