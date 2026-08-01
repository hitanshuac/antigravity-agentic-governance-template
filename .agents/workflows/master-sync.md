---
description: A master orchestration workflow that sequentially validates, documents, generates assets, versions, and checkpoints the codebase.
---

# Master Sync Workflow

**Trigger:** Explicit invocation via `/ask run @[.agents/workflows/master-sync.md]`

This is the **top-level orchestrator** for synchronizing the entire codebase. It calls sub-workflows in strict sequential order. Do NOT skip phases.

## Phase 1: Pre-flight Checks
1. **Repository Sanitation**: Scan the project root directory for rogue scratchpad scripts or temporary files (e.g., orphaned `*.py` or `*.txt` files used for testing logic). If any are found, MUST NOT delete them directly — invoke `.agents/workflows/dead-code-cleanup.md` instead, which enforces the mandatory Human-in-the-Loop approval gate required by the Explicit Approval Mandate (`00-01-core-safety.md`). Master Sync MUST NOT perform destructive file operations itself.
2. Verify that `.agents/product/templates/` contains all 5 product templates (`01_PRD.md` through `05_TICKETS.md`).
3. If any template is missing, halt and execute `.agents/workflows/generate-product-docs.md` to populate them.
4. If applicable to the project language, run the appropriate linter to verify the codebase passes linting. If this is a pure markdown repository, skip this step.
   // turbo
   `ruff check .` (or `eslint .` for JS/TS projects)

## Phase 2: Test Automation Gate
1. Check if a testing suite exists for the target language (e.g., `pytest`, `jest`). If none exist (e.g., pure markdown template), skip this phase.
2. Execute `.agents/workflows/test-automation.md`.
3. **Strict Handoff:** If the test suite fails or escalates (Execution-Failure), `master-sync.md` MUST halt completely. Do not attempt to fix code in the Outer Loop. The agent must resolve the failure via the Inner Loop (`test-automation.md`) and re-invoke `master-sync.md` only upon a clean test run.

## Phase 3: Update Documentation
1. Execute `.agents/workflows/update-docs.md`.
2. This will scan `.agents/` and `src/` to synchronize `README.md`, `HANDOVER.md`, and `BOOTSTRAP.MD` with the current codebase state.

## Phase 4: Regenerate Architecture Diagrams
1. Execute `.agents/workflows/generate-diagrams.md`.
2. This will scan all programmatic diagram definitions (`.d2`, `.py`) and compile them into deterministic images.
3. The outputs will be saved to `docs/assets/`.

## Phase 5: Publish Showcase
1. Execute `.agents/workflows/publish-showcase.md`.
2. This verifies the documentation assets (PNG + Mermaid) are present and correctly referenced in `README.md`.
3. Present all proposed changes to the user for final approval.

## Phase 6: Semantic Release
1. Execute `.agents/workflows/semantic-release.md`.
2. Ensure the commit message follows Conventional Commits (`feat:`, `fix:`, `docs:`, etc.).
3. The CI/CD pipeline in `.github/workflows/release.yml` will handle the version bump and changelog generation.

## Phase 7: Conversational Error Harvesting
1. The agent MUST review the conversation log (from the last stable checkpoint up to the present moment).
2. Extract any errors, failed implementation attempts, hallucinations, or dead-ends encountered during this session.
3. Execute `.agents/workflows/error-observability.md` to persist these lessons to the central observability suite so they are never repeated.

## Phase 8: Secure Checkpoint
1. The agent MUST exclusively execute `.agents/workflows/secure-checkpoint.md` to stage, commit, and push changes. There is no fallback path. This is a Tier 0 requirement per the Git Version Control Protocol (`00-01-core-safety.md`) — direct `git commit`/`git push` outside this workflow is prohibited regardless of circumstance.
2. Confirm to the user that all changes are permanently secured on GitHub.
