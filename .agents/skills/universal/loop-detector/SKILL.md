---
name: loop-detector
description: "Detects when the agent is trapped in a repetitive fix-attempt cycle and forces escalation. Prevents the 'insistent failure' anti-pattern where the agent retries the same broken approach indefinitely. TRIGGERS: 'I keep getting the same error', 'this keeps failing', 'stuck in a loop', 'why does it keep breaking'. Also auto-invoked by the verification loop rule after 3 failed attempts."
---

# Loop Detector (Runaway Prevention)

The most expensive failure mode in agentic coding is the infinite retry loop:
the agent encounters an error, applies a superficial fix, re-runs, hits the
same error, applies another superficial fix, and burns tokens and time without
making progress. This skill provides a deterministic detection and
escalation protocol.

Based on the "Ralph Pattern" from production agentic systems and LangGraph's
conditional edge routing for cycle detection.

---

## Detection Heuristics

The agent MUST self-monitor for these loop indicators during any iterative
task (debugging, test-fixing, deployment retry):

### Signal 1: Error Repetition
If the same error message (or error category) appears in 3 consecutive
tool executions, the agent is looping.

**Categories** (match by prefix, not exact string):
- `ModuleNotFoundError` / `ImportError` → Dependency loop
- `SyntaxError` / `IndentationError` → Parse loop
- `AssertionError` / test failure → Logic loop
- `ConnectionError` / `TimeoutError` → Environment loop
- `PermissionError` / `FileNotFoundError` → Path loop

### Signal 2: Edit Oscillation
If the agent edits the same file region (same function or same 20-line
block) more than 3 times within a single task, it is oscillating between
incompatible fixes.

### Signal 3: Monotonic Non-Progress
If after 3 iterations the measurable outcome has not improved (same number
of test failures, same error class, same deployment failure), the agent
is not making progress.

---

## Escalation Protocol

When any detection signal fires, the agent MUST immediately execute this
protocol instead of attempting another fix:

### Step 1: HALT
Stop the current fix-attempt cycle. Do not apply another patch.

### Step 2: DIAGNOSE
Write a structured diagnosis to `scratch/loop_diagnosis.md`:

```markdown
## Loop Detected
**Signal:** [Error Repetition | Edit Oscillation | Monotonic Non-Progress]
**Error Pattern:** [the repeating error or pattern]
**Iterations:** [how many attempts were made]
**Root Cause Hypothesis:**
  - Surface cause: [what the error message says]
  - Deeper cause: [why the fixes aren't working]
  - Environmental: [could this be a local env issue vs. a code issue?]
**What I Tried:**
1. [attempt 1 summary]
2. [attempt 2 summary]
3. [attempt 3 summary]
```

### Step 3: PIVOT (if under 3 total attempts in parent task)
Choose ONE of these pivot strategies:

| Strategy | When to Use |
|:---|:---|
| **Reframe** | The error message is misleading; re-read the actual source code instead of trusting the error |
| **Isolate** | Create a minimal reproduction outside the main codebase to test the fix in isolation |
| **Substitute** | Replace the failing component entirely (different library, different approach) |
| **Upstream** | The bug is in a dependency or environment, not in the user's code; document and work around it |

### Step 4: ESCALATE (if pivot also fails)
Present the full diagnosis to the user with this exact prompt:

```
I've detected a loop pattern after [N] attempts. Here's my analysis:
[diagnosis summary]

I recommend: [specific pivot strategy with rationale]

Would you like me to:
(a) Try the pivot strategy above
(b) Take a completely different approach to [the original goal]
(c) Move on to the next task and revisit this later
```

---

## Integration Points

- The @.agents/rules/25-verification-loop.md rule's bounded retry protocol
  (3-attempt ceiling) is the primary trigger for this skill's escalation.
- Loop diagnosis artifacts (`scratch/loop_diagnosis.md`) feed into the
  @.agents/workflows/error-observability.md workflow for pattern accumulation.
- Repeated loop detections on the same error category MUST be logged as a
  candidate for the error pattern library.

---

## Anti-Patterns

- **Cosmetic pivots:** Changing variable names or reordering lines and calling
  it a "different approach." A genuine pivot changes the algorithm, library,
  or architecture.
- **Suppressing the signal:** Catching the error and silently moving on
  instead of fixing it. The loop detector catches non-progress, not just errors.
- **Escalation avoidance:** The agent MUST NOT be reluctant to tell the user
  "I'm stuck." Transparent failure is a feature, not a weakness.
