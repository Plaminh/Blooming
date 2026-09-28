"""Zero-token bilingual conversation templates."""

from app.ai.nlu.router import normalize


def reply(message: str, lang: str, streak: int = 0) -> str:
    text = normalize(message)
    if streak >= 3:
        return (
            "Mình giỏi nhất khoản lên kế hoạch. Hôm nay bạn cần sắp xếp gì?"
            if lang == "vi"
            else "I can help you plan and stay focused. What would you like to organize today?"
        )
    if "thoi tiet" in text or "weather" in text:
        return (
            "Mình chưa có dự báo thời tiết trong chat. Bạn muốn lên kế hoạch hôm nay không?"
            if lang == "vi"
            else "I don't have a weather forecast in chat. Would you like to plan your day?"
        )
    if "joke" in text or "chuyen cuoi" in text:
        return (
            "Một chiếc lịch nói: hôm nay tôi kín quá! Bạn muốn sắp xếp ngày hôm nay không?"
            if lang == "vi"
            else "My calendar said it was fully booked. Want to plan your day?"
        )
    if "yeu" in text or "love" in text:
        return (
            "Mình luôn sẵn sàng đồng hành cùng bạn. Mình giúp bạn lên kế hoạch nhé?"
            if lang == "vi"
            else "I'm here to support you. Would you like help planning?"
        )
    return (
        "Mình đang lắng nghe. Hôm nay bạn muốn lên kế hoạch cho việc gì?"
        if lang == "vi"
        else "I'm listening. What would you like to plan today?"
    )
