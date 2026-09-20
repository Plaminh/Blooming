import logging
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.economy import WATERING_COST, calculate_vitality
from app.db.models.garden import GardenState, Plant, PlantOwnership, RewardEvent
from app.db.models.users import User
from app.schemas.garden import GardenStateResponse, PlantCatalogItem, WaterPlantResponse

GROWTH_THRESHOLDS = {
    "SPROUTING": 0,
    "GROWING": 100,
    "BLOOMING": 300,
    "FLOURISHING": 700,
}

REWARD_AMOUNTS = {"TASK_COMPLETION": 10, "MILESTONE_COMPLETION": 50}
logger = logging.getLogger(__name__)


async def _ensure_garden_state(
    db: AsyncSession, user_id: UUID
) -> tuple[GardenState, bool]:
    # Serialize balance changes, including first-time state creation.
    await db.execute(select(User.id).where(User.id == user_id).with_for_update())
    inserted = await db.scalar(
        insert(GardenState)
        .values(user_id=user_id)
        .on_conflict_do_nothing(index_elements=[GardenState.user_id])
        .returning(GardenState.user_id)
    )
    garden = await db.scalar(
        select(GardenState)
        .where(GardenState.user_id == user_id)
        .execution_options(populate_existing=True)
    )
    assert garden is not None
    return garden, inserted is not None


async def award_resources(
    db: AsyncSession,
    user_id: UUID,
    resource_type: Literal["WATER", "LEAVES"],
    amount: int,
    event_type: str,
    idempotency_key: str,
    source_id: UUID | None = None,
) -> bool:
    """Award the ledger entry, balance and eligible growth in one caller transaction."""
    garden, _ = await _ensure_garden_state(db, user_id)
    values = {
        "user_id": user_id,
        "event_type": event_type,
        "resource_type": resource_type,
        "amount": amount,
        "idempotency_key": idempotency_key,
    }
    source_fields = {
        "FOCUS_COMPLETED": "source_focus_run_id",
        "TASK_COMPLETED": "source_task_id",
        "CORE_OBJECTIVE_COMPLETED": "source_task_id",
        "MILESTONE_COMPLETED": "source_milestone_id",
        "RECOVERY_PLAN_COMPLETED": "source_plan_revision_id",
    }
    if event_type in source_fields:
        values[source_fields[event_type]] = source_id
    inserted = await db.scalar(
        insert(RewardEvent)
        .values(**values)
        .on_conflict_do_nothing(index_elements=[RewardEvent.idempotency_key])
        .returning(RewardEvent.id)
    )
    if inserted is None:
        logger.info("resource_award_duplicate", extra={"event_type": event_type})
        return False
    if resource_type == "WATER":
        garden.water_balance += amount
    else:
        garden.leaves_balance += amount
        growth = {
            "TASK_COMPLETED": REWARD_AMOUNTS["TASK_COMPLETION"],
            "MILESTONE_COMPLETED": REWARD_AMOUNTS["MILESTONE_COMPLETION"],
        }
        if amount > 0:
            garden.growth_points += growth.get(event_type, 0)
    await db.flush()
    logger.info("resource_award_staged", extra={"event_type": event_type, "resource_type": resource_type, "amount": amount})
    return True


async def get_garden_state(db: AsyncSession, user_id: UUID) -> GardenStateResponse:
    garden, created = await _ensure_garden_state(db, user_id)
    plants = (await db.scalars(select(Plant).where(Plant.is_active == True))).all()
    ownerships = (
        await db.scalars(
            select(PlantOwnership).where(PlantOwnership.user_id == user_id)
        )
    ).all()
    owned_ids = {o.plant_id for o in ownerships}

    # Give a new garden its free starter plant, including accounts created
    # before this default was introduced. Preserve every existing selection.
    if garden.selected_plant_id is None and not owned_ids:
        starter = next((p for p in plants if p.species == "monstera" and p.unlock_cost == 0), None)
        if starter is not None:
            db.add(PlantOwnership(user_id=user_id, plant_id=starter.id))
            garden.selected_plant_id = starter.id
            owned_ids.add(starter.id)
            created = True

    if created:
        await db.commit()
        await db.refresh(garden)

    catalog = []
    for p in plants:
        catalog.append(
            PlantCatalogItem(
                id=p.id,
                species=p.species,
                name=p.name,
                description=p.description,
                unlock_cost=p.unlock_cost,
                is_unlocked=p.id in owned_ids,
                is_selected=(p.id == garden.selected_plant_id),
            )
        )

    points = garden.growth_points or 0
    from typing import Literal
    stage: Literal["SPROUTING", "GROWING", "BLOOMING", "FLOURISHING"] = "SPROUTING"
    if points >= GROWTH_THRESHOLDS["FLOURISHING"]:
        stage = "FLOURISHING"
    elif points >= GROWTH_THRESHOLDS["BLOOMING"]:
        stage = "BLOOMING"
    elif points >= GROWTH_THRESHOLDS["GROWING"]:
        stage = "GROWING"
    elif points >= GROWTH_THRESHOLDS["SPROUTING"]:
        stage = "SPROUTING"

    return GardenStateResponse(
        water_balance=garden.water_balance,
        leaves_balance=garden.leaves_balance,
        selected_plant_id=garden.selected_plant_id,
        growth_points=points,
        growth_stage=stage,
        vitality=calculate_vitality(garden.last_watered_at),
        catalog=catalog,
    )


async def unlock_plant(
    db: AsyncSession, user_id: UUID, plant_id: UUID
) -> GardenStateResponse:
    garden, _ = await _ensure_garden_state(db, user_id)
    plant = await db.scalar(
        select(Plant).where(Plant.id == plant_id, Plant.is_active == True)
    )

    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found or inactive")

    existing_ownership = await db.scalar(
        select(PlantOwnership).where(
            PlantOwnership.user_id == user_id, PlantOwnership.plant_id == plant_id
        )
    )
    if existing_ownership:
        # Idempotent
        await db.commit()
        return await get_garden_state(db, user_id)

    if garden.leaves_balance < plant.unlock_cost:
        raise HTTPException(status_code=409, detail={"code": "INSUFFICIENT_LEAVES", "message": "Insufficient leaves", "required": plant.unlock_cost, "available": garden.leaves_balance})

    garden.leaves_balance -= plant.unlock_cost

    ownership = PlantOwnership(user_id=user_id, plant_id=plant_id)
    db.add(ownership)

    # Ledger
    event = RewardEvent(
        user_id=user_id,
        event_type="PLANT_UNLOCK",
        resource_type="LEAVES",
        amount=-plant.unlock_cost,
        idempotency_key=f"unlock_{user_id}_{plant_id}_{datetime.now(timezone.utc).timestamp()}",
    )
    db.add(event)

    await db.commit()
    logger.info("plant_unlocked", extra={"plant_id": str(plant_id), "cost": plant.unlock_cost})
    return await get_garden_state(db, user_id)


async def select_plant(
    db: AsyncSession, user_id: UUID, plant_id: UUID
) -> GardenStateResponse:
    garden, _ = await _ensure_garden_state(db, user_id)
    ownership = await db.scalar(
        select(PlantOwnership).where(
            PlantOwnership.user_id == user_id, PlantOwnership.plant_id == plant_id
        )
    )

    if not ownership:
        raise HTTPException(status_code=404, detail="Unlocked plant not found")

    garden.selected_plant_id = plant_id
    await db.commit()

    return await get_garden_state(db, user_id)


async def water_plant(db: AsyncSession, user_id: UUID) -> WaterPlantResponse:
    garden, _ = await _ensure_garden_state(db, user_id)

    if not garden.selected_plant_id:
        raise HTTPException(status_code=409, detail="No plant selected")

    if garden.water_balance < WATERING_COST:
        raise HTTPException(status_code=409, detail={"code": "INSUFFICIENT_WATER", "message": "Insufficient water", "required": WATERING_COST, "available": garden.water_balance})

    garden.water_balance -= WATERING_COST
    now = datetime.now(timezone.utc)
    garden.last_watered_at = now

    event = RewardEvent(
        user_id=user_id,
        event_type="WATER_PLANT",
        resource_type="WATER",
        amount=-WATERING_COST,
        idempotency_key=f"water_{user_id}_{now.timestamp()}",
    )
    db.add(event)
    await db.commit()
    logger.info("garden_watered", extra={"cost": WATERING_COST})

    return WaterPlantResponse(
        water_balance=garden.water_balance,
        last_watered_at=now,
        vitality=calculate_vitality(garden.last_watered_at, current_time=now),
    )
