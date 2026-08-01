---
trigger: glob
glob: ".agents/rules/**/*.md, .agents/skills/**/*.md, .agents/workflows/**/*.md"
---

# 00-03 Meta-Governance: Deterministic Rule for Writing Rules, Skills, and Workflows

## 0. Purpose

Every governance artifact in `.agents/` has a cost: rules cost tokens on every
turn where their trigger fires, and any artifact can silently drift from or
conflict with what already exists. This rule exists because those failure
modes have already occurred in this repository — always-on rules covering
unrelated concerns, three rule files firing on the same glob with two of them
empty stubs, hand-typed citations pointing at rule numbers that don't exist,
and a workflow that reimplemented a destructive-action gate instead of
reusing the one that already existed. This rule is a deterministic checklist,
not a discussion. The agent MUST walk it in order before saving any new or
substantially modified file under `.agents/rules/`, `.agents/skills/`, or
`.agents/workflows/`.

This rule intentionally uses a `glob` trigger scoped to governance paths, not
`always_on` — a rule about preventing token bloat MUST NOT itself contribute
to it on every unrelated turn.

---

## 1. Deduplication Gate (Run First)

Before creating any new file, the agent MUST `grep_search` across
`.agents/rules/`, `.agents/skills/`, and `.agents/workflows/` for the topic
being addressed.

- If an existing file already covers this topic → extend that file. Creating
  a new file for a topic that already has a home is prohibited without an
  explicit, stated reason (e.g., a genuine Tier separation).
- If no existing file covers it → proceed to Section 2.

---

## 2. Trigger Classification Gate

The agent MUST classify the new artifact using this decision tree and MUST
NOT default to `always_on` for convenience:

| Question | If Yes |
|---|---|
| Does violating this even once, on any turn, risk data loss, security failure, or an irreversible action? | `always_on`, Tier 0 or 1 only. |
| Does this only apply when specific file paths are touched (source, tests, a particular skill's files)? | `glob`, scoped to the narrowest pattern that covers the real cases — not a broad catch-all. |
| Is this only relevant when explicitly invoked for a specific task? | This belongs in `.agents/workflows/`, not `.agents/rules/`, or should be `trigger: manual`. |

**Glob Collision Check:** Before finalizing a `glob` trigger, the agent MUST
`grep_search` existing rule files for the same or an overlapping glob
pattern. If one or more files already fire on that pattern:
- If the new content is a natural extension of an existing file's topic →
  merge into it instead of creating a new file.
- If the new content is a genuinely distinct concern that must fire on the
  same paths → proceed, but state explicitly why merging was rejected.

**Always-On Budget:** Before adding a new `always_on` rule, the agent MUST
count the current number of `always_on` files via `grep_search`. If adding
this file would bring that count above 5, the agent MUST halt and present
the case to the user rather than adding it silently — every additional
always-on file is a permanent tax on every future turn.

---

## 3. Citation Policy (Anti-Drift)

- The agent MUST reference other governance files using Antigravity's native
  `@filename` inclusion syntax, not hand-typed prose like "see Rule 2.5" or
  "per Section 3." Numbered sub-rules are not a stable citation target
  unless the target file actually defines that number.
- The agent MUST NOT restate another file's content in its own words as a
  substitute for referencing it — paraphrase drift is how citations become
  wrong without anyone noticing.
- Before saving, the agent MUST verify every `@filename` reference actually
  resolves to an existing file (`view` or `grep_search` the target path).
  An unresolved reference MUST block the save.

---

## 4. Character Budget Check

Antigravity rule files are capped at 12,000 characters each. Before saving:
1. The agent MUST check the current length of the target file.
2. If the edit would bring the file within 80% of the cap (9,600 characters),
   the agent MUST split the content into a new, appropriately numbered file
   within the same tier rather than risk truncation or undefined behavior
   at the limit.

---

## 5. Workflow Command Classification (Turbo Safety)

Any new or modified workflow step that includes a terminal command MUST be
classified before being written:

| Command Type | Directive |
|---|---|
| Read-only or idempotent (tests, linters, static analysis in check-mode, dependency installs) | Tag `// turbo`. |
| State-mutating but reversible via version control | Leave ungated, but MUST NOT be tagged `// turbo`. |
| Destructive or irreversible (file/branch deletion, force-push, schema drops) | MUST route through the repository's existing Explicit Approval Mandate pattern. The agent MUST NOT invent a new approval mechanism inline — reuse the existing gated workflow for that action class (e.g., deletions route through `dead-code-cleanup.md`; commits/pushes route through `secure-checkpoint.md`). |

**Approval-Gate Reuse Mandate:** A new workflow that needs to perform a
destructive or state-changing action MUST invoke the existing workflow that
already gates that action class. Duplicating gate logic inline — even with
good intentions — is how gates get silently bypassed, as happened when a
prior version of an orchestration workflow deleted files directly instead of
delegating to the dedicated cleanup workflow's approval step.

---

## 6. Workflow Loop Engineering (The 5-Point Checklist)

Any new or modified workflow that defines an iterative process (e.g., test loops, code generation loops) MUST pass this 5-question sanity check before being saved:

1. **Bounded Exit:** Does it stop on its own, with a cited number, or could it run forever? (Must enforce a ceiling, e.g., max 3 attempts).
2. **Precedent-First:** Does it check for precedent (ADRs, rubric) before generating anything new?
3. **Escalation Routing:** If it fails, does it explicitly separate the failure into Design-Novelty vs. Execution-Failure *before* escalating?
4. **Pre-Classified Commands:** Is every command pre-classified (e.g., tagged `// turbo` or explicitly gated), rather than leaving the decision to runtime?
5. **Write-Back Loop:** Does a failure or escalation leave something behind (a log entry, an ADR) that makes the *next* run of this loop cheaper?

If a workflow loop cannot answer "YES" to all five, it is not finished and MUST NOT be saved.

---

## 7. Context-Genericity Check

The agent MUST NOT hardcode a specific competition, client, or project name
as a load-bearing constraint inside a rule, skill, or workflow (e.g., a named
hackathon's attempt limits or repo-size caps baked directly into a
workflow's logic). Any such value MUST be sourced from a single config file
via `@filename` reference. If no config file exists yet for the constraint
being added, the agent MUST create one rather than inline the value.

---

## 8. Weak-Modal & Framing Lint

Before saving, the agent MUST scan its own new text for weak modals
("should," "could," "try to," "consider," "it's recommended") and for
negative framing that names the forbidden thing directly. Per the
Deterministic Guardrails Protocol, any instance found MUST be rewritten as
a strong, positively-framed directive before the file is saved.

---

## 9. Post-Write Verification

After saving, the agent MUST:
1. `grep_search` across `.agents/rules/` for the new file's key terms to
   confirm no duplicate or contradicting directive now exists elsewhere.
2. Re-verify every `@filename` reference in the new file resolves.
3. If the new artifact is Tier 0 or Tier 1, log a one-line entry in
   `.agents/architecture/adrs/` per @.agents/skills/universal/design-standards/SKILL.md
   Section 6, stating what problem the artifact solves and why it required
   a new file rather than an extension of an existing one.

Skipping this checklist when creating or substantially modifying a
governance artifact is a Tier 0 violation — the artifacts this rule governs
are themselves the mechanism that keeps every other Tier enforceable.
