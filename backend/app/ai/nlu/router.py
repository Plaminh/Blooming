"""Deterministic, bilingual intent routing for Mr. Bloom."""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel

Intent = Literal[
    "CRISIS",
    "GREETING",
    "THANKS",
    "STATUS_TODAY",
    "STATUS_GARDEN",
    "STATUS_STATS",
    "STATUS_GOALS",
    "HELP_FEATURE",
    "PLAN_DAY",
    "CREATE_GOAL",
    "EDIT_DRAFT",
    "MOOD",
    "CHITCHAT",
    "STATUS_RECURRING",
    "STOP_RECURRING",
]


@dataclass(frozen=True)
class Route:
    intent: Intent
    confidence: float
    source: Literal["rules", "fallback", "llm"] = "rules"
    flags: frozenset[str] = field(default_factory=frozenset)


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.casefold())
    stripped = "".join(
        char for char in decomposed if unicodedata.category(char) != "Mn"
    )
    return re.sub(r"\s+", " ", stripped.replace("đ", "d")).strip()


def has_diacritics(text: str) -> bool:
    """True when the user typed Vietnamese accents (or đ)."""
    lowered = re.sub(r"\s+", " ", text.casefold()).strip()
    return normalize(text) != lowered


def accent_aware_search(
    message: str, accented: str, plain: str, english: str | None = None
) -> bool:
    """Match Vietnamese keywords without letting accent stripping merge words.

    Stripping accents maps "chắn" (as in "chắc chắn") and "chán" (bored) to the
    same "chan". When the user typed accents, match the accented forms against
    the original text; only unaccented input falls back to the plain forms.
    English keywords never carry accents and are always matched plainly.
    """
    text = normalize(message)
    if english and re.search(english, text):
        return True
    if has_diacritics(message):
        original = unicodedata.normalize("NFC", message.casefold())
        return bool(re.search(accented, original))
    return bool(re.search(plain, text))


# Vietnamese words cannot use \b around accented letters reliably across
# normalization forms, so these patterns bound words with explicit lookarounds.
_W = r"(?<![\w])"
_E = r"(?![\w])"
PLAN_KEYWORDS_RE = (
    r"\b(len ke hoach|lap lich|xep lich|plan my day|schedule my day|sap xep lich"
    r"|sap xep viec|plan my week|schedule my week)\b"
)
RECURRENCE_RE = (
    r"\b(moi ngay|hang ngay|ngay nao cung|hang tuan|moi tuan|every day|everyday|daily"
    r"|weekly|every week|every (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
    r"|moi thu (?:[2-7]|hai|ba|tu|nam|sau|bay)|moi chu nhat)\b"
)
RECURRING_NOUN_RE = (
    r"\b(viec lap lai|lich lap lai|lap lai|recurring|repeating|repeat)\b"
)
DAY_TARGET_RE = (
    r"\b(today|tomorrow|hom nay|ngay mai|"
    r"monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
    r"thu [2-7]|chu nhat|\d{4}-\d{2}-\d{2})\b"
)
SCHEDULING_DETAIL_RE = (
    r"\b\d+(?:\.\d+)?\s*(?:minutes?|mins?|hours?|hrs?|phut|gio|tieng|p|h)\b"
    r"|\b(?:from|tu)\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?\s+(?:to|den)\s+"
    r"\d{1,2}(?::\d{2})?\s*(?:am|pm)?\b"
)
GOAL_TARGET_DATE_RE = (
    r"(?:20\d{2}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/20\d{2}|"
    r"(?:january|february|march|april|may|june|july|august|september|october|"
    r"november|december)\s+\d{1,2}(?:st|nd|rd|th)?(?:,)?\s+20\d{2})"
)

ROUTER_SYSTEM_PROMPT = """Classify only the latest user intent. Reply with one JSON intent.
Never execute an action. A short bare imperative describing concrete work that could become
a task is PLAN_DAY even when it has no date or duration (for example, 'Organize project
materials.', 'Review lecture notes.', or 'Clean my desk.'). A personal opinion or casual
observation is CHITCHAT (for example, 'I like organizing things.'). Questions about what
the assistant can do are HELP_FEATURE, acknowledgements are THANKS, and requests for a
long-term outcome or roadmap are CREATE_GOAL. Do not classify every request containing an
action verb as PLAN_DAY; consider whether the user is naming work for their own plan."""


def _looks_like_bare_task_statement(text: str) -> bool:
    """Identify grammar-shaped task commands without maintaining a task-verb lexicon.

    This deliberately remains low confidence so the semantic classifier can distinguish
    commands from terse casual remarks. Its fallback bias preserves a plausible task when
    that classifier is unavailable instead of silently sending it to chitchat.
    """
    words = re.findall(r"[a-z0-9']+", text)
    if not 2 <= len(words) <= 12 or "?" in text:
        return False
    if words[0] in {
        "i",
        "i'm",
        "im",
        "we",
        "we're",
        "were",
        "my",
        "our",
        "what",
        "why",
        "when",
        "where",
        "who",
        "how",
        "is",
        "are",
        "do",
        "does",
        "did",
        "can",
        "could",
        "would",
        "should",
        "will",
    }:
        return False
    # Imperative conversation requests commonly address the assistant ("tell me",
    # "explain to me"); they are not statements of the user's own work.
    if len(words) > 1 and words[1] in {"me", "us", "chuyen"}:
        return False
    return True


def detect_lang(text: str) -> Literal["vi", "en"]:
    if any(char in text.lower() for char in "ăâđêôơư"):
        return "vi"
    plain = normalize(text)
    if re.search(
        r"\b(hom nay|toi|ban|cua|giup|lich|viec|muc tieu|cam on|xin chao)\b", plain
    ):
        return "vi"
    return "en"


def is_self_contained_day_plan(message: str) -> bool:
    text = normalize(message)
    return bool(
        re.search(DAY_TARGET_RE, text) and re.search(SCHEDULING_DETAIL_RE, text)
    )


def is_explicit_goal_request(message: str) -> bool:
    """Recognize goal creation phrasing independently of current draft state."""
    text = normalize(message)
    goal_opening = re.search(
        r"\b(?:i want to|my goal is to|create (?:a )?goal to)\s+"
        r"(?:finish|complete|achieve|build|learn|launch|become|earn|write|deliver)\b",
        text,
    )
    if goal_opening and re.search(rf"\bby\s+{GOAL_TARGET_DATE_RE}\b", text):
        return True
    # "Tôi muốn học xong IELTS trước 31/12/2026": a wish with a deadline.
    vi_opening = re.search(
        r"\b(?:toi|minh|em)\s+muon\b|\bmuc tieu (?:cua (?:toi|minh) )?la\b", text
    )
    return bool(
        vi_opening
        and re.search(rf"\b(?:truoc|den|vao|han|by)\s+(?:ngay\s+)?{GOAL_TARGET_DATE_RE}\b", text)
    )


def route(
    message: str, *, has_draft: bool = False, awaiting_answer: bool = False
) -> Route:
    text = normalize(message)
    words = text.split()
    flags = set()
    if has_draft:
        flags.add("has_draft")
    if awaiting_answer:
        flags.add("awaiting_answer")
    if "tự tử" in message.casefold() or re.search(
        r"\b(tu hai|muon chet|khong muon song|suicide|suicidal|kill myself|hurt myself|self harm|want to die|end my life)\b",
        text,
    ):
        return Route("CRISIS", 1.0, flags=frozenset(flags))
    mood = accent_aware_search(
        message,
        accented=rf"{_W}(mệt|chán|căng thẳng|áp lực|kiệt sức|buồn ngủ|uể oải|oải){_E}",
        plain=r"\b(met|(?<!chac )chan|cang thang|ap luc|kiet suc|buon ngu|ue oai)\b",
        english=r"\b(stress|stressed|tired|exhausted|burned out|burnt out)\b",
    )
    if mood:
        flags.add("tired")
    planning = bool(re.search(PLAN_KEYWORDS_RE, text))
    # A complete goal declaration starts a new roadmap and is independent of
    # any Today draft. Keep it ahead of all draft-edit heuristics.
    if is_explicit_goal_request(message):
        return Route("CREATE_GOAL", 0.95, flags=frozenset(flags))
    if re.search(RECURRING_NOUN_RE, text) or re.search(RECURRENCE_RE, text):
        # "bo" alone would also match "chạy bộ mỗi ngày" (jog every day).
        stop = accent_aware_search(
            message,
            accented=rf"{_W}(dừng|ngừng|hủy|huỷ|bỏ|xóa|xoá|tắt){_E}",
            plain=r"\b(dung|ngung|huy|(?<!chay )bo|xoa|tat)\b",
            english=r"\b(stop|cancel|remove|delete|end)\b",
        )
        if stop and not re.search(
            r"\b\d+\s*(?:p|phut|minutes?|mins?|h|gio|tieng)\b", text
        ):
            return Route("STOP_RECURRING", 0.9, flags=frozenset(flags))
        if re.search(RECURRING_NOUN_RE, text) and re.search(
            r"\b(nao|gi|cua toi|dang co|list|show|my|what|which|xem|liet ke)\b", text
        ):
            return Route("STATUS_RECURRING", 0.9, flags=frozenset(flags))
    if has_draft and re.search(
        r"\b(doi|sua|bo|xoa|them|keo|giam|tang|change|edit|remove|delete|add|shorten|extend)\b",
        text,
    ):
        return Route("EDIT_DRAFT", 0.95, flags=frozenset(flags))
    if re.search(
        r"\b(hom nay|today)\b.*\b(co gi|con gi|lam gi|tasks?|lich|ke hoach|schedule|plan)\b|\b(next task|viec tiep theo|viec ke tiep|what do i have today)\b",
        text,
    ):
        if not re.search(r"\b(lap lich|len ke hoach|plan my day)\b", text):
            return Route("STATUS_TODAY", 0.92, flags=frozenset(flags))
    garden_noun = accent_aware_search(
        message,
        accented=rf"{_W}(nước|vườn|cây|leaves|water){_E}",
        plain=r"\b(nuoc|vuon|cay)\b",
        english=r"\b(water|leaves|leaf|garden)\b",
    )
    # "có" is deliberately not a question word here: "Tôi có hẹn uống nước"
    # is an appointment, not a garden balance question.
    if (
        garden_noun
        and re.search(
            r"\b(bao nhieu|con|balance|how many|garden|the nao|status|my|cua toi)\b",
            text,
        )
        and not re.search(r"\b(uong nuoc|drink)\b", text)
    ):
        return Route("STATUS_GARDEN", 0.91, flags=frozenset(flags))
    if not planning and re.search(
        r"\b(thong ke|statistics|stats|bao nhieu gio|how many hours|this week|tuan nay)\b",
        text,
    ):
        return Route("STATUS_STATS", 0.9, flags=frozenset(flags))
    if re.search(
        r"\bmuc tieu\b.*\b(cua toi|hien tai|con|tiep theo|sap toi)\b"
        r"|\bmilestone\b.*\b(tiep theo|sap toi)\b"
        r"|\b(?:goal|milestone)s?\b.*\b(current|next|status)\b"
        r"|\b(my goals?|my current goal|current goals?|next milestone)\b",
        text,
    ):
        return Route("STATUS_GOALS", 0.9, flags=frozenset(flags))
    if re.search(
        r"\b(pomodoro|water|leaves|reality check|vitality|replan|growth)\b.*\b(la gi|de lam gi|hoat dong|nghia|what|how|mean)\b|\bwhat (?:is|are) (?:pomodoro|water|leaves|vitality|reality check)\b|\b(ban la ai|ban lam duoc gi|what can you (?:do|help(?: me)? (?:with|plan))|how can you help(?: me)?)\b",
        text,
    ):
        return Route("HELP_FEATURE", 0.9, flags=frozenset(flags))
    if planning:
        return Route("PLAN_DAY", 0.94, flags=frozenset(flags))
    # A day target plus concrete scheduling detail is a self-contained new
    # plan, even when a draft exists. Keep this ahead of the has-draft edit
    # fallback so stale draft state cannot hijack an explicit replacement.
    if is_self_contained_day_plan(message):
        return Route("PLAN_DAY", 0.9, flags=frozenset(flags))
    if re.search(RECURRENCE_RE, text) and re.search(
        r"\b\d+\s*(?:p|phut|minutes?|mins?|h|gio|tieng)\b|\b(hoc|lam|doc|tap|study|read|work|practice|exercise)\b",
        text,
    ):
        return Route("PLAN_DAY", 0.85, flags=frozenset(flags))
    if re.search(r"\b(plan|schedule|scheduling)\b", text) and len(words) > 1:
        return Route("PLAN_DAY", 0.85, flags=frozenset(flags))
    if re.search(r"\b(i have|i only have|toi co)\b", text) and re.search(
        r"\b(hours?|minutes?|gio|phut|tasks?|viec)\b", text
    ):
        return Route("PLAN_DAY", 0.75, flags=frozenset(flags))
    if re.search(r"\b(split|how long|chia nho|bao lau)\b", text) and re.search(
        r"\b(study|homework|task|work|session|viec|hoc)\b", text
    ):
        return Route("PLAN_DAY", 0.75, flags=frozenset(flags))
    if re.search(r"\b(muc tieu|goal|roadmap|lo trinh|long term)\b", text):
        return Route("CREATE_GOAL", 0.88, flags=frozenset(flags))
    if mood and len(words) <= 12:
        return Route("MOOD", 0.9, flags=frozenset(flags))
    if re.search(r"\b(lap|plan|schedule|study|hoc|lam)\b", text) and re.search(
        r"\b\d+\s*(?:p|phut|minutes?|mins?|h|gio|tieng)\b", text
    ):
        return Route("PLAN_DAY", 0.8, flags=frozenset(flags))
    if len(re.findall(r"\b\d+\s*(?:p|phut|minutes?|mins?|h|gio|tieng)\b", text)) >= 2:
        return Route("PLAN_DAY", 0.8, flags=frozenset(flags))
    if len(words) <= 6 and re.match(r"^(hi|hello|hey|xin chao|chao|alo)\b", text):
        return Route("GREETING", 0.98, flags=frozenset(flags))
    if len(words) <= 8 and re.search(r"\b(cam on|thanks|thank you|tks)\b", text):
        return Route("THANKS", 0.98, flags=frozenset(flags))
    if has_draft:
        return Route("EDIT_DRAFT", 0.5, "fallback", frozenset(flags))
    if re.search(r"\b\d+\s*(?:p|phut|minutes?|mins?|h|gio|tieng)\b", text):
        return Route("PLAN_DAY", 0.5, "fallback", frozenset(flags))
    if _looks_like_bare_task_statement(text):
        return Route("PLAN_DAY", 0.55, "fallback", frozenset(flags))
    return Route("CHITCHAT", 0.5, "fallback", frozenset(flags))


class IntentClassification(BaseModel):
    intent: Literal[
        "GREETING",
        "THANKS",
        "STATUS_TODAY",
        "STATUS_GARDEN",
        "STATUS_STATS",
        "STATUS_GOALS",
        "HELP_FEATURE",
        "PLAN_DAY",
        "CREATE_GOAL",
        "EDIT_DRAFT",
        "MOOD",
        "CHITCHAT",
        "STATUS_RECURRING",
    ]


async def classify_low_confidence(
    message: str, fallback: Route, db, user_id, history: list[dict] | None = None
) -> Route:
    """Use a small model only after deterministic routing is uncertain."""
    if fallback.confidence >= 0.7 or fallback.intent == "CRISIS":
        return fallback
    from app.ai.llm.budget import BudgetMode, available_routes, get_budget_mode
    from app.ai.llm.providers import LLMError, llm_provider
    from app.core.config import settings

    if await get_budget_mode(db, user_id, "ROUTER") == BudgetMode.RULES_ONLY:
        return fallback
    routes = await available_routes(db, settings.AI_ROUTE_ROUTER)
    if not routes:
        return fallback
    try:
        result = await llm_provider.call(
            routes,
            [
                {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
                *(history or [])[-4:],
                {"role": "user", "content": message},
            ],
            require_json=True,
            json_schema=IntentClassification.model_json_schema(),
            max_tokens=80,
            db=db,
            user_id=user_id,
            purpose="ROUTER",
        )
        intent = IntentClassification.model_validate(result).intent
        return Route(intent, 0.75, "llm", fallback.flags)
    except (LLMError, ValueError):
        return fallback
