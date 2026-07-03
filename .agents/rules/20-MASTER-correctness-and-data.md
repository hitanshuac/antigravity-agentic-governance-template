# 20-MASTER-correctness-and-data



---
### Source: `20-20-MASTER-correctness-and-data.md`
---

# Testing Standards

This rule governs all testing practices across the Agentic Environment. It enforces industry-standard test structure, naming, and the strict prohibition of shipping untested code.

## 1. Never Ship Untested Code
- Every function, route, and pipeline component that is part of a ticket in `05_TICKETS.md` MUST have at least one corresponding test.
- If a ticket has no acceptance criteria, the agent must ask the user to define them before proceeding.
- Pull Requests with zero test coverage on new code MUST be rejected by CI.

## 2. Test Pyramid Enforcement
- **Unit Tests** must form the majority (~70%) of the test suite. They test pure logic in isolation with mocked dependencies.
- **Integration Tests** (~20%) test boundaries between components (e.g., API → database, validator → DLQ).
- **End-to-End Tests** (~10%) test the full user-facing flow. These are the most expensive and MUST be used sparingly.

## 2.5 State-Aware Integration Tests (Mandatory for I/O)

> **Post-Mortem Origin:** This rule was added after unit tests using Pytest `tmpdir` (clean-slate isolation) passed 100% but missed a critical schema mismatch with a real production file. The bug silently wiped `data/error_logs.json`.

- **Rule**: Any module that reads or writes persistent files (JSON, DB, Parquet) MUST have at least one integration test that operates on pre-populated fixture data matching the REAL production schema.
- **Why**: Unit tests with `tmpdir` only verify that code works on a clean slate. They cannot catch schema mismatches between what the code expects and what the data actually looks like.
- **Action**:
  - Create test fixtures in `tests/fixtures/` containing representative samples of real production data (e.g., `tests/fixtures/error_logs_sample.json`).
  - Integration tests must read from these fixtures, perform the operation (e.g., append a log entry), and verify no data was lost or corrupted.
  - At minimum, assert: `len(after) >= len(before)` for all append operations.
  - Fixtures must include edge cases: empty files, files with the canonical schema, and files with legacy schemas (e.g., the old dictionary format) to verify migration logic.
  - Reference: `00-MASTER-safety-and-guardrails.md` Rule 1 (Schema-First Data Contracts).

## 3. Naming Conventions
- Test files: `test_<module_name>.py` (e.g., `test_compaction.py`)
- Test functions: `test_<feature>_<behavior>_<expected>` (e.g., `test_compaction_strips_filler_prefix_correctly`)
- Test classes (when grouping): `TestCompaction`, `TestDLQRouting`

## 4. Fixture & Setup Standards
- Shared fixtures must be defined in `src/tests/conftest.py`.
- Database tests must use in-memory DuckDB instances (`:memory:`) unless testing persistence specifically.
- API tests must use FastAPI's `TestClient` — never make real HTTP calls in unit tests.
- External API dependencies must be mocked using `unittest.mock` or `pytest-mock`.

## 5. Test Execution Protocol
- Tests must be run after **every** code change, not just at the end of a feature.
- Use `python -m pytest src/tests/ -v --tb=short` as the standard command.
- The CI/CD pipeline (`.github/workflows/main.yml`) must run the full test suite on every push.

## 5.5 Contract Tests for Data Schemas

- **Rule**: Every Pydantic model or `TypedDict` used for file I/O MUST have a corresponding contract test that validates a known-good fixture file against the model.
- **Why**: Contract tests catch schema drift between what the code expects and what the data actually looks like. They are the bridge between unit tests (which test logic) and integration tests (which test boundaries).
- **Action**:
  - Test file: `tests/test_contracts.py`
  - Each test loads a fixture file from `tests/fixtures/` and asserts it deserializes successfully through the Pydantic model without validation errors.
  - If a fixture fails validation, the TEST fails (not the app). This ensures schema changes are intentional and documented, not accidental.
  - Contract tests must run BEFORE integration tests in the test suite execution order.
  - Reference: `20-MASTER-correctness-and-data.md` Rule 4, `00-MASTER-safety-and-guardrails.md` Rule 1.

## 6. Failure Handling
- If a test fails, the agent must first check `.agents/workflows/error-observability.md` for historical context.
- The agent must fix the **implementation code**, not weaken the test, unless the test itself contains a genuine error.
- After 3 failed debugging iterations on the same test, the agent must flag it for manual user review and move on.

## 7. Anti-Solipsism Verification (Human Testing)
- **Rule:** Never rely solely on internal, solipsistic verification (reading your own terminal outputs).
- Always explicitly provide the human user with the exact, step-by-step UI and CLI testing commands required to run and test the full-stack system locally (e.g., how to start the backend, how to start the frontend, what URL to open) upon completion of any task.


---
### Source: `21-20-MASTER-correctness-and-data.md`
---

# Pydantic Data Validation Standards

This rule governs the data validation layer using Pydantic, focusing on fault tolerance and isolating bad records without halting the entire pipeline.

## 1. Non-Blocking Validation
- If incoming data violates the defined Pydantic schema, it must **NOT** crash the pipeline or raise an uncaught `ValidationError`.
- The pipeline must continue processing healthy records while safely isolating the malformed data.

## 2. Quarantine Protocol
- Any record that fails Pydantic validation must be caught and routed to a quarantine file.
- Save the bad records in a `.parquet` file located within the `data/` directory (e.g., `data/quarantine_YYYYMMDD.parquet`).
- Include the original payload and the specific validation error message in the quarantine record for manual review.

## 3. Graceful Degradation
- Allow partial batch successes. If a batch contains 90% valid data and 10% invalid data, the 90% must be ingested into DuckDB while the 10% is quarantined.
- Log a warning for SRE teams to review the quarantine file, but do not exit the pipeline with a non-zero status code solely due to validation failures.

## 4. File-Based Data Validation (Non-Database Contexts)

> **Post-Mortem Origin:** This rule was added after an incident where a JSON error log was silently wiped because the agent used raw `json.load()` + `isinstance()` instead of schema validation. The existing Rules 1-3 only covered DuckDB/pipeline contexts, leaving JSON files unprotected.

- **Rule**: When project constraints prohibit databases (e.g., strict client lightweight rules), the Pydantic validation mandate still applies to ALL persistent data files.
- **Why**: A JSON file is a schema-less database. Without validation, any code that reads it must guess the structure, and guesses can silently destroy data.
- **Action**:
  - Define a Pydantic model (or `TypedDict` with explicit validation) for every JSON/YAML/TOML file the application reads or writes.
  - Deserialize file content THROUGH the Pydantic model. If validation fails, route the error to the observability layer (`error-observability.md`) using the same quarantine pattern as Rule 2.
  - This rule applies even when the persistence layer is "just a JSON file." Treat it with the same rigor as DuckDB.
  - Reference: `00-MASTER-safety-and-guardrails.md` Rule 1, `00-MASTER-safety-and-guardrails.md` (Tier 0 Safety overrides Tier 3 Compliance).

## 5. Source Baseline Verification vs. Hallucinated Precision
- **Rule**: Never build highly specific tracking logic (e.g., splitting "Transit" into "CNG Bus", "Electric Bus", "AC Metro") unless the underlying reference dataset contains explicit, verified baseline KPIs for those exact sub-categories.
- **Why**: An idempotent system with mathematically robust logic is still generating a hallucination if the source baseline is unverified. Pretending to track carbon at a highly granular level using estimated or averaged baseline data destroys the integrity of the tracking application.
- **Action**:
  - Before expanding data models or Pydantic schemas to track granular habits, verify the source of truth (`data/emissions_factors.csv`, etc.).
  - If the dataset only contains generic `bus_km` (0.06 kg/km), do NOT split the UI/schema into `cng_bus` and `electric_bus` until verified metrics are obtained.
  - Grouping variables is acceptable if their baseline variance is minimal (< 10-20%). If variance is high but verified data is absent, flag it as a data dependency blocker rather than hallucinating an average.


---
### Source: `22-20-MASTER-correctness-and-data.md`
---

# DuckDB SQL Standards

This rule strictly governs all DuckDB operations to guarantee idempotent data ingestion and prevent data duplication during pipeline failures or retries.

## 1. Idempotency is Mandatory
- **Never** use raw `INSERT INTO` statements without conflict resolution.
- All ingestion logic MUST be idempotent. A partial failure and subsequent retry must result in the exact same database state as a single successful run.

## 2. Conflict Resolution
- Use `INSERT OR REPLACE` when the primary keys are strictly defined and replacing the entire row is acceptable.
- For more complex logic, use Staging Tables:
  - Load incoming data into a temporary `staging_table`.
  - Use `INSERT ... ON CONFLICT (id) DO UPDATE SET ...` to merge the staging data into the production table.

## 3. Transactions
- Wrap batch operations in explicit `BEGIN TRANSACTION` and `COMMIT` blocks to ensure atomic writes.

## 4. No Duplicates
- Pipeline retries must never result in duplicate rows under any circumstances.


---
### Source: `23-20-MASTER-correctness-and-data.md`
---

# Strict Constraint: No Raw CSV LLM Scans

This rule applies to all ingestion, auditing, and scanning workflows within the Hybrid AI Router Vision pipeline.

## 1. The Core Constraint
- **Rule**: NEVER pass a raw `.csv` or raw `.xlsx` file directly into an LLM context window.
- **Why**: Raw CSVs contain massive amounts of noisy tokens (commas, empty strings, repetitive structural elements). Passing them directly to an LLM causes severe token inflation, hallucinations (where the LLM loses track of column indices), and immediate context window exhaustion, violating the Context Compaction rule.

## 2. Mandatory Abstraction Layers
- Before any LLM operation is performed on tabular or document data, the file **MUST** be processed locally using a structured parsing package.
- **For Tabular Data (CSV/XLSX)**: Use `markitdown` (via `MarkItDown().convert()`) or `pandas` to structure the grid. If an LLM needs to understand the table, pass it the clean Markdown output from `markitdown` or a highly truncated JSON sample of the headers—never the raw comma-separated text.
- **For Unstructured Documents (PDF/Images)**: Use `docling` (via `DocumentConverter`) or the established Vision Cascade to extract bounding boxes and structured JSON representation.

## 3. Implementation of the Shadow Copy / Silver Layer
When building "Shadow Copies" or extracting data to a Silver Layer, do not rely on an LLM to parse the entire grid. Instead:
1. Use `markitdown` or `docling` to extract the document content.
2. If schema mapping is needed, pass *only* the Markdown headers to the LLM to identify the column positions (Schema-on-Read).
3. Perform the actual data extraction, mathematical validations (e.g., `qty * rate`), and anomaly flagging deterministically in Python.


---
### Source: `24-20-MASTER-correctness-and-data.md`
---

# Financial Data Integrity

This rule defines strict standards for data extracted via MarkItDown or any other ingestion pipeline regarding financial figures.

## 1. Zero-Mutation Policy on Financial Data
- **Rule**: You MUST NEVER modify, forward-fill (ffill), back-fill, impute, or attempt to "correct" financial columns, specifically `RATE` and `AMOUNT`.
- **Why**: Financial data must perfectly reflect the raw invoice. Altering this data—even to fix an obvious formatting mistake made by a vendor—introduces untraceable accounting discrepancies and breaks data lineage.
- **Action**:
  - Extract the raw string/float values exactly as they appear in the markdown or tabular source.
  - If a vendor leaves a `RATE` blank but fills an `AMOUNT`, leave the `RATE` blank.
  - Do not calculate missing values (e.g. `QTY * RATE = AMOUNT`). The missing value must remain `null` or `NaN`.

## 2. No Synthetic Data Generation
- **Rule**: When providing snippets or previews of data extractions, agents MUST ONLY show the exact data present in the file. Synthetic data (hallucinations) to "fill out" a table preview is strictly forbidden.

## 3. Exception Handling
- If a value cannot be safely cast to its required schema type (e.g., parsing a string "N/A" as a float), the pipeline MUST raise a `SchemaError` and halt, rather than silently replacing it with `0` or `0.0` (as per `00-MASTER-safety-and-guardrails.md`).


---
### Source: `25-20-MASTER-correctness-and-data.md`
---

# Router Alignment: Ephemeral Context Grounding

This rule permanently enforces inline payload mutation for all outbound text-model requests in the Agentic Application cascade.

## 1. Mandatory System Prompt Injection
- Every outbound `messages` payload sent to any cascade tier **must** include a `role: system` message at **index 0**.
- The canonical system message is defined in `src/capabilities/compaction.py` as the `SYSTEM_PROMPT` constant.
- No cascade tier is exempt. If a provider cannot accept `role: system`, the grounding text must be prepended as a prefix to the first `role: user` message instead.

## 2. Ephemeral Injection Only
- The system message is injected **at request time** inside the `ground_messages()` function. It is never persisted to disk, database, or session state.
- The original inbound `messages` array from the client must not be mutated. The router must operate on a **deep copy**.

## 3. Content Governance
- The `SYSTEM_GROUNDING_PROMPT` must identify the system as the "Agentic Application" and instruct the downstream model to respond helpfully and concisely.
- Any modification to the prompt content requires a corresponding entry in `retrospective.md` and a version bump.

## 4. Observability
- Every grounding injection must emit an `INFO`-level log line containing `[CONTEXT GROUNDING]` for SRE traceability.
- The log must include the number of messages in the grounded payload.

## 5. Relationship to Context Compaction
- After grounding is applied, the payload must pass through the **Context Compaction** layer defined in [`40-MASTER-style-and-quality.md`](./40-MASTER-style-and-quality.md).
- Execution order: **Grounding (this rule)** → **Compaction** → **Admission Control** → **Cascade**.
- The system message injected by this rule is immune to compaction eviction (see `40-MASTER-style-and-quality.md` §3).


---
### Source: `26-quarantine-dlq.md`
---

# Quarantine & Dead-Letter Queue (DLQ)

This rule establishes the standard operating procedure for handling malformed data and Pydantic validation failures.

## Directives

1. **Never Crash the Loop:** When an ingestion pipeline encounters data that fails Pydantic schema validation, it MUST NOT crash the main application process or event loop.
2. **Isolate Failures:** Malformed data must be safely caught and isolated to prevent upstream and downstream corruption.
3. **Route to DLQ:** All validation failures must be routed to the Dead-Letter Queue (DLQ). The required location for this is `data/quarantine_log.parquet`.
4. **Observability:** Ensure that the original payload, the validation error message, and a timestamp are logged alongside the quarantined record so that agents can autonomously diagnose and retry the processing later.


---
### Source: `27-20-MASTER-correctness-and-data.md`
---

---
description: Unified standard operating procedure defining the "Inner Loop" and "Outer Loop" rhythm that all AI agents must follow.
trigger: always_on
priority: tier_2_correctness
---

# SRE Standard Operating Procedure (SOP)

This rule defines the strict rhythmic loops that all AI agents must follow during the Software Development Life Cycle (SDLC) to ensure continuous quality, observability, and synchronized documentation.

## 1. The "Inner Loop" (Continuous Iteration)
The Inner Loop runs continuously during active development, ensuring that no code is shipped broken.

- **Trigger:** After EVERY code modification (even a single line change).
- **Action:** The agent MUST autonomously execute the `.agents/workflows/test-automation.md` workflow.
- **Enforcement:**
  1. The agent MUST execute `pytest`.
  2. **Failure Condition (Non-Zero Exit Code):** If tests fail, the agent MUST execute `.agents/workflows/error-observability.md` to log the failure, then fix the code, and retry.
  3. **Halt Condition:** If the agent fails to fix the test after three (3) consecutive attempts, it MUST halt execution immediately and ask the user for manual intervention.
  4. **Success Condition (Exit Code 0):** The Inner Loop is only considered successful when `pytest` returns exit code `0` AND the test output explicitly shows that at least 1 test was collected and passed (preventing false positives from empty test suites).
  5. Upon meeting the Success Condition, the agent MUST provide the user with explicit UI/CLI commands to test the feature manually (Anti-Solipsism Protocol per `20-MASTER-correctness-and-data.md` Rule 7) and wait for the human user to reply "approved" or "works" before moving to the next task.

## 2. The "Outer Loop" (Ticket Conclusion)
The Outer Loop runs when a logical chunk of work is finished, preparing the codebase for production release.

- **Trigger:** When all Acceptance Criteria for the current ticket in `docs/05_TICKETS.md` are marked complete `[x]`, and the Inner Loop Success Condition is met.
- **Action:** The agent MUST autonomously execute the `.agents/workflows/master-sync.md` workflow.
- **Enforcement:** The `master-sync.md` workflow will automatically handle the sequential orchestration of documentation updates, diagram generation, and secure Git checkpoints. The agent MUST NOT begin work on the next ticket until the Outer Loop has successfully completed.

## 3. Workflow Integration
This SOP binds the bifurcated workflows into a unified strategy. Do not ask the user for permission to run the Inner Loop; testing is mandatory. You must ask for permission before executing the Outer Loop (the `master-sync.md` commit).
