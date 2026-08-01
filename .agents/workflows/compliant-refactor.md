---
name: SRE-Compliant Agentic Refactor
description: Orchestrates agentic-refactor and test-automation while strictly enforcing SRE SOPs, defensive programming, and active competition rules.
---

# SRE-Compliant Agentic Refactor

This master orchestration workflow chains architectural decomposition (`agentic-refactor.md`) with continuous testing (`test-automation.md`) to execute large-scale codebase changes while ensuring zero violations of the project's core rule constraints.

## Phase 1: Rule Verification & Constraints Loading

Before writing or modifying any code, the agent MUST read and internalize the following core mandates:

1. **Competition Rules**: Load whatever `.agents/rules/` file the active competition config points to (see `.agents/skills/universal/meta-agent-formats/SKILL.md` § Modular Competition Rules). Do NOT hardcode a specific competition's evaluation criteria into this workflow — the last version of this file assumed a "Hack2Skill" attempt-limit and repo-size constraint that was never traced to a source rule and does not apply to every competition this repo is used for. If a hard attempt-limit or repo-size cap is genuinely required, verify it in the current competition's official rules before enforcing it here.
2. **SRE SOP**: `.agents/rules/30-phase-test.md` (Strict Inner/Outer Loop execution — 3-attempt ceiling on the Inner Loop, no silent failures).
3. **Defensive Programming**: `.agents/rules/00-01-core-safety.md` (Schema-first I/O, idempotent writes, zero silent data loss).
4. **Code Quality**: `.agents/rules/40-phase-deploy.md` (Clean, maintainable, language-idiomatic style).
5. **Security / SAST**: `.agents/rules/10-phase-audit.md` (CWE prevention, safe inputs).
6. **Data Validation**: `.agents/rules/20-phase-execute.md` (Strict boundaries, Pydantic type enforcement).

*Failure to adhere to these rules during the refactor will result in pipeline failure.*

---

## Phase 2: Agentic Decomposition & Refactor

### Phase 2.0: Precedent Check (Mandatory, Before Any Structural Change)
Before invoking `agentic-refactor.md`, the agent MUST:
1. `grep_search` `.agents/architecture/adrs/` for a prior decision covering this component, module boundary, or an analogous decomposition.
2. Run the proposed decomposition through @.agents/skills/universal/design-standards/SKILL.md Section 1 (Classification Gate) — Policy, Precedent, or Rubric-resolvable decisions MUST be applied directly, not re-derived from scratch.
3. Only if Section 1 yields **Novel** may the agent proceed to open-ended architectural planning in `agentic-refactor.md` Phase 2–4.

Invoke the **`.agents/workflows/agentic-refactor.md`** workflow to begin structural changes.

**During execution, the agent MUST ensure:**
- No component is modified without a clear separation of concerns.
- Pydantic models (or strict `TypedDict`s) are used as contracts for all I/O boundary layers.
- Exception handling logs full context (Fail Fast, Never Fail Silent) rather than swallowing errors.
- External API calls are strictly encapsulated and decoupled from raw UI events.

---

## Phase 3: SRE Inner Loop Testing

Immediately upon completing code modifications, the agent MUST invoke the **`.agents/workflows/test-automation.md`** workflow.

1. **Execute Tests**: Run the host project's test suite using the detected framework (e.g., `pytest`, `jest`, `go test`) — see `test-automation.md` for the turbo-tagged commands.
2. **Handle Failures**: If any tests fail (Non-Zero Exit Code), the agent MUST halt, diagnose the failure, fix the code according to defensive standards, and retry. This retry loop is capped at 3 attempts per `30-phase-test.md`.
3. **4th-Failure Escalation (Execution-Failure Path):** On the 4th failure, the agent MUST NOT dump an open-ended problem on the user. Per @.agents/skills/universal/design-standards/SKILL.md Section 6, this is by definition an **Execution-Failure** — the design was already settled in Phase 2.0 — so the agent MUST:
   1. State explicitly: *"Execution-Failure: [sub-task] has failed 4 attempts; design is not in question."*
   2. Produce a minimal failing repro: exact command, exact error, exact files touched across the 4 attempts.
   3. Halt and present the repro to the user — do not re-open architectural discussion.
4. **Write-Back (Mandatory on Every Escalation):** Once the user resolves the escalation, the agent MUST log an ADR to `.agents/architecture/adrs/` before the Outer Loop may close — trigger type, repro given, fix received, and whether this reveals a recurring bug class worth folding into `design-standards/SKILL.md`. An escalation that isn't logged is a Tier 2 violation per `00-03-meta-governance.md` Section 6 (Write-Back Loop) and blocks `master-sync.md`.
5. **Success Condition**: The refactor is NOT complete until all tests pass (`Exit Code 0`) and the test output explicitly confirms collection/execution.

---

## Phase 4: Final Compliance Sign-off

Once the Inner Loop succeeds, the agent must verify:
1. No unauthorized secrets or API keys have been hardcoded (SAST compliance per `10-phase-audit.md`).
2. The UI gracefully degrades under load (Defensive compliance).
3. The codebase remains clean, well-commented, and ready for the active competition's evaluation criteria as loaded in Phase 1.

*The agent will then notify the user of the successful refactor and await approval for the Outer Loop master sync.*
