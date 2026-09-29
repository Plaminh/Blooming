# Feature Specification: Block 4 - Staging Deployment and Verification

**Status**: INCOMPLETE - external staging access not available

## Goal

Deploy the prepared artifacts to hosted staging and verify database, API, email, desktop installer, and end-to-end behavior without depending on development tooling.

## Required verification

Provision PostgreSQL with backup, migration and app roles; prove backup restoration; deploy the immutable backend image; gate on readiness; test Brevo verification and assistant chat; build/install the staging desktop artifact; run the complete 20-scenario manual matrix.

No external action is marked successful without provider output or observed application behavior.
