# Phase 1: Quickstart Validation Guide

Since this is a refactoring feature, validation involves running the existing automated test suites and performing the baseline manual checks to ensure no regressions occurred.

## Prerequisites
- Local PostgreSQL instance available.
- Python 3.12+ (backend).
- Node.js & Vite (frontend).
- Rust / Tauri (desktop).

## Setup Commands

### 1. Database Initialization
```bash
# Must run cleanly on a fresh database
cd database
psql -d blooming_test -f install.sql
```

### 2. Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Frontend Dependencies
```bash
cd frontend
npm install
```

## Validation & Testing

### 1. Backend Automated Tests (Deterministic)
```bash
cd backend
pytest tests/unit/
pytest tests/integration/
pytest tests/api/
```
*Expected Outcome: All passing tests from the pre-refactor baseline still pass. Exclude non-deterministic LLM tests.*

### 2. Frontend / Type Checks
```bash
cd frontend
npm run check
npm run test:unit
```
*Expected Outcome: Zero type errors, all unit tests pass.*

### 3. Application Smoke Test (Manual)
```bash
# Terminal 1: Backend
cd backend
python run.py

# Terminal 2: Frontend
cd frontend
npm run tauri dev
```
*Expected Outcome: The application starts normally. The 9 critical manual flows (Authentication, Onboarding, Today Plan, Mr. Bloom chat, Goals, Pomodoro, Re-plan, Garden, Widget) behave identically to their documented pre-refactor state.*
