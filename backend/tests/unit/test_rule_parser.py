import pytest
from datetime import datetime
import zoneinfo
from app.services.rule_parser import RuleParser
from app.models.ai_schemas import AIRequestContext

def test_rule_parser_task_draft():
    parser = RuleParser()
    req = AIRequestContext(
        user_input="task: Clean desk, 30m", 
        context_type="today_planning",
        current_time=datetime.now(zoneinfo.ZoneInfo("UTC")),
        timezone="UTC"
    )
    result = parser.parse(req)
    assert result is not None
    assert result["tasks"][0]["title"] == "Clean desk"
    assert result["tasks"][0]["duration_min"]["value"] == 30

def test_rule_parser_unresolved():
    parser = RuleParser()
    req = AIRequestContext(
        user_input="plan my day", 
        context_type="today_planning",
        current_time=datetime.now(zoneinfo.ZoneInfo("UTC")),
        timezone="UTC"
    )
    result = parser.parse(req)
    assert result is None

def test_rule_parser_ignores_roadmap_context():
    parser = RuleParser()
    req = AIRequestContext(
        user_input="task: Clean desk, 30m",
        context_type="roadmap_planning",
        current_time=datetime.now(zoneinfo.ZoneInfo("UTC")),
        timezone="UTC"
    )
    result = parser.parse(req)
    assert result is None
