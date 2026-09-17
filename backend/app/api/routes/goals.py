from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, SessionDep
from app.schemas.goals import (
    GoalCreate,
    GoalResponse,
    GoalUpdate,
    MilestoneCreate,
    MilestoneResponse,
    MilestoneUpdate,
)
from app.services.goals_service import goals_service

router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("/", response_model=list[GoalResponse])
async def list_goals(
    db: SessionDep,
    current_user: CurrentUser,
):
    return await goals_service.get_goals(db, current_user.id)


@router.post("/", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_in: GoalCreate,
    db: SessionDep,
    current_user: CurrentUser,
):
    goal = await goals_service.create_goal(db, goal_in, current_user.id)
    await db.commit()
    return goal


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: UUID,
    db: SessionDep,
    current_user: CurrentUser,
):
    return await goals_service.get_goal(db, goal_id, current_user.id)


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: UUID,
    goal_in: GoalUpdate,
    db: SessionDep,
    current_user: CurrentUser,
):
    goal = await goals_service.update_goal(db, goal_id, goal_in, current_user.id)
    await db.commit()
    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: UUID,
    db: SessionDep,
    current_user: CurrentUser,
) -> None:
    await goals_service.delete_goal(db, goal_id, current_user.id)
    await db.commit()


@router.post(
    "/{goal_id}/milestones",
    response_model=MilestoneResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_milestone(
    goal_id: UUID,
    milestone_in: MilestoneCreate,
    db: SessionDep,
    current_user: CurrentUser,
):
    milestone = await goals_service.create_milestone(
        db, goal_id, milestone_in, current_user.id
    )
    await db.commit()
    return milestone


@router.put("/{goal_id}/milestones/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(
    goal_id: UUID,
    milestone_id: UUID,
    milestone_in: MilestoneUpdate,
    db: SessionDep,
    current_user: CurrentUser,
):
    milestone = await goals_service.update_milestone(
        db, goal_id, milestone_id, milestone_in, current_user.id
    )
    await db.commit()
    return milestone


@router.delete(
    "/{goal_id}/milestones/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_milestone(
    goal_id: UUID,
    milestone_id: UUID,
    db: SessionDep,
    current_user: CurrentUser,
) -> None:
    await goals_service.delete_milestone(db, goal_id, milestone_id, current_user.id)
    await db.commit()
