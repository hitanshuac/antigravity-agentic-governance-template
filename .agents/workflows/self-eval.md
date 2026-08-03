---
name: Self-Eval
description: Runs the governance evaluation harness against the template's own history to establish a baseline.
---

# Self-Eval Workflow

**Trigger:** Explicit invocation via `/ask run @[.agents/workflows/self-eval.md]`

## Precedent Check
Before running, the agent MUST `grep_search` `.agents/architecture/adrs/` for any
prior eval decisions or baseline thresholds that override the defaults below.

## Execution Steps

1. Run the governance evaluation harness. Read-only analysis, safe to auto-run:
   // turbo
   `python -m tools.governance_eval.cli analyze`
2. Parse the output scorecard (default: `governance_scorecard.md`) for metrics.
3. **Threshold Gate:** If any metric is below 0.7:
   - **Attempt 1:** Re-run with `--verbose` to get detailed failure context.
   - **Attempt 2:** Check if the failure is caused by stale conversation data
     (e.g., truncated transcripts) and retry with `--brain-dir` pointed at
     the most recent conversation.
   - **Attempt 3:** If still failing, halt with a structured failure report:
     ```
     ## Self-Eval Failed (3/3 attempts exhausted)
     **Task:** Governance scorecard generation
     **Error Category:** Execution-Failure
     **Metric(s) below threshold:** [list]
     **Hypothesis:** [agent's analysis]
     **Recommended Next Step:** [specific action]
     ```
4. On success, append the summary results to `data/eval_history.json`.
5. **Write-Back:** If this eval revealed a new failure class not previously
   documented, log an ADR to `.agents/architecture/adrs/` before completing.
