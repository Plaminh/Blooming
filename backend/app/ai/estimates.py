"""Conservative duration estimates for explicit but untimed tasks."""

from app.ai.nlu.router import normalize

ESTIMATES: tuple[tuple[tuple[str, ...], int, str], ...] = (
    (("bai tap", "homework", "lap trinh", "coding", "code", "lab"), 90, "Learning"),
    (("bao cao", "report", "essay", "luan van"), 90, "Work"),
    (("day kem", "gia su", "day hoc", "tutoring"), 90, "Work"),
    (("hop", "meeting", "standup"), 45, "Work"),
    (("on bai", "on tap", "study", "hoc"), 60, "Learning"),
    (("tai lieu", "reading", "doc", "read"), 45, "Learning"),
    (("email", "mail", "tin nhan"), 15, "Work"),
    (("tap the duc", "gym", "chay bo", "exercise"), 40, "Personal"),
    (("nau an", "an trua", "an toi", "meal", "cook"), 45, "Personal"),
    (("don dep", "giat", "clean"), 30, "Personal"),
)


def estimate(title: str) -> tuple[int, str] | None:
    text = f" {normalize(title)} "
    matches = [
        (len(keyword), minutes, category)
        for keywords, minutes, category in ESTIMATES
        for keyword in keywords
        if f" {keyword} " in text
    ]
    if not matches:
        return None
    _, minutes, category = max(matches, key=lambda match: match[0])
    return minutes, category
