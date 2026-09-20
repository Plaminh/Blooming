"""Manual fixed-prompt model evaluation. Defaults to local Ollama."""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.ai.providers import LLMError, llm_provider  # noqa: E402
from app.ai.drafts import assemble_today  # noqa: E402
from app.ai.handlers.planner import LLMDayPlan, _parsed_from_llm  # noqa: E402
from app.ai.parser import parse  # noqa: E402
from app.ai.router import route as local_route  # noqa: E402
from app.ai.validators import check_today  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.services.today_service import today_service  # noqa: E402

PROMPTS = [
    "Plan 30 minutes of reading today",
    "Schedule study for one hour at 14:00",
    "Lập lịch học 45 phút",
    "Xếp lịch đọc sách 30p và tập thể dục 40p",
    "I have two hours for a report and email",
    "Plan tomorrow from 09:00 to 12:00",
    "Hôm nay tôi rảnh từ 13h đến 16h",
    "Make cooking optional",
    "Plan a fixed meeting at 10:00",
    "Schedule a report before 17:00",
    "Help me split a long study session",
    "I am unsure how long homework takes",
    "Lập lịch họp 30 phút lúc 9h",
    "Xếp bài tập trước 18h",
    "Plan reading then writing",
    "I only have 45 minutes",
    "Make a realistic day plan",
    "Plan two short tasks and a break",
    "Tôi có ba việc cần làm",
    "Lên kế hoạch ngày mai",
    "Schedule gym after work",
    "Plan lunch and email",
    "Make the second task optional",
    "Move task one to 45 minutes",
    "Create a study plan with assumptions",
    "Plan around a fixed appointment",
    "Lịch của tôi hơi quá tải",
    "Giúp tôi giảm bớt việc không bắt buộc",
    "Plan a calm afternoon",
    "Schedule 60 minutes of coding",
]

EXPECTED_INTENTS = [
    "PLAN_DAY", "PLAN_DAY", "PLAN_DAY", "PLAN_DAY", "PLAN_DAY",
    "PLAN_DAY", "PLAN_DAY", "EDIT_DRAFT", "PLAN_DAY", "PLAN_DAY",
    "PLAN_DAY", "PLAN_DAY", "PLAN_DAY", "PLAN_DAY", "PLAN_DAY",
    "PLAN_DAY", "PLAN_DAY", "PLAN_DAY", "PLAN_DAY", "PLAN_DAY",
    "PLAN_DAY", "PLAN_DAY", "EDIT_DRAFT", "EDIT_DRAFT", "PLAN_DAY",
    "PLAN_DAY", "CHITCHAT", "EDIT_DRAFT", "PLAN_DAY", "PLAN_DAY",
]


def percentile(samples: list[int], percent: float) -> float:
    if not samples:
        return 0.0
    ordered = sorted(samples)
    position = (len(ordered) - 1) * percent
    low = int(position)
    return round(ordered[low] + (ordered[min(low + 1, len(ordered) - 1)] - ordered[low]) * (position - low), 1)


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=("ollama", "groq"), default="ollama")
    parser.add_argument("--offline-only", action="store_true",
        help="Measure deterministic intent and parser coverage without a provider")
    parser.add_argument(
        "--allow-groq",
        action="store_true",
        help="Explicitly allow quota consuming Groq calls",
    )
    args = parser.parse_args()
    if args.provider == "groq" and not args.allow_groq and not args.offline_only:
        parser.error("Groq evaluation requires --allow-groq")
    route = settings.AI_ROUTE_PLANNER if args.provider == "groq" else "ollama:llama3.1"
    assert len(PROMPTS) == len(EXPECTED_INTENTS) == 30
    intent_hits = sum(local_route(prompt, has_draft=expected == "EDIT_DRAFT").intent == expected
        for prompt, expected in zip(PROMPTS, EXPECTED_INTENTS))
    planning_prompts = [prompt for prompt, expected in zip(PROMPTS, EXPECTED_INTENTS) if expected == "PLAN_DAY"]
    parser_hits = sum(bool(parse(prompt).tasks) for prompt in planning_prompts)
    if args.offline_only:
        print(json.dumps({
            "intent_accuracy": round(intent_hits / len(PROMPTS), 3),
            "parser_coverage": round(parser_hits / len(planning_prompts), 3),
            "schema_valid_rate": None,
            "scheduler_valid_rate": None,
            "tokens": None,
            "latency_p50_ms": None,
            "latency_p95_ms": None,
        }, indent=2))
        return 0
    valid = 0
    scheduler_valid = 0
    token_total = 0
    latencies: list[int] = []
    timezone = ZoneInfo("UTC")
    context = SimpleNamespace(now=datetime.now(timezone), timezone=timezone,
        default_date_offset=0, default_windows=(("09:00", "17:00"),),
        break_minutes=5, calibration={})
    llm_provider.init_client()
    try:
        for index, prompt in enumerate(PROMPTS, 1):
            try:
                result = await llm_provider.call(
                    route,
                    [{"role": "system", "content": "Extract a day plan as JSON. Do not claim it is saved."},
                     {"role": "user", "content": prompt}],
                    require_json=True,
                    json_schema=LLMDayPlan.model_json_schema(),
                    max_tokens=800,
                )
                latencies.append(llm_provider.last_latency_ms)
                usage = llm_provider.last_usage
                token_total += int(usage.get("prompt_tokens", 0)) + int(usage.get("completion_tokens", 0))
                plan = LLMDayPlan.model_validate(result)
                valid += 1
                if EXPECTED_INTENTS[index - 1] == "PLAN_DAY":
                    parsed = _parsed_from_llm(plan, context, prompt)
                    draft, _ = assemble_today(parsed, context)
                    if not check_today(draft):
                        today_service._normalize_and_schedule(draft, timezone, draft.planDate, uuid4())
                        scheduler_valid += 1
                print(f"{index:02d}: valid")
            except (LLMError, ValidationError, ValueError, HTTPException) as exc:
                print(f"{index:02d}: {type(exc).__name__}")
    finally:
        await llm_provider.close_client()
    metrics = {
        "intent_accuracy": round(intent_hits / len(PROMPTS), 3),
        "parser_coverage": round(parser_hits / len(planning_prompts), 3),
        "schema_valid_rate": round(valid / len(PROMPTS), 3),
        "scheduler_valid_rate": round(scheduler_valid / len(planning_prompts), 3),
        "tokens": token_total,
        "latency_p50_ms": percentile(latencies, 0.5),
        "latency_p95_ms": percentile(latencies, 0.95),
    }
    print(json.dumps(metrics, indent=2))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
