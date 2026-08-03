# Workflow: Universal Test Automation

**Trigger:** Mandatory after every code change. Also invocable via `/ask run @[.agents/workflows/test-automation.md]`

## Objective
Eliminate the token-burn cycle of "write code → manually write tests → debug → refactor → retest" by automating test plan generation from ticket acceptance criteria. This workflow enforces the industry-standard **Red-Green-Refactor** loop and the **Test Pyramid** across ANY language or framework.

## Industry Standard: The Testing Protocol

### The Test Pyramid (Mandatory Structure)
```
        /  E2E  \          ← Fewest: Browser/API integration tests
       / Integ.  \         ← Middle: Cross-component contract tests
      /   Unit    \        ← Most: Pure function/method tests
```
- **Unit Tests (70%):** Test individual functions in isolation. Mock all external dependencies.
- **Integration Tests (20%):** Test component boundaries.
- **E2E Tests (10%):** Test the full user-facing flow. Use sparingly.

### Red-Green-Refactor Loop
1. **Red:** Write a failing test *before* writing the implementation code.
2. **Green:** Write the minimum code to make the test pass.
3. **Refactor:** Clean up the code while keeping all tests green.

## Execution Steps

### Phase 1: Stack Detection & Test Plan Generation
1. **Detect Language/Framework:** Scan the repository (`package.json`, `pyproject.toml`, `go.mod`, etc.) to automatically determine the language and appropriate testing framework (e.g., Pytest, Jest, Go testing).
2. **Precedent Check:** The agent MUST `grep_search` `.agents/architecture/adrs/` for any existing testing precedents, mocking decisions, or framework-specific rules before generating new test approaches.
3. **Analyze Requirements:** Read `05_TICKETS.md` and extract the **Acceptance Criteria**. If `05_TICKETS.md` does not exist, intelligently scan the codebase for untested modules.
4. Output a `test_plan.md` in the project's `docs/` directory listing every test case with:
   - **Test Name** (descriptive naming convention appropriate for the framework)
   - **Test Type** (Unit / Integration / E2E)
   - **Setup** (what fixtures or mocks are needed)
   - **Action** (what operation is performed)
   - **Assertion** (what the expected outcome is)
4. Present the test plan to the user for review before generating code.

### Phase 2: Test Scaffold Generation
1. Generate test files in the appropriate framework-standard directory (e.g., `tests/`, `__tests__/`, `*_test.go`).
2. Each test must have a clear description/docstring explaining what it validates.
3. Use the framework's native setup/teardown mechanics (fixtures, `beforeEach`, `setup`, etc.). Do not duplicate setup code.
4. **Environment Agnostic Mocks:** Mock all side-effects (file system, network, database) using native mocking libraries to ensure tests run fast and isolated.

### Phase 2.5: Fixture Verification Gate (Mandatory for I/O Modules)

> **Post-Mortem Origin:** This phase was added after unit tests using clean `tmpdir` directories passed 100% but missed a schema mismatch with the real `data/error_logs.json` file. See @.agents/skills/python/defensive-programming/SKILL.md for the underlying schema contract this gate protects.

1. For any module that performs file I/O (reads/writes JSON, YAML, CSV, Parquet, DB), the agent MUST create a `tests/fixtures/` directory containing sample data files that mirror the real production state.
2. Before running tests, verify that fixtures exist for every I/O module. If missing:
   - If the real data file exists in `data/`, copy a sanitized sample into `tests/fixtures/`.
   - If no real data exists yet, create representative samples matching the canonical schema defined in the relevant workflow (e.g., `error-observability.md` Step 1).
3. Fixtures MUST include edge cases: empty files, canonical-schema files, and legacy-schema files (to verify migration logic).
4. Integration tests MUST load these fixtures as pre-populated state rather than starting from a clean slate.
5. Reference: `00-01-core-safety.md` Rule 1 (Explicit Approval), @.agents/skills/universal/design-standards/SKILL.md Section 3 (Error Handling Decisions).

### Phase 3: Execution & Observability
1. Run the appropriate test command after every code change. These are read-only and safe to auto-run:
   // turbo
   `pytest -v --tb=short` (or `npm test`, `go test -v` depending on detected stack)
2. **Handle Failures**: If any tests fail (Non-Zero Exit Code), the agent MUST halt, log the failure via `.agents/workflows/error-observability.md`, diagnose, fix the code according to defensive standards, and retry. This retry loop is capped at 3 attempts per `30-phase-test.md`.
3. **3rd-Failure Escalation (Execution-Failure Path):** On the 3rd consecutive failure, the agent MUST NOT dump an open-ended problem on the user. Per @.agents/skills/universal/design-standards/SKILL.md Section 6, this is by definition an **Execution-Failure** — so the agent MUST:
   1. State explicitly: *"Execution-Failure: [sub-task] has failed 3 attempts."*
   2. Produce a minimal failing repro: exact command, exact error, exact files touched across the 3 attempts.
   3. Halt and present the repro to the user.
4. **Write-Back (Mandatory on Every Escalation):** Once the user resolves the escalation, the agent MUST log an ADR to `.agents/architecture/adrs/` before closing the ticket — trigger type, repro given, fix received, and whether this reveals a recurring bug class. An escalation that isn't logged is a Tier 2 violation per `00-03-meta-governance.md` Section 6 (Write-Back Loop) and blocks `master-sync.md`.
5. **Success Condition**: If tests pass, mark the ticket's acceptance criteria as completed in `05_TICKETS.md`.

### Phase 4: Coverage Gate (Optional)
1. Run the language-specific coverage tool. Read-only, safe to auto-run:
   // turbo
   `pytest --cov` (or `jest --coverage`)
2. Target: **80% minimum line coverage** for new code.
3. If coverage drops below threshold, add missing test cases before proceeding.

## Token Conservation Rules
1. **Never generate more than 5 test files in a single pass.** Run tests after each file.
2. **Never debug a failing test for more than 3 iterations.** The 4th failure MUST trigger the explicit Execution-Failure escalation path (Phase 3).
3. **Reuse fixtures aggressively.**
4. **Keep test output concise.** Use short traceback flags (`--tb=short`, `--silent`) to minimize noise.
