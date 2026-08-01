---
name: self-reflection
description: "Structured self-critique using the Reflexion pattern. Forces the agent to systematically evaluate its own output against requirements before finalizing. TRIGGERS: 'reflect on this', 'critique this', 'review before shipping', 'self-review', 'check your work', 'double-check this', 'is this actually correct'. Also auto-invoked before any secure-checkpoint or master-sync workflow."
---

# Self-Reflection Skill (Reflexion Pattern)

A correct answer reached through a dangerous path is still a production risk.
This skill forces a structured pause-and-critique step before the agent
finalizes any complex output — code, architecture decisions, or multi-step plans.

Based on the Reflexion framework (Shinn et al. 2023) and adapted for
in-IDE agentic workflows where the agent cannot retrain but CAN reason
about its own trajectory.

---

## When to Invoke

This skill MUST be invoked:
1. Before any `/secure-checkpoint` or `/master-sync` workflow execution
2. Before presenting a multi-file code change to the user
3. Before finalizing an architecture decision or ADR
4. When explicitly triggered by the user

This skill MUST NOT be invoked for:
- Single-line fixes or trivial edits
- Factual lookups or status checks
- Changes that have already passed automated verification

---

## The 5-Point Reflection Protocol

When invoked, the agent MUST walk through these 5 questions in order,
writing the answers into a scratch file `scratch/reflection.md` before
presenting the final output:

### 1. Requirement Alignment
```
Does my output satisfy ALL stated requirements?
- List each requirement from the user's request
- Mark each as [MET] or [UNMET]
- If any are [UNMET], stop and address them before continuing
```

### 2. Assumption Audit
```
What assumptions did I make that the user did NOT explicitly state?
- List each assumption
- For each: is this assumption safe, or could it be wrong?
- Flag any assumption that depends on the user's environment
```

### 3. Adversarial Review
```
If a hostile code reviewer examined this output, what would they attack?
- Security: any injection vectors, hardcoded secrets, unvalidated inputs?
- Performance: any O(n²) loops, unbounded queries, memory leaks?
- Correctness: any edge cases (empty input, null, Unicode, concurrent access)?
- Style: any anti-patterns specific to this project's conventions?
```

### 4. Completeness Check
```
What did I forget?
- Error handling: does every external call have a try/except or equivalent?
- Documentation: are new functions/classes documented?
- Tests: if I added logic, did I add or update tests?
- Dependencies: did I import everything I used? Did I add anything to requirements?
```

### 5. Simpler Alternative
```
Is there a simpler way to achieve the same result?
- Could I solve this with fewer files, fewer lines, or a standard library?
- Am I over-engineering this? (per @.agents/skills/universal/design-standards/SKILL.md)
- Would a senior engineer look at this and say "why didn't you just..."?
```

---

## Output Format

After completing the protocol, the agent MUST summarize findings in this format:

```markdown
## Self-Reflection Summary
**Confidence:** [HIGH | MEDIUM | LOW]
**Requirements:** [X/Y met]
**Issues Found:** [count]
**Actions Taken:** [list of fixes applied based on reflection]
**Remaining Risks:** [anything the user should be aware of]
```

If confidence is LOW, the agent MUST present the reflection summary to the user
and ask for guidance before proceeding.

---

## Anti-Patterns

- **Rubber-stamp reflection:** Going through the motions and marking everything
  as fine without genuine critique. If the reflection finds zero issues on a
  complex change, the reflection itself is suspect.
- **Analysis paralysis:** Spending more time reflecting than building. The
  reflection protocol is designed for 2-3 minutes of focused critique, not
  an open-ended audit.
- **Skipping reflection under time pressure:** Hackathon velocity is NOT an
  excuse to skip self-review. Shipping broken code costs more time than a
  2-minute reflection.
