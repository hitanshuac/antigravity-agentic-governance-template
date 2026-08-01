---
trigger: always_on
---

# Decision Escalation Protocol

This file is intentionally `always_on` despite its size: decision points can
occur on any turn, not just when specific file paths are touched, and the
file is short enough that the always-on budget in `00-03-meta-governance.md`
Section 2 is not meaningfully affected (this brings the count to 4 of 5).

## 1. Precedent-First Resolution
Before escalating any architectural or design ambiguity to the user or a stronger model, the agent MUST:
1. Search `.agents/architecture/adrs/` for a matching or analogous prior decision.
2. Search `@.agents/skills/universal/design-standards/SKILL.md` and other relevant skills for an applicable rule.
3. Only escalate if no precedent or rule resolves the ambiguity.

## 2. Mandatory ADR on Escalation
Any design decision resolved via escalation (user or external model) MUST be written back
as a new ADR before the ticket is marked complete. Failure to log forfeits Outer Loop completion.
