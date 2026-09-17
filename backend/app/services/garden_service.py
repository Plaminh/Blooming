from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.garden import GardenState, Plant, PlantOwnership, RewardEvent
from app.schemas.garden import GardenStateResponse, PlantCatalogItem, WaterPlantResponse
from app.core.economy import calculate_vitality, WATERING_COST
from fastapi import HTTPException

async def _ensure_garden_state(db: AsyncSession, user_id: UUID) -> GardenState:
    garden = await db.scalar(select(GardenState).where(GardenState.user_id == user_id))
    if not garden:
        garden = GardenState(user_id=user_id, water_balance=0, leaves_balance=0)
        db.add(garden)
        await db.commit()
        await db.refresh(garden)
    return garden

async def award_resources(
    db: AsyncSession, 
    user_id: UUID, 
    resource_type: str, 
    amount: int, 
    event_type: str, 
    idempotency_key: str, 
    source_id: UUID | None = None
) -> bool:
    """
    Awards resources to a user without committing.
    Returns True if awarded, False if idempotency key already exists.
    """
    existing = await db.scalar(select(RewardEvent).where(RewardEvent.idempotency_key == idempotency_key))
    if existing:
        return False
        
    garden = await db.scalar(select(GardenState).where(GardenState.user_id == user_id))
    if not garden:
        garden = GardenState(user_id=user_id, water_balance=0, leaves_balance=0)
        db.add(garden)
        
    if resource_type == "WATER":
        garden.water_balance += amount
    elif resource_type == "LEAVES":
        garden.leaves_balance += amount
        
    event = RewardEvent(
        user_id=user_id,
        event_type=event_type,
        resource_type=resource_type,
        amount=amount,
        idempotency_key=idempotency_key
    )
    if event_type == "FOCUS_COMPLETED":
        event.source_focus_run_id = source_id
    elif event_type == "MILESTONE_COMPLETED":
        event.source_milestone_id = source_id
        
    db.add(event)
    return True

async def get_garden_state(db: AsyncSession, user_id: UUID) -> GardenStateResponse:
    garden = await _ensure_garden_state(db, user_id)
    
    plants = (await db.scalars(select(Plant).where(Plant.is_active == True))).all()
    ownerships = (await db.scalars(select(PlantOwnership).where(PlantOwnership.user_id == user_id))).all()
    owned_ids = {o.plant_id for o in ownerships}
    
    catalog = []
    for p in plants:
        catalog.append(PlantCatalogItem(
            id=p.id,
            species=p.species,
            name=p.name,
            description=p.description,
            unlock_cost=p.unlock_cost,
            is_unlocked=p.id in owned_ids,
            is_selected=(p.id == garden.selected_plant_id)
        ))
        
    return GardenStateResponse(
        water_balance=garden.water_balance,
        leaves_balance=garden.leaves_balance,
        selected_plant_id=garden.selected_plant_id,
        vitality=calculate_vitality(garden.last_watered_at),
        catalog=catalog
    )

async def unlock_plant(db: AsyncSession, user_id: UUID, plant_id: UUID) -> GardenStateResponse:
    garden = await _ensure_garden_state(db, user_id)
    plant = await db.scalar(select(Plant).where(Plant.id == plant_id, Plant.is_active == True))
    
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found or inactive")
        
    existing_ownership = await db.scalar(select(PlantOwnership).where(PlantOwnership.user_id == user_id, PlantOwnership.plant_id == plant_id))
    if existing_ownership:
        # Idempotent
        return await get_garden_state(db, user_id)
        
    if garden.leaves_balance < plant.unlock_cost:
        raise HTTPException(status_code=402, detail="Insufficient leaves")
        
    garden.leaves_balance -= plant.unlock_cost
    
    ownership = PlantOwnership(user_id=user_id, plant_id=plant_id)
    db.add(ownership)
    
    # Ledger
    event = RewardEvent(
        user_id=user_id,
        event_type="PLANT_UNLOCK",
        resource_type="LEAVES",
        amount=-plant.unlock_cost,
        idempotency_key=f"unlock_{user_id}_{plant_id}_{datetime.now().timestamp()}"
    )
    db.add(event)
    
    await db.commit()
    return await get_garden_state(db, user_id)

async def select_plant(db: AsyncSession, user_id: UUID, plant_id: UUID) -> GardenStateResponse:
    garden = await _ensure_garden_state(db, user_id)
    ownership = await db.scalar(select(PlantOwnership).where(PlantOwnership.user_id == user_id, PlantOwnership.plant_id == plant_id))
    
    if not ownership:
        raise HTTPException(status_code=403, detail="Plant not owned")
        
    garden.selected_plant_id = plant_id
    await db.commit()
    
    return await get_garden_state(db, user_id)

async def water_plant(db: AsyncSession, user_id: UUID) -> WaterPlantResponse:
    garden = await _ensure_garden_state(db, user_id)
    
    if not garden.selected_plant_id:
        raise HTTPException(status_code=400, detail="No plant selected")
        
    if garden.water_balance < WATERING_COST:
        raise HTTPException(status_code=402, detail="Insufficient water")
        
    garden.water_balance -= WATERING_COST
    now = datetime.now(timezone.utc)
    garden.last_watered_at = now
    
    event = RewardEvent(
        user_id=user_id,
        event_type="WATER_PLANT",
        resource_type="WATER",
        amount=-WATERING_COST,
        idempotency_key=f"water_{user_id}_{now.timestamp()}"
    )
    db.add(event)
    await db.commit()
    
    return WaterPlantResponse(
        water_balance=garden.water_balance,
        last_watered_at=now,
        vitality=calculate_vitality(garden.last_watered_at, current_time=now)
    )
