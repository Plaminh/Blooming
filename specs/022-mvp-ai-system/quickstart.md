# Quickstart Validation Guide: MVP AI System

This guide explains how to validate the AI routing layer locally using isolated backend tests and raw HTTP requests, without needing the full desktop application to run.

## Prerequisites

1. Ensure the Python virtual environment is activated in the `backend/` directory.
2. The `.env` file must contain valid Cloudflare AI Gateway endpoints and API keys for Groq and Gemini.
   ```ini
   AI_GATEWAY_URL="https://gateway.ai.cloudflare.com/v1/{account_id}/blooming-ai"
   CF_AIG_TOKEN="..."
   GROQ_API_KEY="..."
   GROQ_MODEL="openai/gpt-oss-20b"
   GEMINI_API_KEY="..."
   GEMINI_MODEL="gemini-2.5-flash"
   ```
3. Generate a JWT token for a valid test user to use in the `Authorization` header.
4. Start the FastAPI backend:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

## Scenarios

### Scenario 1: Rule-Based Deterministic Fast Path
**Command**:
```bash
curl -X POST "http://localhost:8000/api/v1/planning/draft" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <access_token>" \
     -d '{"user_input": "task: Clean desk, 25m", "context_type": "today_planning"}'
```
**Expected Outcome**: Returns immediately (< 50ms) with `provider_used: "RULE"` and a single TaskDraft.

### Scenario 2: Groq Inference (Primary)
**Command**:
```bash
curl -X POST "http://localhost:8000/api/v1/planning/draft" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <access_token>" \
     -d '{"user_input": "I need to organize my inbox for an hour", "context_type": "today_planning"}'
```
**Expected Outcome**: Structured task draft with `provider_used: "GROQ"` and `source: "EXTRACTED"` for the duration.

### Scenario 3: Gemini Fallback
**Setup**: Set an invalid `GROQ_API_KEY` in `.env` and restart the server.
**Command**: Run the same command as Scenario 2.
**Expected Outcome**: Succeeds with `provider_used: "GEMINI"` and `fallback_triggered: true`.

### Scenario 4: Invalid Schema -> Safe Handling
**Setup**: Set a prompt that forces the LLM to output a badly formatted JSON, or mock it.
**Expected Outcome**: 502 Bad Gateway with `status: error` and code `STRUCTURED_OUTPUT_INVALID`. Application state is left untouched.

### Scenario 5: Needs Clarification
**Command**:
```bash
curl -X POST "http://localhost:8000/api/v1/planning/draft" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <access_token>" \
     -d '{"user_input": "I want to finish some stuff.", "context_type": "roadmap_planning"}'
```
**Expected Outcome**: 200 OK with `status: needs_clarification` from Groq with a question asking for specifics.

### Scenario 6: Both Providers Unavailable
**Setup**: Invalid keys for both Groq and Gemini.
**Expected Outcome**: 503 Service Unavailable with `status: error`, code `AI_SERVICE_UNAVAILABLE`.

### Scenario 7: Unsupported Fields Rejected
Handled by Pydantic's `extra="forbid"`. Test via mock if necessary.

### Scenario 8: Unauthorized Request
**Command**: Omit the `Authorization` header.
**Expected Outcome**: 401 Unauthorized.
