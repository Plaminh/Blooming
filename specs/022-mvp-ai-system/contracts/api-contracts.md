# API Contracts: MVP AI System

This contract defines the integration point between the SvelteKit frontend and the FastAPI backend for AI-assisted planning.

## AI Planning Endpoint

**Endpoint**: `POST /api/v1/planning/draft`
**Description**: Submits natural language input for interpretation. The backend will attempt rule-based parsing, then Groq, then Gemini. Timezone resolution is handled automatically via authenticated `CurrentUser` settings.

### Request Body (JSON)
```json
{
  "user_input": "I want to finish the MVP spec today, which takes about 2 hours, and then review PRs for 1 hour.",
  "context_type": "today_planning"
}
```

### Successful Draft Proposal (200 OK)
Returns a validated draft proposal.

```json
{
  "status": "success",
  "meta": {
    "provider_used": "GROQ",
    "latency_ms": 450,
    "fallback_triggered": false,
    "result_category": "SUCCESS"
  },
  "data": {
    "tasks": [
      {
        "title": "Finish MVP spec",
        "duration_min": { "value": 120, "source": "USER", "confidence": 1.0 },
        "priority": { "value": "P1", "source": "AI_ESTIMATE", "confidence": 0.8 }
      }
    ]
  }
}
```

### Needs Clarification (200 OK)
Returned when the AI recognizes missing required fields or ambiguity (especially in Roadmap planning).

```json
{
  "status": "needs_clarification",
  "meta": {
    "provider_used": "GROQ",
    "fallback_triggered": false,
    "latency_ms": 320,
    "result_category": "NEEDS_CLARIFICATION"
  },
  "clarification": {
    "questions": [
      "Are these tasks meant for today or some time this week?"
    ]
  }
}
```

### Validation Error (422 Unprocessable Entity)
Returned when the generated draft violates business rules, or if the user's timezone configuration is invalid.

```json
{
  "status": "error",
  "meta": {
    "provider_used": "GEMINI",
    "fallback_triggered": true,
    "latency_ms": 1200,
    "result_category": "BUSINESS_VALIDATION_FAILURE"
  },
  "error": {
    "code": "BUSINESS_VALIDATION_FAILURE",
    "message": "AI proposal violates business rules."
  }
}
```

### Invalid AI Output (502 Bad Gateway)
Returned when the AI responds but fails to generate an output matching the required JSON schema, even after fallback.

```json
{
  "status": "error",
  "meta": {
    "provider_used": "GEMINI",
    "fallback_triggered": true,
    "latency_ms": 1500,
    "result_category": "STRUCTURED_OUTPUT_INVALID"
  },
  "error": {
    "code": "STRUCTURED_OUTPUT_INVALID",
    "message": "AI produced an unusable structured format."
  }
}
```

### AI Unavailable / Provider Error (503 Service Unavailable)
If all providers are down:

```json
{
  "status": "error",
  "meta": {
    "provider_used": "GEMINI",
    "fallback_triggered": true,
    "latency_ms": 3500,
    "result_category": "AI_SERVICE_UNAVAILABLE"
  },
  "error": {
    "code": "AI_SERVICE_UNAVAILABLE",
    "message": "AI providers are currently unavailable."
  }
}
```
