"""Zero token mood support with explicit, allowlisted actions."""

from app.schemas.assistant import ChatResponse, QuickReply


def tired_response(lang: str, *, has_plan: bool = True) -> ChatResponse:
    if lang == "vi":
        reply = ("Nghe như bạn đang mệt. Bạn có thể bỏ các việc không bắt buộc hôm nay nếu muốn."
                 if has_plan else "Nghe như bạn đang mệt. Mình có thể giúp bạn lập một kế hoạch nhẹ cho hôm nay.")
        label = "Bỏ việc không bắt buộc" if has_plan else "Lập kế hoạch nhẹ"
    else:
        reply = ("It sounds like you're tired. You can skip today's optional tasks if you choose."
                 if has_plan else "It sounds like you're tired. I can help make a light plan for today.")
        label = "Skip optional tasks" if has_plan else "Make a light plan"
    return ChatResponse(
        reply=reply, intent="MOOD", tier="RULES",
        suggestions=[QuickReply(label=label, action="SKIP_OPTIONAL_TODAY") if has_plan
                     else QuickReply(label=label, send_text="Plan my day: one small task 25 min")],
    )
