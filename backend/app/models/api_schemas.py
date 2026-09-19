from pydantic import BaseModel, Field
from typing import Literal

class PlanningDraftRequest(BaseModel):
    user_input: str = Field(..., description="The raw natural language input from the user.")
    context_type: Literal["today_planning", "roadmap_planning"] = Field(
        ..., description="The context type for planning."
    )
