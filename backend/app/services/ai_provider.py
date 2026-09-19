import abc
from enum import Enum
from typing import Dict, Any, Optional
from app.models.ai_schemas import AIRequestContext

class ProviderErrorCategory(str, Enum):
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    AUTH_ERROR = "AUTH_ERROR"
    RATE_LIMIT = "RATE_LIMIT"
    TIMEOUT = "TIMEOUT"
    PROVIDER_5XX = "PROVIDER_5XX"
    PROVIDER_4XX = "PROVIDER_4XX"
    NETWORK_ERROR = "NETWORK_ERROR"
    MALFORMED_RESPONSE = "MALFORMED_RESPONSE"
    STRUCTURED_OUTPUT_INVALID = "STRUCTURED_OUTPUT_INVALID"

class AIProviderException(Exception):
    def __init__(self, category: ProviderErrorCategory, message: str):
        super().__init__(message)
        self.category = category

class AIProvider(abc.ABC):
    @abc.abstractmethod
    async def invoke(self, request_context: AIRequestContext) -> Dict[str, Any]:
        """
        Invoke the AI provider with the full request context.
        Returns the raw dictionary (parsed from JSON structure) 
        which will then be validated by Pydantic.
        """
        pass
