---
trigger: glob
glob: "tests/**/*.py, *_test.py"
---

# 30 Phase Test

# Testing Standards

This rule governs all testing practices across the Agentic Environment.

## 1. Mandatory Test Coverage
- **Rule**: Every function, route, and pipeline component that is part of a ticket MUST have at least one corresponding test.
- **Rule**: If a ticket lacks acceptance criteria, the agent MUST explicitly ask the user to define them before proceeding.
- **Rule**: You MUST apply the implementation directives found in `@.agents/skills/universal/test-engineering/SKILL.md` (e.g., Test Pyramid, State-Aware Integration, Contract Tests) for all test generation.

# SRE Standard Operating Procedure (SOP)

## 1. The "Inner Loop" (Continuous Iteration)
- **Trigger:** After EVERY code modification.
- **Action:** The agent MUST autonomously execute the `.agents/workflows/test-automation.md` workflow.
- **Enforcement:**
  1. Execute the host project's test suite.
  2. If tests fail, execute `.agents/workflows/error-observability.md` to log the failure, fix the code, and retry.
  3. If the agent fails to fix the test after 3 attempts, it MUST explicitly halt execution. Per `@.agents/skills/universal/design-standards/SKILL.md` Section 6, this is by definition an Execution-Failure — the agent MUST classify it as such and present a bounded repro to the user rather than an open-ended request for help.
  4. The Inner Loop is ONLY successful when the test runner returns exit code `0` AND at least 1 test passed.
  5. The agent MUST provide explicit UI/CLI commands to test the feature manually and wait for human approval.

## 2. The "Outer Loop" (Ticket Conclusion)
- **Trigger:** When all Acceptance Criteria for the current ticket are marked complete `[x]`, and the Inner Loop Success Condition is met.
- **Action:** The agent MUST autonomously execute the `.agents/workflows/master-sync.md` workflow.
- **Enforcement:** The agent MUST explicitly complete the Outer Loop (the `master-sync.md` commit) before beginning work on the next ticket. Per the Single Responsibility Handoff (`00-03-meta-governance.md` Section 6), `master-sync.md` MUST NOT attempt to fix a failure the Inner Loop already halted on — it may only check pass/fail and escalate.

**Migration note:** delete `30-00-phase-test.md` and `30-01-phase-test.md` after adopting this file. Both previously fired on the identical glob (`tests/**/*.py, *_test.py`), which `00-03-meta-governance.md` Section 2's Glob Collision Check requires either a merge or an explicit stated reason for — no such reason was recorded, so this merges them, consistent with the precedent already set for `20-phase-execute.md`.
