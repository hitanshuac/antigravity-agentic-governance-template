---
name: test-engineering
description: Technical implementation of Pytest, Fixtures, State-Aware Integration Tests, Contract Tests, and the Red-Green-Refactor loop.
---

# Test Engineering & QA Skill

**Trigger:** Mandatory after every code change. Also invoked for "write tests for...", "add coverage", or as part of orchestration workflows.

## 1. Test Pyramid Enforcement
- **Unit Tests** must form the majority (~70%) of the test suite. They test pure logic in isolation with mocked dependencies.
- **Integration Tests** (~20%) test boundaries between components (e.g., API → database, validator → DLQ).
- **End-to-End Tests** (~10%) test the full user-facing flow. 

## 2. Red-Green-Refactor Loop
1. **Red:** Write a failing test *before* writing the implementation code.
2. **Green:** Write the minimum code to make the test pass.
3. **Refactor:** Clean up the code while keeping all tests green.

## 3. Test Plan & Scaffold Generation
1. **Stack Detection:** Scan the repository (`package.json`, `pyproject.toml`, `go.mod`, etc.) to automatically determine the language and appropriate testing framework.
2. **Precedent Check:** `grep_search` `.agents/architecture/adrs/` for testing precedents before generating new test approaches.
3. **Analyze Requirements:** Extract Acceptance Criteria from `05_TICKETS.md`.
4. **Scaffolding:** Generate test files in the framework-standard directory. Mock side-effects using native mocking libraries. Never generate more than 5 test files in a single pass.

## 4. State-Aware Integration Tests & Fixture Verification (Mandatory for I/O)
- Any module that reads or writes persistent files (JSON, DB, Parquet) MUST have at least one integration test that operates on pre-populated fixture data matching the REAL production schema.
- Before running tests, verify that fixtures exist in `tests/fixtures/`. If missing, copy a sanitized sample from `data/` or create one matching the canonical schema.
- Fixtures MUST include edge cases: empty files, canonical-schema files, and legacy-schema files (for migration logic).
- At minimum, assert: `len(after) >= len(before)` for all append operations.
- Shared fixtures must be defined using `conftest.py` (or equivalent). Database tests must use in-memory instances.

## 5. Contract Tests for Data Schemas
- Every Pydantic model or `TypedDict` used for file I/O MUST have a corresponding contract test that validates a known-good fixture file against the model.
- Test file: `tests/test_contracts.py`

## 6. Test Execution & Failure Handling Protocol
- Tests must be run after **every** code change using the framework-appropriate command (e.g., `pytest src/tests/ -v --tb=short`).
- If a test fails, check `data/error_logs.json` for historical context. (Note: this refers to the observability system).
- Fix the **implementation code**, rather than weakening the test.
- **3rd-Failure Escalation (Execution-Failure Path):** After 3 failed debugging iterations on the same test, the agent MUST explicitly state: *"Execution-Failure: [sub-task] has failed 3 attempts."*, produce a minimal failing repro, and halt for user review. 
- **Write-Back:** Once resolved by the user, log an ADR to `.agents/architecture/adrs/`.

## 7. Coverage Gate
- Target: **80% minimum line coverage** for new code. Run coverage tools (e.g., `pytest --cov`) to verify. If below threshold, add missing test cases.

## 8. Anti-Solipsism Verification (Human Testing)
- Explicitly provide the human user with the exact, step-by-step UI and CLI testing commands required to run and test the full-stack system locally upon completion of any task.
