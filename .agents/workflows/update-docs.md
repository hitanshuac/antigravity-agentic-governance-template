---
description: Update all markdown documentation (README, Handover, etc.) to strictly match the current state of the codebase, using a diff-based scan to avoid re-reading the entire tree on every run.
---

# Update Docs Workflow

**Trigger:** Invoked by `master-sync.md` Phase 3, or manually via `/ask run @[.agents/workflows/update-docs.md]`

## Objective
Ensure that all project documentation accurately reflects the current state of the codebase, without paying the token cost of re-reading everything every time. This is the **single source of truth** for documentation generation.

## Execution Steps

### Phase 0: Change Detection (Just-In-Time Scan)
Before reading any file content, the agent MUST determine what actually changed since the last documentation update:
1. Check for `.agents/architecture/.last_doc_sync` — a plain-text file containing the commit SHA of the last successful `update-docs.md` run.
2. If it exists, run:
   // turbo
   `git diff --name-only <last_sync_sha> HEAD`
3. If it does not exist (first run), treat this as a full scan — proceed to Phase 1 as before, then write the current SHA to `.agents/architecture/.last_doc_sync` at the end of Phase 5.
4. **If the diff is empty:** the agent MUST halt immediately and report "No changes since last doc sync — skipping." Do NOT proceed to Phase 1. Regenerating identical documentation is pure token waste.
5. **If the diff is non-empty:** only the changed paths from Phase 0 feed into Phases 1–2 below — not the full tree.

### Phase 1: Environment Scan (Scoped to Changed Paths)
Of the paths returned in Phase 0, scan only the ones that fall under these directories — skip any directory with no changed files:
1. `.agents/rules/` — re-identify active governance constraints only if a rule file changed.
2. `.agents/skills/` — re-catalog only skills whose files changed.
3. `.agents/workflows/` — re-list only workflows whose files changed.
4. `.agents/product/templates/` — re-verify only if a template changed.
5. `.agents/architecture/adrs/` — re-check only if a new ADR was added since last sync.

### Phase 2: Source Code Analysis (Scoped to Changed Paths)
1. Of the changed paths, read only the ones inside the host project's source directory.
2. Identify new or modified public functions, classes, and API endpoints in those specific files — not a full re-parse of `src/`.
3. Note any changes to the dependency manifest (`requirements.txt`, `package.json`) only if that file appears in the Phase 0 diff.

### Phase 3: README Synthesis
Update `README.md` to reflect the latest state, editing only the sections affected by what changed in Phases 1–2 — not regenerating the entire file from scratch each run. The README must contain:
- **Header & Badges**: Title and relevant tech badges.
- **Architecture Diagram**: Reference to `docs/assets/architecture_diagram.png`.
- **Overview**: Split-Plane Architecture summary.
- **Dynamic Skill Integration**: Statement about composable skill imports.
- **Installation & Setup**: Clone, venv, pip install instructions.
- **Current Capabilities**: Dynamic lists of Rules, Python APIs, Product Templates, Skills, and Workflows discovered in Phases 1-2.
- **Directory Structure**: Overview of `src/`, `data/`, `.agents/`, `.antigravity/`.
- **Adoption Method**: Instructions for injecting the Agentic Brain into other projects.
- **Visual Reference Appendix**: Architecture PNG and Mermaid diagrams.
- **Acknowledgments**: Credit to the study antigravity repository.

### Phase 4: Supporting Documentation
1. Update `HANDOVER.md` only if a changed path in Phase 0 touched a rule, workflow, or skill file.
2. Update `BOOTSTRAP.MD` only if a changed path added or removed a phase or verification step.
3. Do NOT update `HANDOVER.md` or `BOOTSTRAP.MD` if no structural changes have occurred — unchanged per the original rule, now enforced structurally by Phase 0 rather than left to agent discretion.

### Phase 5: Review & Sync Marker
1. Create a `walkthrough.md` artifact summarizing the documentation changes — per Anthropic's compaction pattern, this should be a condensed pointer artifact (what changed and why), not a restatement of the full diff.
2. Present the proposed changes to the user for approval before committing.
3. On approval, write the current `git rev-parse HEAD` to `.agents/architecture/.last_doc_sync`, overwriting the previous SHA. This is what makes the next run's Phase 0 diff meaningful — skipping this step silently degrades this workflow back into a full rescan every time.
