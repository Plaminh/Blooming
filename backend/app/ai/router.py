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


def detect_lang(text: str) -> Literal["vi", "en"]:
    if any(char in text.lower() for char in "ăâđêôơư"):
        return "vi"
    plain = normalize(text)
    if re.search(
        r"\b(hom nay|toi|ban|cua|giup|lich|viec|muc tieu|cam on|xin chao)\b", plain
    ):
        return "vi"
    return "en"


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
    mood = bool(
        re.search(
            r"\b(met|chan|stress|stressed|ap luc|kiet suc|buon ngu|tired|exhausted|burned out)\b",
            text,
        )
    )
    if mood:
        flags.add("tired")
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
    if re.search(r"\b(water|nuoc|leaves|leaf|vuon|cay)\b", text) and re.search(
        r"\b(bao nhieu|con|co|balance|how many|garden|the nao|status|my|cua toi)\b",
        text,
    ):
        return Route("STATUS_GARDEN", 0.91, flags=frozenset(flags))
    if re.search(
        r"\b(thong ke|statistics|stats|bao nhieu gio|how many hours|this week|tuan nay)\b",
        text,
    ):
        return Route("STATUS_STATS", 0.9, flags=frozenset(flags))
    if re.search(
        r"\b(muc tieu|goal|milestone)\b.*\b(cua toi|hien tai|con|tiep theo|sap toi|my|current|next|status)\b|\b(my current goal|next milestone)\b",
        text,
    ):
        return Route("STATUS_GOALS", 0.9, flags=frozenset(flags))
    if re.search(
        r"\b(pomodoro|water|leaves|reality check|vitality|replan|growth)\b.*\b(la gi|de lam gi|hoat dong|nghia|what|how|mean)\b|\bwhat (?:is|are) (?:pomodoro|water|leaves|vitality|reality check)\b|\b(ban la ai|ban lam duoc gi|what can you do)\b",
        text,
    ):
        return Route("HELP_FEATURE", 0.9, flags=frozenset(flags))
    if re.search(
        r"\b(len ke hoach|lap lich|xep lich|plan my day|schedule my day|sap xep lich|sap xep viec)\b",
        text,
    ):
        return Route("PLAN_DAY", 0.94, flags=frozenset(flags))
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
        r"\b\d+\s*(?:p|phut|min|h|gio|tieng)\b", text
    ):
        return Route("PLAN_DAY", 0.8, flags=frozenset(flags))
    if len(re.findall(r"\b\d+\s*(?:p|phut|min|h|gio|tieng)\b", text)) >= 2:
        return Route("PLAN_DAY", 0.8, flags=frozenset(flags))
    if len(words) <= 6 and re.match(r"^(hi|hello|hey|xin chao|chao|alo)\b", text):
        return Route("GREETING", 0.98, flags=frozenset(flags))
    if len(words) <= 8 and re.search(r"\b(cam on|thanks|thank you|tks)\b", text):
        return Route("THANKS", 0.98, flags=frozenset(flags))
    if has_draft:
        return Route("EDIT_DRAFT", 0.5, "fallback", frozenset(flags))
    if re.search(r"\b\d+\s*(?:p|phut|min|h|gio|tieng)\b", text):
        return Route("PLAN_DAY", 0.5, "fallback", frozenset(flags))
    return Route("CHITCHAT", 0.5, "fallback", frozenset(flags))


class IntentClassification(BaseModel):
    intent: Literal["GREETING", "THANKS", "STATUS_TODAY", "STATUS_GARDEN", "STATUS_STATS", "STATUS_GOALS", "HELP_FEATURE", "PLAN_DAY", "CREATE_GOAL", "EDIT_DRAFT", "MOOD", "CHITCHAT"]


async def classify_low_confidence(message: str, fallback: Route, db, user_id, history: list[dict] | None = None) -> Route:
    """Use a small model only after deterministic routing is uncertain."""
    if fallback.confidence >= 0.7 or fallback.intent == "CRISIS":
        return fallback
    from app.ai.budget import BudgetMode, available_routes, get_budget_mode
    from app.ai.providers import LLMError, llm_provider
    from app.core.config import settings

    if await get_budget_mode(db, user_id, "ROUTER") == BudgetMode.RULES_ONLY:
        return fallback
    routes = await available_routes(db, settings.AI_ROUTE_ROUTER)
    if not routes:
        return fallback
    try:
        result = await llm_provider.call(
            routes,
            [{"role": "system", "content": "Classify only the latest user intent. Reply with one JSON intent. Never execute an action."},
             *(history or [])[-4:], {"role": "user", "content": message}],
            require_json=True, json_schema=IntentClassification.model_json_schema(),
            max_tokens=80, db=db, user_id=user_id, purpose="ROUTER",
        )
        intent = IntentClassification.model_validate(result).intent
        return Route(intent, 0.75, "llm", fallback.flags)
    except (LLMError, ValueError):
        return fallback
