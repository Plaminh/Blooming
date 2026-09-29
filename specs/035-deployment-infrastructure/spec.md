# Feature Specification: Block 3 - Deployment Infrastructure

**Status**: Implemented; Docker/database rehearsal pending environment verification

## Goal

Provide a production-like backend, PostgreSQL migration path, readiness gate, and repeatable local deployment without source edits.

## Requirements

- Secrets remain backend-only and staging configuration is validated.
- Baseline version is `000`; ordered SQL migrations are transactional and tracked.
- Backend emits JSON stdout logs with request ID, method, path, status, and latency.
- Readiness requires DB access and migration metadata and exposes the build identifier.
- The backend image runs non-root with one Uvicorn worker.
- Compose orders PostgreSQL, release migrations, then backend.

## Success criteria

Fresh/upgrade migrations, readiness, image build, and restart rehearsal pass. Provider-specific provisioning is deferred to Block 4.
