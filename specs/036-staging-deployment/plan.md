# Implementation Plan: Block 4

Follow `docs/staging-deployment.md`: provision and back up PostgreSQL, apply migrations as owner, deploy the backend with injected secrets, verify health/CORS/user flows, replace public API/CSP origins, build the staging installer, then execute the clean-machine matrix.
