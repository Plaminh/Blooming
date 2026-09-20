import logging
from typing import Any

from app.schemas.assistant import ChatRequest, ChatResponse
# we will import rules and routers when they are implemented

logger = logging.getLogger(__name__)

async def process_chat(request: ChatRequest) -> ChatResponse:
    # This is a stub for the unified router pipeline entry point
    # We will implement the full router pipeline here later
    
    # Fake response for now to satisfy types
    return ChatResponse(
        reply="Hello! The router pipeline is not yet implemented.",
        session_id=request.session_id,
        tier="RULES"
    )
