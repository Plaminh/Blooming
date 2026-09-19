import time
import logging
from typing import Any, Tuple
from app.models.ai_schemas import AIRequestContext, TodayAIInterpretation, RoadmapAIInterpretation
from app.services.rule_parser import RuleParser
from app.services.business_validator import BusinessValidator
from app.services.groq_provider import GroqProvider
from app.services.gemini_provider import GeminiProvider
from app.services.ai_provider import AIProviderException

logger = logging.getLogger(__name__)

class AIRouterException(Exception):
    def __init__(self, code: str, message: str, status_code: int, provider_used: str, fallback: bool, latency: int):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.provider_used = provider_used
        self.fallback = fallback
        self.latency = latency

class AIRouter:
    def __init__(self, rule_parser=None, business_validator=None, groq_provider=None, gemini_provider=None):
        self.rule_parser = rule_parser or RuleParser()
        self.business_validator = business_validator or BusinessValidator()
        self.groq_provider = groq_provider or GroqProvider()
        self.gemini_provider = gemini_provider or GeminiProvider()

    async def generate_draft(self, request_context: AIRequestContext) -> dict:
        start_time = time.perf_counter()
        
        # 1. Deterministic Rule Parsing
        rule_result = self.rule_parser.parse(request_context)
        
        provider_used = "GROQ"
        fallback_triggered = False
        raw_output = None
        
        if rule_result:
            provider_used = "RULE"
            raw_output = {
                "status": "DRAFT",
                "proposal": rule_result
            }
        else:
            # 2. AI Routing
            try:
                raw_output = await self.groq_provider.invoke(request_context)
            except AIProviderException as e:
                logger.warning(f"Groq failed with {e.category.value}. Falling back to Gemini.")
                fallback_triggered = True
                provider_used = "GEMINI"
                try:
                    raw_output = await self.gemini_provider.invoke(request_context)
                except AIProviderException as e_gemini:
                    logger.error(f"Gemini fallback failed with {e_gemini.category.value}")
                    latency = int((time.perf_counter() - start_time) * 1000)
                    raise AIRouterException(
                        code="AI_SERVICE_UNAVAILABLE",
                        message="AI providers are currently unavailable.",
                        status_code=503,
                        provider_used=provider_used,
                        fallback=fallback_triggered,
                        latency=latency
                    )
            except Exception as e:
                logger.error("Unexpected error in Groq provider")
                fallback_triggered = True
                provider_used = "GEMINI"
                try:
                    raw_output = await self.gemini_provider.invoke(request_context)
                except Exception as e_gemini:
                    logger.error("Unexpected error in Gemini fallback")
                    latency = int((time.perf_counter() - start_time) * 1000)
                    raise AIRouterException(
                        code="AI_SERVICE_UNAVAILABLE",
                        message="AI providers are currently unavailable.",
                        status_code=503,
                        provider_used=provider_used,
                        fallback=fallback_triggered,
                        latency=latency
                    )

        latency_ms = int((time.perf_counter() - start_time) * 1000)
        
        # 3. Pydantic Schema Validation
        is_valid, validated_data = self.validate_schema(raw_output, request_context.context_type)
        if not is_valid:
            if provider_used == "GROQ":
                logger.warning(f"Groq schema invalid. Falling back to Gemini.")
                fallback_triggered = True
                provider_used = "GEMINI"
                try:
                    raw_output = await self.gemini_provider.invoke(request_context)
                    is_valid, validated_data = self.validate_schema(raw_output, request_context.context_type)
                except AIProviderException as e:
                    logger.error(f"Gemini fallback failed on schema retry with {e.category.value}")
                    latency_ms = int((time.perf_counter() - start_time) * 1000)
                    raise AIRouterException(
                        code="AI_SERVICE_UNAVAILABLE",
                        message="AI providers are currently unavailable.",
                        status_code=503,
                        provider_used=provider_used,
                        fallback=fallback_triggered,
                        latency=latency_ms
                    )
                except Exception:
                    logger.error("Gemini fallback failed on schema retry")
                    latency_ms = int((time.perf_counter() - start_time) * 1000)
                    raise AIRouterException(
                        code="AI_SERVICE_UNAVAILABLE",
                        message="AI providers are currently unavailable.",
                        status_code=503,
                        provider_used=provider_used,
                        fallback=fallback_triggered,
                        latency=latency_ms
                    )
            
            if not is_valid:
                latency_ms = int((time.perf_counter() - start_time) * 1000)
                raise AIRouterException(
                    code="STRUCTURED_OUTPUT_INVALID",
                    message="AI produced an unusable structured format.",
                    status_code=502,
                    provider_used=provider_used,
                    fallback=fallback_triggered,
                    latency=latency_ms
                )

        # 4. Check for clarification
        if validated_data.status == "NEEDS_CLARIFICATION":
            return {
                "status": "needs_clarification",
                "meta": {
                    "provider_used": provider_used,
                    "fallback_triggered": fallback_triggered,
                    "latency_ms": latency_ms,
                    "result_category": "NEEDS_CLARIFICATION"
                },
                "clarification": {
                    "questions": validated_data.questions or []
                }
            }

        # 5. Business Validation
        proposal = validated_data.proposal
        if not proposal:
            raise AIRouterException(
                code="STRUCTURED_OUTPUT_INVALID",
                message="AI did not provide a proposal.",
                status_code=502,
                provider_used=provider_used,
                fallback=fallback_triggered,
                latency=latency_ms
            )

        is_bus_valid, bus_err = self.business_validator.validate(proposal, request_context)
        if not is_bus_valid:
            raise AIRouterException(
                code="BUSINESS_VALIDATION_FAILURE",
                message=f"Draft proposal violates business rules.",
                status_code=422,
                provider_used=provider_used,
                fallback=fallback_triggered,
                latency=latency_ms
            )

        return {
            "status": "success",
            "meta": {
                "provider_used": provider_used,
                "fallback_triggered": fallback_triggered,
                "latency_ms": latency_ms,
                "result_category": "SUCCESS"
            },
            "data": proposal.model_dump()
        }

    def validate_schema(self, data: dict, context_type: str) -> Tuple[bool, Any]:
        try:
            if context_type == "today_planning":
                interp = TodayAIInterpretation.model_validate(data)
            elif context_type == "roadmap_planning":
                interp = RoadmapAIInterpretation.model_validate(data)
            else:
                return False, None
            return True, interp
        except Exception:
            return False, None
