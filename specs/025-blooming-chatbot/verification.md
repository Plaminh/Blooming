# Verification record

Run on 2026-09-20 in `E:\Blooming` (Windows, Python 3.10.10). No commit or merge was made.

| Command | Result |
| --- | --- |
| `cd backend; pytest -q --tb=short` | 321 passed, 1 existing Starlette deprecation warning |
| `cd backend; python -m ruff check .` | All checks passed |
| `cd backend; python -m mypy app` | No issues in 95 source files |
| `cd backend; alembic current` | `c0f4a891b6e2 (head)` |
| `cd backend; alembic upgrade head; alembic downgrade -1; alembic upgrade head` | All three commands passed; final head confirmed |
| `cd frontend; npm test` | 31 files, 197 tests passed |
| `cd frontend; npm run check` | 0 errors, 0 warnings |
| `cd frontend; npm run lint` | 0 errors, 0 warnings (Svelte diagnostics with warnings treated as failures) |
| `cd frontend; npm run build` | Static build passed |
| `python scripts/eval_chat.py --help` | Passed; Groq requires `--allow-groq` |
| `python scripts/eval_chat.py --offline-only` | Intent accuracy 1.0 and parser coverage 0.92 on the 30 labeled prompts; provider metrics unavailable |

`T051` remains open. The local machine has neither the Ollama command nor a responding service at `localhost:11434`. A default evaluation attempt failed on connection and opened the circuit breaker; no live model quality or token metrics are available. The RULES_ONLY API path was exercised in an automated test with the token budgets set to zero. The target Python 3.11 environment still needs its own run.
