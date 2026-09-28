"""Single question clarification rules for incomplete requests."""

from app.schemas.assistant import ChatResponse


def missing_goal_target_date(lang: str) -> ChatResponse:
    question = (
        "Bạn muốn hoàn thành mục tiêu này vào ngày nào?"
        if lang == "vi"
        else "What date would you like to complete this goal by?"
    )
    return ChatResponse(
        reply=question,
        question=question,
        intent="CREATE_GOAL",
        tier="RULES",
        suggestions=[],
    )
