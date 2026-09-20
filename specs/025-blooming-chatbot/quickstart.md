# Quickstart & Validation Guide

## Prerequisites & Setup
The project uses standard FastAPI and SvelteKit toolchains.

### Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

## Running Migrations
To safely test the `AiUsageLog` migration locally:
```bash
# Upgrade to head
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Re-upgrade
alembic upgrade head
```

## Automated Testing

### Backend Tests
```bash
# Run complete test suite
pytest

# Phase-focused tests (Examples)
pytest tests/test_providers.py         # Phase 0: Provider Layer
pytest tests/test_router_rules.py      # Phase 2: Router & Rules
pytest tests/test_parser.py            # Phase 3: Deterministic Parser
pytest tests/test_budget.py            # Phase 4: Budget Guard
pytest tests/test_roadmap.py           # Phase 5: Goal Creation
```

### Backend Quality Checks
```bash
# Format and Lint
black app tests
flake8 app tests
mypy app
```

### Frontend Tests
```bash
# Complete frontend tests
npm run test

# Run specific component tests
npm run test -- src/lib/features/mr-bloom/components/molecules/ChatMessage.test.ts
```

### Frontend Quality Checks
```bash
# Type check and lint
npm run check

# Build check
npm run build
```

## Manual Validation

### 1. Ollama-based Smoke Tests (Zero Quota)
Configure `.env` for local LLM inference:
```env
AI_ROUTE_PLANNER=ollama:llama3.1
AI_ROUTE_EDITOR=ollama:llama3.1
```
Send a chat payload requesting a plan. Ensure the backend doesn't crash and generates a draft.

### 2. Groq LLM Evaluation (WARNING: CONSUMES QUOTA)
To measure model capability, run the custom eval script. **Warning: This consumes real provider quota. Monitor your organization's limits.**
```bash
python scripts/eval_chat.py --provider groq
```

### 3. RULES_ONLY Behavior
Force the system into `RULES_ONLY` mode by setting your rolling token budget to 0 in `config.py` or `.env`.
Send: "lên kế hoạch 60p đọc sách"
**Expected Outcome**: The system successfully parses the duration and task name using the deterministic regex parser. A valid draft is returned and no external LLM calls are logged in the console.

### 4. Privacy Check
Check the database contents of the new `ai_usage_log` table:
```sql
SELECT purpose, model, prompt_tokens, outcome FROM ai_usage_log ORDER BY id DESC LIMIT 5;
```
**Expected Outcome**: You should see token counts, model identifiers, and outcomes, but strictly NO raw message text, user prompts, or JSON payloads.
