import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.ai_router import AIRouter, AIRouterException
from app.models.ai_schemas import AIRequestContext
from app.services.ai_provider import AIProviderException, ProviderErrorCategory
from datetime import datetime
import zoneinfo

@pytest.fixture
def req_context():
    return AIRequestContext(
        user_input="test",
        context_type="today_planning",
        current_time=datetime.now(zoneinfo.ZoneInfo("UTC")),
        timezone="UTC"
    )

@pytest.fixture
def mocks():
    rule_parser = MagicMock()
    rule_parser.parse.return_value = None
    business_validator = MagicMock()
    business_validator.validate.return_value = (True, None)
    groq = AsyncMock()
    gemini = AsyncMock()
    return rule_parser, business_validator, groq, gemini

@pytest.fixture
def router(mocks):
    return AIRouter(*mocks)

@pytest.mark.asyncio
async def test_rule_success(router, req_context, mocks):
    rp, _, groq, gemini = mocks
    rp.parse.return_value = {"tasks": [{"title": "test"}]}
    res = await router.generate_draft(req_context)
    assert res["status"] == "success"
    assert res["meta"]["provider_used"] == "RULE"
    groq.invoke.assert_not_called()
    gemini.invoke.assert_not_called()

@pytest.mark.asyncio
async def test_groq_draft_success(router, req_context, mocks):
    rp, _, groq, gemini = mocks
    groq.invoke.return_value = {
        "status": "DRAFT",
        "proposal": {"tasks": [{"title": "T"}]}
    }
    res = await router.generate_draft(req_context)
    assert res["status"] == "success"
    assert res["meta"]["provider_used"] == "GROQ"
    gemini.invoke.assert_not_called()

@pytest.mark.asyncio
async def test_groq_timeout_fallback(router, req_context, mocks):
    rp, _, groq, gemini = mocks
    groq.invoke.side_effect = AIProviderException(ProviderErrorCategory.TIMEOUT, "Timeout")
    gemini.invoke.return_value = {
        "status": "DRAFT",
        "proposal": {"tasks": [{"title": "T"}]}
    }
    res = await router.generate_draft(req_context)
    assert res["status"] == "success"
    assert res["meta"]["provider_used"] == "GEMINI"
    assert res["meta"]["fallback_triggered"] is True

@pytest.mark.asyncio
async def test_groq_auth_failure_fallback(router, req_context, mocks):
    rp, _, groq, gemini = mocks
    groq.invoke.side_effect = AIProviderException(ProviderErrorCategory.AUTH_ERROR, "Auth")
    gemini.invoke.return_value = {
        "status": "DRAFT",
        "proposal": {"tasks": [{"title": "T"}]}
    }
    res = await router.generate_draft(req_context)
    assert res["status"] == "success"
    assert res["meta"]["provider_used"] == "GEMINI"
    assert res["meta"]["fallback_triggered"] is True

@pytest.mark.asyncio
async def test_groq_malformed_output_fallback(router, req_context, mocks):
    rp, _, groq, gemini = mocks
    groq.invoke.side_effect = AIProviderException(ProviderErrorCategory.MALFORMED_RESPONSE, "Malformed")
    gemini.invoke.return_value = {
        "status": "DRAFT",
        "proposal": {"tasks": [{"title": "T"}]}
    }
    res = await router.generate_draft(req_context)
    assert res["status"] == "success"

@pytest.mark.asyncio
async def test_groq_invalid_structured_schema_fallback(router, req_context, mocks):
    rp, _, groq, gemini = mocks
    groq.invoke.return_value = {"invalid": "data"}
    gemini.invoke.return_value = {
        "status": "DRAFT",
        "proposal": {"tasks": [{"title": "T"}]}
    }
    res = await router.generate_draft(req_context)
    assert res["status"] == "success"
    assert res["meta"]["provider_used"] == "GEMINI"
    assert res["meta"]["fallback_triggered"] is True

@pytest.mark.asyncio
async def test_valid_clarification_no_fallback(router, req_context, mocks):
    rp, _, groq, gemini = mocks
    groq.invoke.return_value = {
        "status": "NEEDS_CLARIFICATION",
        "questions": ["Q?"]
    }
    res = await router.generate_draft(req_context)
    assert res["status"] == "needs_clarification"
    assert res["clarification"]["questions"] == ["Q?"]
    assert res["meta"]["provider_used"] == "GROQ"
    gemini.invoke.assert_not_called()

@pytest.mark.asyncio
async def test_business_invalid_no_fallback(router, req_context, mocks):
    rp, bv, groq, gemini = mocks
    groq.invoke.return_value = {
        "status": "DRAFT",
        "proposal": {"tasks": [{"title": "T"}]}
    }
    bv.validate.return_value = (False, "Bad")
    with pytest.raises(AIRouterException) as exc:
        await router.generate_draft(req_context)
    assert exc.value.status_code == 422
    assert exc.value.provider_used == "GROQ"
    gemini.invoke.assert_not_called()

@pytest.mark.asyncio
async def test_gemini_failure_after_fallback(router, req_context, mocks):
    rp, _, groq, gemini = mocks
    groq.invoke.side_effect = AIProviderException(ProviderErrorCategory.TIMEOUT, "Timeout")
    gemini.invoke.side_effect = AIProviderException(ProviderErrorCategory.TIMEOUT, "Timeout")
    with pytest.raises(AIRouterException) as exc:
        await router.generate_draft(req_context)
    assert exc.value.status_code == 503
    assert exc.value.provider_used == "GEMINI"

@pytest.mark.asyncio
async def test_unusable_gemini_structured_output(router, req_context, mocks):
    rp, _, groq, gemini = mocks
    groq.invoke.return_value = {"invalid": "data"}
    gemini.invoke.return_value = {"invalid": "data"}
    with pytest.raises(AIRouterException) as exc:
        await router.generate_draft(req_context)
    assert exc.value.status_code == 502
    assert exc.value.provider_used == "GEMINI"

@pytest.mark.asyncio
async def test_roadmap_clarification(router, req_context, mocks):
    req_context.context_type = "roadmap_planning"
    rp, _, groq, gemini = mocks
    groq.invoke.return_value = {
        "status": "NEEDS_CLARIFICATION",
        "questions": ["Q?"]
    }
    res = await router.generate_draft(req_context)
    assert res["status"] == "needs_clarification"

@pytest.mark.asyncio
async def test_roadmap_success(router, req_context, mocks):
    req_context.context_type = "roadmap_planning"
    rp, _, groq, gemini = mocks
    groq.invoke.return_value = {
        "status": "DRAFT",
        "proposal": {"goal_title": "G", "milestones": [{"title": "M"}]}
    }
    res = await router.generate_draft(req_context)
    assert res["status"] == "success"

def test_today_schema_semantics():
    from app.models.ai_schemas import TodayAIInterpretation
    from pydantic import ValidationError
    
    # Today DRAFT with proposal -> valid
    TodayAIInterpretation.model_validate({"status": "DRAFT", "proposal": {"tasks": []}})
    
    # Today DRAFT without proposal -> invalid
    with pytest.raises(ValidationError):
        TodayAIInterpretation.model_validate({"status": "DRAFT"})
        
    # Today NEEDS_CLARIFICATION with questions -> valid
    TodayAIInterpretation.model_validate({"status": "NEEDS_CLARIFICATION", "questions": ["Q"]})
    
    # Today NEEDS_CLARIFICATION without questions -> invalid
    with pytest.raises(ValidationError):
        TodayAIInterpretation.model_validate({"status": "NEEDS_CLARIFICATION"})
        
    # Today NEEDS_CLARIFICATION with proposal -> invalid
    with pytest.raises(ValidationError):
        TodayAIInterpretation.model_validate({"status": "NEEDS_CLARIFICATION", "questions": ["Q"], "proposal": {"tasks": []}})
        
    # Extra fields rejected
    with pytest.raises(ValidationError):
        TodayAIInterpretation.model_validate({"status": "DRAFT", "proposal": {"tasks": []}, "extra": "field"})

def test_roadmap_schema_semantics():
    from app.models.ai_schemas import RoadmapAIInterpretation
    from pydantic import ValidationError
    
    # Roadmap DRAFT with proposal -> valid
    RoadmapAIInterpretation.model_validate({"status": "DRAFT", "proposal": {"goal_title": "G", "milestones": []}})
    
    # Roadmap DRAFT without proposal -> invalid
    with pytest.raises(ValidationError):
        RoadmapAIInterpretation.model_validate({"status": "DRAFT"})
        
    # Roadmap NEEDS_CLARIFICATION with questions -> valid
    RoadmapAIInterpretation.model_validate({"status": "NEEDS_CLARIFICATION", "questions": ["Q"]})
    
    # Roadmap NEEDS_CLARIFICATION without questions -> invalid
    with pytest.raises(ValidationError):
        RoadmapAIInterpretation.model_validate({"status": "NEEDS_CLARIFICATION"})
        
    # Roadmap NEEDS_CLARIFICATION with proposal -> invalid
    with pytest.raises(ValidationError):
        RoadmapAIInterpretation.model_validate({"status": "NEEDS_CLARIFICATION", "questions": ["Q"], "proposal": {"goal_title": "G", "milestones": []}})
        
    # Extra fields rejected
    with pytest.raises(ValidationError):
        RoadmapAIInterpretation.model_validate({"status": "DRAFT", "proposal": {"goal_title": "G", "milestones": []}, "extra": "field"})

@pytest.mark.asyncio
async def test_groq_invalid_schema_then_gemini_timeout_returns_503(req_context):
    groq_mock = AsyncMock()
    gemini_mock = AsyncMock()
    
    # Groq returns something that fails schema validation
    groq_mock.invoke.return_value = {"invalid": "schema"}
    
    # Gemini throws an exception during fallback
    gemini_mock.invoke.side_effect = AIProviderException(ProviderErrorCategory.TIMEOUT, "Timeout")
    
    router = AIRouter(
        rule_parser=MagicMock(parse=MagicMock(return_value=None)),
        business_validator=MagicMock(),
        groq_provider=groq_mock,
        gemini_provider=gemini_mock
    )
    
    with pytest.raises(AIRouterException) as exc:
        await router.generate_draft(req_context)
        
    assert exc.value.status_code == 503
    assert exc.value.code == "AI_SERVICE_UNAVAILABLE"
