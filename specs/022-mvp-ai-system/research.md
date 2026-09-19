# Research: MVP AI System

## AI Gateway Integration

**Decision**: Use `httpx` to make asynchronous HTTP requests to the Cloudflare AI Gateway, rather than installing provider-specific SDKs.

**Rationale**:
- Cloudflare AI Gateway provides a unified REST interface.
- Using `httpx` avoids dependency bloat (no need to install both `groq` and `google-generativeai` packages).
- We already have `httpx` installed for backend HTTP requests.
- The system must parse provider responses and map them into Pydantic models for strict validation.

**Alternatives considered**:
- Installing provider SDKs (`groq`, `google-generativeai`): Rejected due to added dependencies and potential version conflicts, especially when routing all traffic through a custom Cloudflare Gateway URL which can sometimes require SDK hacks.

## Deterministic Rule Parsing

**Decision**: Implement a lightweight rule-based parser in Python using Regex and exact string matching prior to invoking the AI Router.

**Rationale**:
- The feature spec mandates bypassing AI for structured commands like explicit task inputs (`task: <title>, <N>m`).
- A deterministic layer is much faster and more reliable for known commands.

**Alternatives considered**:
- Using an NLP library like `spaCy` or `nltk`: Rejected as it violates the MVP constraint of being lightweight and avoiding unnecessary AI/NLP complexity.

## AI Fallback Mechanism

**Decision**: Implement an `AIProviderRouter` in the backend service layer that orchestrates try-except blocks, calling Groq first and falling back to Gemini on `AIProviderException`, specific `ProviderErrorCategory` failures, or typed Pydantic interpretation validation errors.

**Rationale**:
- Ensures the fallback logic is cleanly encapsulated and isolated from the business logic.
- Directly aligns with the requested routing flow.
