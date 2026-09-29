# ADR 001: Staging Session Lifetime

## Context

In the current implementation, the JWT access token lifetime is set to 30 minutes, and there is no refresh-token endpoint. For a desktop application like Blooming, users may leave the app running in the system tray or let the computer sleep for hours. When a token expires after waking from sleep, it risks forcing the user back to the login screen unnecessarily, which is highly disruptive to staging testing.

## Decision

- **Staging Access Token Lifetime**: Configure the staging environment to use a 24-hour access token (`ACCESS_TOKEN_EXPIRE_MINUTES=1440`).
- **No Refresh Tokens (Block 0)**: Do not implement refresh tokens in this block.
- **Error Handling**: Network, offline, or timeout failures must not be treated as authentication failures (401).

## Rationale

A 24-hour token prevents frustrating logouts during staging review and avoids the immediate complexity of implementing a full refresh-token architecture. The distinction between network errors and authentication errors ensures that waking from sleep without immediate network connectivity does not trigger an accidental logout.

## Consequences & Boundaries

- **Out of Scope**: Implementation of refresh tokens is deferred.
- **Configuration Contract**: `ACCESS_TOKEN_EXPIRE_MINUTES` is documented in the environment template.

## Deferred Work

- **Production Hardening**: Full refresh-token architecture implementation.
- **Later Blocks**: Implementation of a robust reconnect queue for network restoration.

## Acceptance Criteria

- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` is set or documented as 1440 for staging environments.
- [ ] Network timeout and offline errors are clearly decoupled from authentication (401) errors in error handling docs/strategies.
- [ ] Refresh token implementation is explicitly marked as deferred.
