"""Replies backed by authenticated application services and static feature knowledge."""

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.handlers.chitchat import reply as chitchat_reply
from app.ai.knowledge import KB
from app.ai.router import Route, normalize
from app.schemas.assistant import ChatResponse, QuickReply
from app.services import garden_service, statistics_service
from app.services.goals_service import goals_service
from app.services.today_service import today_service


def _chips(lang: str) -> list[QuickReply]:
    if lang == "vi":
        return [QuickReply(label="Lên kế hoạch hôm nay", send_text="Lập lịch hôm nay"), QuickReply(label="Tạo mục tiêu", send_text="Tạo mục tiêu")]
    return [QuickReply(label="Plan my day", send_text="Plan my day"), QuickReply(label="Create a goal", send_text="Create a goal")]


async def handle(
    route: Route, message: str, *, db: AsyncSession | None,
    user_id: UUID | None, now: datetime, lang: str,
) -> ChatResponse:
    intent = route.intent
    suggestions = _chips(lang)
    if intent == "CRISIS":
        reply = (
            "Mình rất tiếc bạn đang trải qua chuyện này. Hãy liên hệ ngay với người bạn tin cậy hoặc dịch vụ khẩn cấp tại nơi bạn sống nếu bạn có nguy cơ làm hại bản thân."
            if lang == "vi" else
            "I'm sorry you're going through this. Please contact someone you trust or local emergency services now if you might hurt yourself."
        )
        suggestions = []
    elif intent == "GREETING":
        if lang == "vi":
            greeting = "Chào buổi sáng" if now.hour < 12 else "Chào buổi chiều" if now.hour < 18 else "Chào buổi tối"
            reply = f"{greeting}! Bạn muốn sắp xếp việc gì hôm nay?"
        else:
            greeting = "Good morning" if now.hour < 12 else "Good afternoon" if now.hour < 18 else "Good evening"
            reply = f"{greeting}! What would you like to plan today?"
    elif intent == "THANKS":
        reply = "Rất vui được giúp bạn. Mình cùng tiếp tục nhé?" if lang == "vi" else "Glad to help. Ready to keep going?"
    elif intent == "HELP_FEATURE":
        text = normalize(message)
        key = next((word for word in ("pomodoro", "water", "leaves", "vitality", "reality") if word in text), None)
        if key is None and ("what can you do" in text or "ban la ai" in text):
            reply = "Mình giúp bạn lên kế hoạch và theo dõi việc tập trung." if lang == "vi" else "I help you plan your day and stay focused."
        elif key:
            reply = KB[key][lang]
        else:
            reply = chitchat_reply(message, lang)
    elif intent == "STATUS_TODAY":
        if db is None or user_id is None:
            raise ValueError("Authenticated database context required")
        today = await today_service.get_today(db, user_id, now.date())
        if today["status"] == "NO_PLAN":
            reply = "Bạn chưa có kế hoạch hôm nay." if lang == "vi" else "You have no plan for today yet."
        else:
            tasks = [block for block in today["blocks"] if block["block_type"] == "TASK"]
            completed = sum(block["status"] == "COMPLETED" for block in tasks)
            pending = next((block for block in tasks if block["status"] not in {"COMPLETED", "SKIPPED", "CANCELLED"}), None)
            if lang == "vi":
                reply = f"Hôm nay có {len(tasks)} việc, đã xong {completed}."
                if pending:
                    reply += f" Tiếp theo: {pending['title']} lúc {pending['planned_start_at'].strftime('%H:%M')}."
            else:
                reply = f"Today you have {len(tasks)} tasks; {completed} are done."
                if pending:
                    reply += f" Next: {pending['title']} at {pending['planned_start_at'].strftime('%H:%M')}."
    elif intent == "STATUS_GARDEN":
        if db is None or user_id is None:
            raise ValueError("Authenticated database context required")
        garden = await garden_service.get_garden_state(db, user_id)
        reply = (
            f"Vườn của bạn có {garden.water_balance} Water và {garden.leaves_balance} Leaves; cây đang ở giai đoạn {garden.growth_stage}."
            if lang == "vi" else
            f"Your garden has {garden.water_balance} Water and {garden.leaves_balance} Leaves; your plant is {garden.growth_stage.lower()}."
        )
    elif intent == "STATUS_STATS":
        if db is None or user_id is None:
            raise ValueError("Authenticated database context required")
        stats = await statistics_service.get_statistics_summary(
            db, user_id, now.date() - timedelta(days=6), now.date(),
        )
        reply = (
            f"7 ngày qua bạn tập trung {stats.study_time_hours} giờ {stats.study_time_minutes} phút trong {stats.study_day_count} ngày."
            if lang == "vi" else
            f"In the last 7 days, you focused for {stats.study_time_hours} hours {stats.study_time_minutes} minutes across {stats.study_day_count} days."
        )
    elif intent == "STATUS_GOALS":
        if db is None or user_id is None:
            raise ValueError("Authenticated database context required")
        goals = await goals_service.get_goals(db, user_id)
        active = [goal for goal in goals if goal.status in {"ACTIVE", "DRAFT", "ON_HOLD"}]
        next_goal = min(active, key=lambda goal: goal.target_date or now.date() + timedelta(days=36500), default=None)
        if next_goal:
            reply = f"Mục tiêu gần nhất: {next_goal.title}." if lang == "vi" else f"Your next goal: {next_goal.title}."
        else:
            reply = "Bạn chưa có mục tiêu đang mở." if lang == "vi" else "You have no open goals yet."
    elif intent == "MOOD":
        reply = (
            "Nghe như bạn đang mệt. Mình có thể giúp chia nhỏ việc hoặc giảm việc không bắt buộc; bạn quyết định trước khi lưu."
            if lang == "vi" else
            "It sounds like you're tired. I can help break work down or reduce optional tasks; you decide before saving."
        )
    elif intent == "EDIT_DRAFT":
        reply = (
            "Bạn có thể sửa thời lượng, mức ưu tiên hoặc bỏ việc ngay trong bản nháp."
            if lang == "vi" else
            "You can adjust duration, importance, or remove tasks in the draft controls."
        )
    else:
        reply = chitchat_reply(message, lang)
    return ChatResponse(reply=reply, intent=intent, tier="RULES", suggestions=suggestions)
