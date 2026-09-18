import uuid
from datetime import datetime, timezone

import pytest_asyncio
from app.db.models.garden import GardenState, Plant, PlantOwnership, RewardEvent
from app.db.models.users import User
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def test_garden_state(db_session: AsyncSession, test_user: User) -> GardenState:
    garden = GardenState(
        user_id=test_user.id,
        water_balance=100,
        leaves_balance=50,
        growth_points=0,
        last_watered_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    db_session.add(garden)
    await db_session.commit()
    await db_session.refresh(garden)
    return garden


@pytest_asyncio.fixture
async def test_plant(db_session: AsyncSession) -> Plant:
    plant = Plant(
        id=uuid.uuid4(),
        species="test_succulent",
        name="Test Succulent",
        description="A beautiful test plant.",
        unlock_cost=50,
        is_active=True,
    )
    db_session.add(plant)
    await db_session.commit()
    await db_session.refresh(plant)
    return plant


@pytest_asyncio.fixture
async def test_plant_ownership(
    db_session: AsyncSession, test_user: User, test_plant: Plant
) -> PlantOwnership:
    ownership = PlantOwnership(
        id=uuid.uuid4(),
        user_id=test_user.id,
        plant_id=test_plant.id,
        unlocked_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    db_session.add(ownership)
    await db_session.commit()
    await db_session.refresh(ownership)
    return ownership


@pytest_asyncio.fixture
async def test_reward_event(db_session: AsyncSession, test_user: User) -> RewardEvent:
    event = RewardEvent(
        id=uuid.uuid4(),
        user_id=test_user.id,
        event_type="FOCUS_COMPLETED",
        resource_type="WATER",
        amount=10,
        idempotency_key="test_focus_1",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)
    return event
