---
trigger: glob
glob: "src/**/*.py, tests/**/*.py, *.py"
---

# 25 Verification Loop (PRAR Cycle)

This is a Tier 2 (Correctness) rule. It mandates a **Perceive → Reason → Act → Reflect** cycle
for all code generation, ensuring the agent never presents unverified output as complete.

This rule uses a `glob` trigger scoped to Python files. It does NOT consume an always-on slot.
The verification mandate applies to any language, but the trigger fires on the dominant
codebase language to avoid token waste on non-code turns.

---

## 1. Mandatory Post-Write Verification

After writing or modifying any code file, the agent MUST execute at least one verification
step before presenting the result to the user:

| Code Type | Required Verification |
|:---|:---|
| Application code with existing tests | Run `pytest` (or the project's test runner) |
| Application code without tests | Run the code or invoke the function with a smoke-test input |
| Configuration files | Validate syntax (`python -c "import json; json.load(open('file'))"` or equivalent) |
| Infrastructure/deployment | Dry-run the deployment command if available |

The agent MUST NOT tell the user "the code should work" or "this looks correct" without
having executed a verification step. Unverified confidence is a Tier 2 violation.

---

## 2. Bounded Retry Protocol

When verification fails, the agent MUST follow this deterministic retry sequence:

1. **Attempt 1:** Diagnose the error from the traceback. Apply a targeted fix. Re-run verification.
2. **Attempt 2:** If the same category of error persists, step back and re-read the relevant
   source files to check assumptions. Apply fix. Re-run verification.
3. **Attempt 3:** If still failing, change approach entirely (different algorithm, library, or
   architecture). Apply fix. Re-run verification.

**Hard ceiling: 3 retry attempts.** After 3 failed attempts, the agent MUST halt and present
a structured failure report to the user using this exact format:

```markdown
## Verification Failed (3/3 attempts exhausted)
**Task:** [what was being attempted]
**Error Category:** [Design-Novelty | Execution-Failure | Environment-Issue]
**Attempts:**
1. [what was tried] → [what failed]
2. [what was tried] → [what failed]
3. [what was tried] → [what failed]
**Hypothesis:** [agent's best guess at the root cause]
**Recommended Next Step:** [specific action for the user]
```

The agent MUST NOT continue retrying the same approach with minor variations beyond 3 attempts.
Infinite retry loops are a Tier 0 violation per @.agents/rules/00-00-core-safety.md.

---

## 3. Verification Logging

Every verification cycle MUST produce observable output:

- The exact command that was run
- The exit code (0 = pass, non-zero = fail)
- For failures: the first 20 lines of the error output
- For passes: a one-line confirmation (e.g., "12 tests passed in 0.8s")

The agent MUST NOT suppress or summarize verification output. The user MUST be able to
see exactly what was tested and what the result was.

---

## 4. Pre-Checkpoint Gate

Before invoking any checkpoint or commit workflow (e.g., @.agents/workflows/secure-checkpoint.md),
the agent MUST confirm that the most recent verification passed. Committing code that has
not passed verification is a Tier 2 violation.

Exception: documentation-only changes (`.md`, `.txt`, `.rst` files) are exempt from this gate.

---

## 5. Interaction with Other Rules

- This rule complements @.agents/rules/30-phase-test.md (which covers test strategy).
  This rule covers the *mandatory execution* of verification; `30-phase-test` covers
  *what kinds* of tests to write.
- Retry failures that are categorized as `Design-Novelty` MUST be escalated per
  @.agents/rules/05-decision-escalation.md before further attempts.
