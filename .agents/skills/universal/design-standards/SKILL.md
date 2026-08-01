---
name: Design Standards & Anti-Over-Engineering
description: Technical implementation of minimalist architectures and high-fidelity UI design.
trigger: glob
glob: "src/**/*.py, .agents/architecture/adrs/**/*.md"
skill: design-standards
owner_layer: Global
scope: All architectural, interface, and implementation-level design decisions
stability: core
status: active
---

# Design Standards & Decision Rubric

## 0. Purpose

This skill exists to collapse "design judgment calls" into "checklist execution"
wherever possible, so that escalation to a stronger model is the exception, not
the default path. The agent MUST attempt full resolution via this rubric BEFORE
invoking the Decision Escalation Protocol (`05-decision-escalation.md`).

Every section below is a **decision tree**, not a discussion. The agent MUST walk
the tree top to bottom and stop at the first matching leaf. If no leaf matches,
the decision is a genuine escalation candidate — proceed to Section 6.

---

## 1. Classification Gate (Run This First)

Before applying any rubric below, the agent MUST classify the decision:

| Signal | Classification | Route |
|---|---|---|
| A rule in `.agents/rules/` already dictates the answer | **Policy** | Apply rule directly. No rubric needed. |
| An ADR in `.agents/architecture/adrs/` covers an analogous case | **Precedent** | Apply ADR decision. Log a one-line reference, not a new ADR. |
| The decision matches a tree in Sections 2–5 below | **Rubric-resolvable** | Walk the tree. Log a one-line ADR reference. |
| None of the above apply | **Novel** | Escalate per Section 6. |

The agent MUST explicitly state which row applied before proceeding. Skipping
this statement is a Tier 2 (Correctness) violation.

---

## 2. Abstraction Level Decisions (extends the Ponytail Ladder)

When deciding whether to introduce a new function, class, module, or dependency:

1. **YAGNI check** — Is there a concrete, current ticket requirement for this,
   or is it speculative? → If speculative, STOP. Do not build it.
2. **Context check** — Does equivalent logic already exist elsewhere in this
   repo? → If yes, reuse or extend it. Do not duplicate.
3. **Stdlib check** — Does the language's standard library solve this without
   a new dependency? → If yes, use it.
4. **Native platform check** — Does the existing framework (FastAPI, DuckDB,
   etc.) already expose this capability? → If yes, use it.
5. **Dependency check** — Is a well-maintained, widely-adopted library the
   only reasonable option? → If yes, add it and declare it in
   `requirements.txt` per the 12-Factor rule.
6. **One-liner check** — Can this be expressed in ≤3 lines inline without
   hurting readability? → If yes, inline it. Do not create a new file.
7. **Minimum viable abstraction** — Only if none of the above resolve it,
   create the smallest possible new construct (function before class,
   module before package).

**Escalate only if:** the correct rung of the ladder is genuinely ambiguous
(e.g., a library exists but its maintenance status is unclear) — not because
the agent is unsure whether abstraction is "good practice."

---

## 3. Error Handling Decisions

| Situation | Directive |
|---|---|
| Input crosses a trust boundary (user input, external API, file I/O) | MUST validate with a Pydantic schema and fail fast. No silent coercion. |
| Input is internal, already validated upstream in the same call chain | MUST NOT re-validate. Trust the type system. |
| Operation is idempotent-safe to retry (network call, external write) | MUST wrap in the retry pattern defined in `defensive-programming/SKILL.md`. |
| Operation is not safely retryable (e.g., non-idempotent financial write) | MUST fail loudly and require explicit re-invocation. MUST NOT auto-retry. |
| Error is expected and recoverable in normal operation | MUST return a typed error/result, not raise. |
| Error indicates a programming bug or invariant violation | MUST raise. Do not swallow. |

**Escalate only if:** the trust boundary itself is ambiguous — e.g., data
crossing a plugin/extension boundary of uncertain provenance.

---

## 4. Interface & API Boundary Decisions

1. Is this boundary crossed by more than one caller today, or planned to be
   within the current ticket? → If no, keep it a private function. Do not
   design a public interface for a single caller.
2. Does the boundary need to be stable across versions (external consumers,
   other services)? → If yes, version it explicitly; do not allow breaking
   changes without a major version bump.
3. Is the boundary internal-only (same repo, same deploy unit)? → Optimize
   for the current caller's actual shape. Do not generalize preemptively.
4. Does this boundary touch an LLM provider? → MUST route through
   `SecureLLMClient` per the OWASP LLM rule. This is non-negotiable and is
   not a judgment call.

**Escalate only if:** the boundary spans a genuine build-vs-buy tradeoff
(e.g., "should this be our own API or should we adopt an existing protocol").

---

## 5. State & Persistence Decisions

| Situation | Directive |
|---|---|
| Data must survive a process restart | MUST use a backing service (DuckDB, file store) — never in-memory only. |
| Data is derived and cheaply recomputable | MUST NOT persist it. Compute on demand or cache with an explicit TTL. |
| Multiple writers may touch the same record concurrently | MUST use `INSERT OR REPLACE` idempotency per the SQL Standards rule. |
| Data is agent-scratch/intermediate reasoning state | MUST stay in-process. MUST NOT be written to `data/` — that plane is
system-managed output only. |

**Escalate only if:** a genuinely new persistence pattern is needed that
doesn't fit DuckDB/file-store/in-memory (e.g., needing a message queue).

---

## 6. Escalation Protocol (Last Resort)

There are exactly two valid reasons to escalate. The agent MUST classify
which one applies BEFORE escalating, since they route to different targets.

| Trigger | Signature | Escalate To |
|---|---|---|
| **Design-Novelty** | Sections 1–5 produce no matching leaf. The ambiguity is in *what* to build. | Strongest available reasoning model (e.g., Claude Opus). |
| **Execution-Failure** | The rubric already resolved *what* to build, but the agent has failed the same sub-task 2+ times in a row (the Inner Loop's 3-attempt ceiling in `30-phase-test.md` is about to trip). The ambiguity is in *why the implementation keeps failing*, not in the design. | Strongest available reasoning model, scoped narrowly to the failing sub-task only — do NOT re-litigate the design. |

The default execution model MUST remain the environment's tuned default
(e.g., Gemini) for all Policy, Precedent, and Rubric-resolvable decisions per
Section 1. Escalating on cost/capability grounds alone, without one of the
two triggers above, is a Tier 3 (Compliance) violation — it burns budget
without shrinking the Section 6 problem space for next time.

On escalation, the agent MUST:

1. State explicitly which trigger applies: *"Design-Novelty: no rule, ADR,
   or rubric branch resolves this."* OR *"Execution-Failure: sub-task
   [name] has failed [n] attempts; design is not in question."*
2. Summarize the decision as a **bounded question** (max 2 options, with
   tradeoffs) for Design-Novelty, or a **minimal failing repro** (exact
   command, exact error, files touched) for Execution-Failure. Neither
   should be an open-ended prompt.
3. On resolution, MUST write a new ADR to `.agents/architecture/adrs/`
   before the Outer Loop (`30-phase-test.md`) is permitted to close the
   ticket. An unlogged escalation is a Tier 2 violation and blocks
   `master-sync.md`. Execution-Failure escalations that reveal a *recurring*
   bug class (not a one-off typo) MUST also be logged, since those are
   exactly the errors this rubric is meant to eventually prevent outright.
4. The ADR MUST include: the trigger type, the bounded question or repro
   given, the answer/fix received, and the rubric section it should be
   added to (if it's likely to recur) — flagged for a future rule-update
   pass.

**The goal is not zero escalation.** The goal is that every escalation
permanently reduces the size of Section 6's problem space for the next
ticket. An escalation that isn't logged as a reusable ADR is wasted spend.

## 7. Skill Cross-References

Per Antigravity's `@filename` resolution, the following are included by
reference rather than restated in prose, so this file stays synchronized
with the source of truth and does not silently drift:

- @.agents/skills/python/defensive-programming/SKILL.md
- @.agents/skills/universal/context-compactor/SKILL.md
- @.agents/rules/05-decision-escalation.md

## 8. Anti-AI-Slop Design Rule

Avoid "lowest common denominator" AI visual patterns.
1. Use high-contrast font pairings (e.g., distinctive Serif display + clean Sans body).
2. Extract color palettes from references or use `oklch` for adjustments instead of pure CSS colors.
3. Use plain structural elements (e.g., plain gray rectangles for image placeholders) instead of generic SVGs.
