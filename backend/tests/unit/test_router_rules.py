import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from app.ai.handlers.chitchat import reply as chitchat_reply
from app.ai.router import detect_lang, normalize, route
from app.ai.router import classify_low_confidence
from app.ai import budget
from app.ai.providers import llm_provider


@pytest.mark.parametrize(
    "message,intent,has_draft",
    [
        ("Hi", "GREETING", False),
        ("Hello", "GREETING", False),
        ("Hey there", "GREETING", False),
        ("Alo", "GREETING", False),
        ("Chào", "GREETING", False),
        ("Xin chào", "GREETING", False),
        ("Chào bạn", "GREETING", False),
        ("Alo bạn ơi", "GREETING", False),
        ("Thanks", "THANKS", False),
        ("Thank you", "THANKS", False),
        ("Tks", "THANKS", False),
        ("Thanks a lot", "THANKS", False),
        ("Cảm ơn", "THANKS", False),
        ("Cám ơn nhiều", "THANKS", False),
        ("Cảm ơn bạn", "THANKS", False),
        ("Tôi cảm ơn", "THANKS", False),
        ("Today what tasks?", "STATUS_TODAY", False),
        ("Today schedule?", "STATUS_TODAY", False),
        ("Next task", "STATUS_TODAY", False),
        ("What do I have today?", "STATUS_TODAY", False),
        ("Hôm nay còn gì?", "STATUS_TODAY", False),
        ("Hôm nay có kế hoạch gì?", "STATUS_TODAY", False),
        ("Việc tiếp theo", "STATUS_TODAY", False),
        ("Hôm nay làm gì?", "STATUS_TODAY", False),
        ("Water balance", "STATUS_GARDEN", False),
        ("My garden water", "STATUS_GARDEN", False),
        ("Leaves balance", "STATUS_GARDEN", False),
        ("Nước còn bao nhiêu?", "STATUS_GARDEN", False),
        ("Vườn của tôi", "STATUS_GARDEN", False),
        ("Cây thế nào?", "STATUS_GARDEN", False),
        ("Statistics", "STATUS_STATS", False),
        ("Stats this week", "STATUS_STATS", False),
        ("Thống kê", "STATUS_STATS", False),
        ("Tuần này học bao nhiêu giờ", "STATUS_STATS", False),
        ("My current goal", "STATUS_GOALS", False),
        ("Next milestone", "STATUS_GOALS", False),
        ("Mục tiêu của tôi", "STATUS_GOALS", False),
        ("Milestone tiếp theo", "STATUS_GOALS", False),
        ("What is Pomodoro?", "HELP_FEATURE", False),
        ("What is Water?", "HELP_FEATURE", False),
        ("What can you do?", "HELP_FEATURE", False),
        ("Pomodoro là gì?", "HELP_FEATURE", False),
        ("Leaves là gì?", "HELP_FEATURE", False),
        ("Bạn là ai?", "HELP_FEATURE", False),
        ("Plan my day", "PLAN_DAY", False),
        ("Schedule my day", "PLAN_DAY", False),
        ("Study 60 min and write 30 min", "PLAN_DAY", False),
        ("Lập lịch hôm nay", "PLAN_DAY", False),
        ("Lên kế hoạch", "PLAN_DAY", False),
        ("Học 60p, viết 30p", "PLAN_DAY", False),
        ("Create a goal", "CREATE_GOAL", False),
        ("Build a roadmap", "CREATE_GOAL", False),
        ("Tạo mục tiêu", "CREATE_GOAL", False),
        ("Lộ trình học", "CREATE_GOAL", False),
        ("Change task 2", "EDIT_DRAFT", True),
        ("Remove the last task", "EDIT_DRAFT", True),
        ("Đổi việc thứ hai", "EDIT_DRAFT", True),
        ("Xóa việc này", "EDIT_DRAFT", True),
        ("I'm tired", "MOOD", False),
        ("I'm stressed", "MOOD", False),
        ("Tôi mệt", "MOOD", False),
        ("Buồn ngủ", "MOOD", False),
        ("Tell me a joke", "CHITCHAT", False),
        ("Kể chuyện cười", "CHITCHAT", False),
        ("I might kill myself", "CRISIS", False),
        ("I am thinking about suicide", "CRISIS", False),
        ("Tôi muốn tự tử", "CRISIS", False),
        ("Tôi không muốn sống", "CRISIS", False),
    ],
)
def test_bilingual_routing(message, intent, has_draft):
    assert route(message, has_draft=has_draft).intent == intent


def test_normalization_and_precedence():
    assert normalize(" ĐỔI  KẾ HOẠCH ") == "doi ke hoach"
    assert detect_lang("Hôm nay làm gì?") == "vi"
    assert route("Hôm nay mệt, lập lịch nhẹ thôi").intent == "PLAN_DAY"
    assert "tired" in route("Hôm nay mệt, lập lịch nhẹ thôi").flags
    assert route("Từ từ thôi").intent != "CRISIS"
    assert route("I want to hurt myself; plan my day").intent == "CRISIS"


def test_chitchat_templates_return_to_planning_without_model():
    assert "forecast" in chitchat_reply("How is the weather?", "en")
    assert "sắp xếp" in chitchat_reply("Kể chuyện cười", "vi")
    assert "plan" in chitchat_reply("Tell me more", "en", streak=3)


@pytest.mark.parametrize("message", [
    "Plan 30 minutes of reading today",
    "Schedule study for one hour at 14:00",
    "I have two hours for a report and email",
    "Plan a calm afternoon",
    "Help me split a long study session",
])
def test_explicit_planning_language_routes_without_classifier(message):
    selected = route(message)
    assert selected.intent == "PLAN_DAY"
    assert selected.confidence >= 0.7


@pytest.mark.asyncio
async def test_low_confidence_uses_budgeted_classifier_and_db_history(monkeypatch):
    monkeypatch.setattr(budget, "get_budget_mode", AsyncMock(return_value=budget.BudgetMode.NORMAL))
    monkeypatch.setattr(budget, "available_routes", AsyncMock(return_value="ollama:small"))
    provider_call = AsyncMock(return_value={"intent": "CREATE_GOAL"})
    monkeypatch.setattr(llm_provider, "call", provider_call)
    selected = await classify_low_confidence("Help with a project", route("Help with a project"),
        AsyncMock(), uuid4(), [{"role": "user", "content": "I want a long term outcome"}])
    assert selected.intent == "CREATE_GOAL"
    assert selected.source == "llm"
    assert provider_call.await_args.kwargs["purpose"] == "ROUTER"
    assert provider_call.await_args.args[1][1]["content"] == "I want a long term outcome"
