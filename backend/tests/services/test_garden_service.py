import pytest
from app.core.economy import WATERING_COST
from app.db.models.garden import GardenState, PlantOwnership, RewardEvent
from app.services import garden_service
from app.services.garden_service import award_resources
from fastapi import HTTPException
from sqlalchemy import event, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

pytestmark = pytest.mark.integration


async def test_water_and_leaves_awards(db_session, test_user):
    user_id = test_user.id
    assert await award_resources(
        db_session, user_id, "WATER", 10, "FOCUS_COMPLETED", "water"
    )
    assert await award_resources(
        db_session, user_id, "LEAVES", 5, "MILESTONE_COMPLETED", "leaves"
    )
    await db_session.commit()
    db_session.expire_all()
    garden = await db_session.get(GardenState, user_id)
    assert (garden.water_balance, garden.leaves_balance, garden.growth_points) == (
        10,
        5,
        50,
    )
    events = (
        await db_session.scalars(
            select(RewardEvent).order_by(RewardEvent.idempotency_key)
        )
    ).all()
    assert [(e.idempotency_key, e.resource_type, e.amount) for e in events] == [
        ("leaves", "LEAVES", 5),
        ("water", "WATER", 10),
    ]


async def test_same_key_awards_once_and_different_keys_award_separately(
    db_session, test_user
):
    user_id = test_user.id
    assert await award_resources(
        db_session, user_id, "LEAVES", 1, "TASK_COMPLETED", "one"
    )
    await db_session.commit()
    assert not await award_resources(
        db_session, user_id, "LEAVES", 1, "TASK_COMPLETED", "one"
    )
    assert await award_resources(
        db_session, user_id, "LEAVES", 1, "TASK_COMPLETED", "two"
    )
    await db_session.commit()
    garden = await db_session.get(GardenState, user_id)
    assert (garden.leaves_balance, garden.growth_points) == (2, 20)
    assert len((await db_session.scalars(select(RewardEvent))).all()) == 2


@pytest.mark.parametrize(
    "resource,amount,constraint",
    [
        ("INVALID_RESOURCE", 10, "reward_events_resource_type_valid"),
        ("WATER", -1, "garden_states_water_valid"),
        ("LEAVES", -1, "garden_states_leaves_valid"),
    ],
)
async def test_invalid_reward_rollback_and_atomicity(
    db_session, test_user, resource, amount, constraint
):
    user_id = test_user.id
    await garden_service.get_garden_state(db_session, user_id)
    with pytest.raises(IntegrityError) as exc:
        await award_resources(
            db_session, user_id, resource, amount, "FOCUS_COMPLETED", "invalid"
        )
    assert exc.value.orig.diag.constraint_name == constraint
    await db_session.rollback()
    garden = await db_session.get(GardenState, user_id)
    assert (garden.water_balance, garden.leaves_balance, garden.growth_points) == (
        0,
        0,
        0,
    )
    assert (await db_session.scalars(select(RewardEvent))).all() == []


async def test_ledger_and_balance_roll_back_when_balance_flush_fails(
    db_session, test_user
):
    user_id = test_user.id
    await garden_service.get_garden_state(db_session, user_id)
    observed = []

    def fail_balance_flush(session, flush_context, instances):
        if session is db_session.sync_session and any(
            isinstance(obj, GardenState) for obj in session.dirty
        ):
            observed.append(True)
            raise RuntimeError("injected balance persistence failure")

    event.listen(Session, "before_flush", fail_balance_flush)
    try:
        with pytest.raises(RuntimeError, match="injected balance"):
            await award_resources(
                db_session, user_id, "WATER", 1, "FOCUS_COMPLETED", "atomic"
            )
    finally:
        event.remove(Session, "before_flush", fail_balance_flush)
    await db_session.rollback()
    assert observed == [True]
    assert (await db_session.get(GardenState, user_id)).water_balance == 0
    assert (await db_session.scalars(select(RewardEvent))).all() == []


async def test_watering_vitality_and_growth_unlock_preservation(
    db_session, test_user, test_garden_state, test_plant, test_plant_ownership, clock
):
    user_id, plant_id = test_user.id, test_plant.id
    garden = test_garden_state
    garden.selected_plant_id = plant_id
    garden.growth_points = 350
    garden.last_watered_at = clock.instant
    await db_session.commit()
    clock.advance(3 * 86400)
    before = await garden_service.get_garden_state(db_session, user_id)
    assert before.vitality == 70
    from uuid import uuid4

    result = await garden_service.water_plant(db_session, user_id, uuid4())
    assert result.water_balance == 100 - WATERING_COST
    assert result.last_watered_at == clock.instant
    assert result.vitality == 100
    db_session.expire_all()
    after = await garden_service.get_garden_state(db_session, user_id)
    assert (after.growth_points, after.growth_stage, after.selected_plant_id) == (
        350,
        "BLOOMING",
        plant_id,
    )
    assert after.leaves_balance == 50
    assert after.vitality == 100
    assert [(p.id, p.is_unlocked) for p in after.catalog] == [
        (p.id, p.is_unlocked) for p in before.catalog
    ]
    assert len((await db_session.scalars(select(PlantOwnership))).all()) == 1
    reward = (await db_session.scalars(select(RewardEvent))).one()
    assert (reward.event_type, reward.resource_type, reward.amount) == (
        "WATER_PLANT",
        "WATER",
        -WATERING_COST,
    )


async def test_water_plant_idempotency_same_and_different_keys(
    db_session, test_user, test_garden_state, test_plant, test_plant_ownership, clock
):
    from uuid import uuid4

    user_id = test_user.id
    test_garden_state.selected_plant_id = test_plant.id
    test_garden_state.water_balance = 3
    await db_session.commit()

    key_same = uuid4()
    key_new = uuid4()

    # Initial water
    result1 = await garden_service.water_plant(db_session, user_id, key_same)
    assert result1.water_balance == 2

    # Double click / retry
    result2 = await garden_service.water_plant(db_session, user_id, key_same)
    assert result2.water_balance == 2

    # New action
    result3 = await garden_service.water_plant(db_session, user_id, key_new)
    assert result3.water_balance == 1

    events = (
        await db_session.scalars(
            select(RewardEvent).where(RewardEvent.event_type == "WATER_PLANT")
        )
    ).all()
    assert len(events) == 2
    assert set([e.idempotency_key for e in events]) == {
        f"water_{user_id}_{key_new}",
        f"water_{user_id}_{key_same}",
    }


async def test_water_plant_concurrent_duplicate(
    db_session, test_user, test_garden_state, test_plant, clock
):
    import asyncio
    from uuid import uuid4
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.db.models.garden import GardenState

    user_id = test_user.id
    test_garden_state.selected_plant_id = test_plant.id
    test_garden_state.water_balance = 3
    await db_session.commit()

    key_same = uuid4()

    # We create two new independent sessions sharing the same engine/connection
    async with AsyncSession(
        bind=db_session.bind, expire_on_commit=False, autoflush=False
    ) as session1:
        async with AsyncSession(
            bind=db_session.bind, expire_on_commit=False, autoflush=False
        ) as session2:
            try:
                # Run concurrently
                results = await asyncio.gather(
                    garden_service.water_plant(session1, user_id, key_same),
                    garden_service.water_plant(session2, user_id, key_same),
                    return_exceptions=True,
                )

                # We expect no unhandled IntegrityError and that both requests return successfully with balance=2
                for res in results:
                    assert not isinstance(res, Exception), (
                        f"Concurrent watering raised {res}"
                    )
                    assert res.water_balance == 2

                await session1.commit()
                await session2.commit()
            except Exception as e:
                await session1.rollback()
                await session2.rollback()
                raise e

    # Check state with original session
    db_session.expire_all()
    garden = await db_session.get(GardenState, user_id)
    assert garden.water_balance == 2

    events = (
        await db_session.scalars(
            select(RewardEvent).where(RewardEvent.event_type == "WATER_PLANT")
        )
    ).all()
    assert len(events) == 1
    assert events[0].idempotency_key == f"water_{user_id}_{key_same}"

    # Verify a new key deducts again
    key_new = uuid4()
    result_new = await garden_service.water_plant(db_session, user_id, key_new)
    assert result_new.water_balance == 1


async def test_unlock_and_repeat_preserve_growth(
    db_session, test_user, test_plant, test_garden_state
):
    user_id, plant_id = test_user.id, test_plant.id
    test_garden_state.growth_points = 350
    await db_session.commit()
    for _ in range(2):
        result = await garden_service.unlock_plant(db_session, user_id, plant_id)
        assert result.leaves_balance == 0
        assert result.growth_points == 350
        assert next(p for p in result.catalog if p.id == plant_id).is_unlocked
    assert len((await db_session.scalars(select(PlantOwnership))).all()) == 1
    rewards = (await db_session.scalars(select(RewardEvent))).all()
    assert len(rewards) == 1
    assert (rewards[0].event_type, rewards[0].amount) == ("PLANT_UNLOCK", -50)


async def test_insufficient_water_leaves_balances_and_events_unchanged(
    db_session, test_user, test_plant, test_plant_ownership
):
    user_id = test_user.id
    garden, _ = await garden_service._ensure_garden_state(db_session, user_id)
    garden.selected_plant_id = test_plant.id
    await db_session.commit()
    from uuid import uuid4

    with pytest.raises(HTTPException) as exc:
        await garden_service.water_plant(db_session, user_id, uuid4())
    assert exc.value.status_code == 409
    assert exc.value.detail == {
        "code": "INSUFFICIENT_WATER",
        "message": "Insufficient water",
        "required": WATERING_COST,
        "available": 0,
    }
    await db_session.rollback()
    garden = await db_session.get(GardenState, user_id)
    assert (garden.water_balance, garden.leaves_balance) == (0, 0)
    assert garden.last_watered_at is None
    assert (await db_session.scalars(select(RewardEvent))).all() == []
