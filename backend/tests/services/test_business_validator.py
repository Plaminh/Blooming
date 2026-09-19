import pytest
from datetime import datetime, timedelta
import zoneinfo
from app.services.business_validator import BusinessValidator
from app.models.ai_schemas import AIRequestContext, TodayDraftProposal, RoadmapDraftProposal, TaskDraft, MilestoneDraft, InferredValue

@pytest.fixture
def current_time():
    return datetime.now(zoneinfo.ZoneInfo("UTC"))

@pytest.fixture
def req_context(current_time):
    return AIRequestContext(
        user_input="test",
        context_type="today_planning",
        current_time=current_time,
        timezone="UTC"
    )

@pytest.fixture
def validator():
    return BusinessValidator()

def test_today_valid(validator, req_context, current_time):
    proposal = TodayDraftProposal(
        tasks=[
            TaskDraft(title="Task 1", duration_min=InferredValue(value=30, source="USER")),
            TaskDraft(title="Task 2", dependencies=["Task 1"])
        ]
    )
    is_valid, err = validator.validate(proposal, req_context)
    assert is_valid is True
    assert err is None

def test_today_empty_title(validator, req_context):
    proposal = TodayDraftProposal(tasks=[TaskDraft(title="  ")])
    is_valid, err = validator.validate(proposal, req_context)
    assert is_valid is False
    assert "empty" in err.lower()

def test_today_duplicate_title(validator, req_context):
    proposal = TodayDraftProposal(tasks=[
        TaskDraft(title="Task 1"),
        TaskDraft(title="Task 1")
    ])
    is_valid, err = validator.validate(proposal, req_context)
    assert is_valid is False
    assert "duplicate" in err.lower()

def test_today_negative_duration(validator, req_context):
    proposal = TodayDraftProposal(tasks=[TaskDraft(title="T", duration_min=InferredValue(value=-5, source="USER"))])
    is_valid, err = validator.validate(proposal, req_context)
    assert is_valid is False
    assert "non-positive" in err.lower()

def test_today_past_deadline(validator, req_context, current_time):
    past = current_time - timedelta(hours=1)
    proposal = TodayDraftProposal(tasks=[TaskDraft(title="T", deadline=InferredValue(value=past, source="USER"))])
    is_valid, err = validator.validate(proposal, req_context)
    assert is_valid is False
    assert "past" in err.lower()

def test_today_self_dependency(validator, req_context):
    proposal = TodayDraftProposal(tasks=[TaskDraft(title="T", dependencies=["T"])])
    is_valid, err = validator.validate(proposal, req_context)
    assert is_valid is False
    assert "depends on itself" in err.lower()

def test_today_non_existent_dependency(validator, req_context):
    proposal = TodayDraftProposal(tasks=[TaskDraft(title="T", dependencies=["Missing"])])
    is_valid, err = validator.validate(proposal, req_context)
    assert is_valid is False
    assert "depends on non-existent task" in err.lower()

def test_today_duplicate_dependency(validator, req_context):
    proposal = TodayDraftProposal(tasks=[
        TaskDraft(title="T1"),
        TaskDraft(title="T2", dependencies=["T1", "T1"])
    ])
    is_valid, err = validator.validate(proposal, req_context)
    assert is_valid is False
    assert "duplicate dependency" in err.lower()

def test_today_fixed_without_deadline(validator, req_context):
    proposal = TodayDraftProposal(tasks=[TaskDraft(title="T", is_fixed=InferredValue(value=True, source="USER"))])
    is_valid, err = validator.validate(proposal, req_context)
    assert is_valid is False
    assert "fixed task 't' requires a deadline" in err.lower()

def test_roadmap_valid(validator, req_context, current_time):
    req_context.context_type = "roadmap_planning"
    future = current_time + timedelta(days=1)
    proposal = RoadmapDraftProposal(
        goal_title="Goal",
        milestones=[
            MilestoneDraft(title="M1"),
            MilestoneDraft(title="M2", target_date=InferredValue(value=future, source="USER"))
        ]
    )
    is_valid, err = validator.validate(proposal, req_context)
    assert is_valid is True
    assert err is None

def test_roadmap_duplicate_milestone(validator, req_context):
    req_context.context_type = "roadmap_planning"
    proposal = RoadmapDraftProposal(goal_title="G", milestones=[
        MilestoneDraft(title="M"), MilestoneDraft(title="M")
    ])
    is_valid, err = validator.validate(proposal, req_context)
    assert is_valid is False
    assert "duplicate" in err.lower()

def test_today_max_duration(validator, req_context):
    proposal = TodayDraftProposal(tasks=[TaskDraft(title="T", duration_min=InferredValue(value=721, source="USER"))])
    is_valid, err = validator.validate(proposal, req_context)
    assert is_valid is False
    assert "exceeds 12 hours" in err.lower()

def test_today_total_duration(validator, req_context):
    proposal = TodayDraftProposal(tasks=[
        TaskDraft(title=f"T{i}", duration_min=InferredValue(value=120, source="USER")) for i in range(13)
    ])
    is_valid, err = validator.validate(proposal, req_context)
    assert is_valid is False
    assert "exceeds 24 hours" in err.lower()

def test_today_max_tasks(validator, req_context):
    proposal = TodayDraftProposal(tasks=[TaskDraft(title=f"T{i}") for i in range(51)])
    is_valid, err = validator.validate(proposal, req_context)
    assert is_valid is False
    assert "limit 50" in err.lower()

def test_roadmap_empty_goal(validator, req_context):
    req_context.context_type = "roadmap_planning"
    proposal = RoadmapDraftProposal(goal_title="  ", milestones=[MilestoneDraft(title="M")])
    is_valid, err = validator.validate(proposal, req_context)
    assert is_valid is False
    assert "goal title cannot be empty" in err.lower()

def test_roadmap_empty_milestone(validator, req_context):
    req_context.context_type = "roadmap_planning"
    proposal = RoadmapDraftProposal(goal_title="G", milestones=[MilestoneDraft(title="")])
    is_valid, err = validator.validate(proposal, req_context)
    assert is_valid is False
    assert "milestone title cannot be empty" in err.lower()

def test_roadmap_past_milestone(validator, req_context, current_time):
    req_context.context_type = "roadmap_planning"
    past = current_time - timedelta(days=1)
    proposal = RoadmapDraftProposal(goal_title="G", milestones=[MilestoneDraft(title="M", target_date=InferredValue(value=past, source="USER"))])
    is_valid, err = validator.validate(proposal, req_context)
    assert is_valid is False
    assert "in the past" in err.lower()

def test_roadmap_chronological_order(validator, req_context, current_time):
    req_context.context_type = "roadmap_planning"
    future1 = current_time + timedelta(days=5)
    future2 = current_time + timedelta(days=2)
    proposal = RoadmapDraftProposal(goal_title="G", milestones=[
        MilestoneDraft(title="M1", target_date=InferredValue(value=future1, source="USER")),
        MilestoneDraft(title="M2", target_date=InferredValue(value=future2, source="USER"))
    ])
    is_valid, err = validator.validate(proposal, req_context)
    assert is_valid is False
    assert "chronologically ordered" in err.lower()

def test_roadmap_max_milestones(validator, req_context):
    req_context.context_type = "roadmap_planning"
    proposal = RoadmapDraftProposal(goal_title="G", milestones=[MilestoneDraft(title=f"M{i}") for i in range(101)])
    is_valid, err = validator.validate(proposal, req_context)
    assert is_valid is False
    assert "limit 100" in err.lower()

