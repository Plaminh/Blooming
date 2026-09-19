from datetime import datetime
from typing import List, Optional, Literal, Generic, TypeVar, Union, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator

T = TypeVar("T")

class InferredValue(BaseModel, Generic[T]):
    model_config = ConfigDict(extra="forbid")
    
    value: T
    source: Literal["USER", "EXTRACTED", "AI_ESTIMATE", "DEFAULT"] = Field(
        description="Provenance of this value"
    )
    confidence: Optional[float] = Field(None, description="Confidence if estimated")

class AIRequestContext(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    user_input: str = Field(..., description="The raw natural language input from the user.")
    context_type: Literal["today_planning", "roadmap_planning"] = Field(
        ..., description="The context type for planning."
    )
    current_time: datetime = Field(..., description="The deterministic current time anchored in user's timezone.")
    timezone: str = Field(..., description="The user's local timezone (e.g. 'America/New_York').")

class ValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    provider_used: Optional[str] = None
    latency_ms: Optional[int] = None

class TaskDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    title: str = Field(..., description="The extracted task name.")
    duration_min: Optional[InferredValue[int]] = Field(None, description="Estimated duration in minutes.")
    priority: Optional[InferredValue[Literal["P1", "P2", "P3"]]] = Field(None, description="Priority level.")
    deadline: Optional[InferredValue[datetime]] = Field(None, description="Task deadline if present.")
    is_core: Optional[InferredValue[bool]] = Field(None, description="Is this task core or optional?")
    is_fixed: Optional[InferredValue[bool]] = Field(None, description="Fixed scheduling vs flexible.")
    dependencies: List[str] = Field(default_factory=list, description="Task titles this depends on.")

class TodayDraftProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    tasks: List[TaskDraft] = Field(..., description="List of proposed tasks for today.")

class MilestoneDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    title: str = Field(..., description="Milestone title.")
    target_date: Optional[InferredValue[datetime]] = Field(None, description="Proposed target date.")

class RoadmapDraftProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    goal_title: str = Field(..., description="The overarching goal.")
    milestones: List[MilestoneDraft] = Field(..., description="Proposed milestones with target dates.")

class TodayAIInterpretation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    status: Literal["DRAFT", "NEEDS_CLARIFICATION"] = Field(..., description="Whether a valid draft is returned or clarification is needed.")
    questions: Optional[List[str]] = Field(None, description="Questions if status is NEEDS_CLARIFICATION")
    proposal: Optional[TodayDraftProposal] = Field(None, description="The proposal if status is DRAFT")

    @model_validator(mode="after")
    def validate_semantics(self) -> 'TodayAIInterpretation':
        if self.status == "DRAFT":
            if not self.proposal:
                raise ValueError("proposal is required when status is DRAFT")
            if self.questions is not None and len(self.questions) > 0:
                raise ValueError("questions must be empty or None when status is DRAFT")
        elif self.status == "NEEDS_CLARIFICATION":
            if not self.questions:
                raise ValueError("questions are required and non-empty when status is NEEDS_CLARIFICATION")
            if self.proposal is not None:
                raise ValueError("proposal must be absent when status is NEEDS_CLARIFICATION")
        return self

class RoadmapAIInterpretation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    status: Literal["DRAFT", "NEEDS_CLARIFICATION"] = Field(..., description="Whether a valid draft is returned or clarification is needed.")
    questions: Optional[List[str]] = Field(None, description="Questions if status is NEEDS_CLARIFICATION")
    proposal: Optional[RoadmapDraftProposal] = Field(None, description="The proposal if status is DRAFT")

    @model_validator(mode="after")
    def validate_semantics(self) -> 'RoadmapAIInterpretation':
        if self.status == "DRAFT":
            if not self.proposal:
                raise ValueError("proposal is required when status is DRAFT")
            if self.questions is not None and len(self.questions) > 0:
                raise ValueError("questions must be empty or None when status is DRAFT")
        elif self.status == "NEEDS_CLARIFICATION":
            if not self.questions:
                raise ValueError("questions are required and non-empty when status is NEEDS_CLARIFICATION")
            if self.proposal is not None:
                raise ValueError("proposal must be absent when status is NEEDS_CLARIFICATION")
        return self
