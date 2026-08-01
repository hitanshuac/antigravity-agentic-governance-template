# AGENTS.md — Portable Governance Core

This file mirrors the Tier 0 and Tier 1 rules from `.agents/rules/` so they
apply regardless of which tool is driving the agent. `.agents/rules/` is read
natively by Antigravity; it is NOT read by Claude Code, Cursor, or a bare API
session. Any decision made outside Antigravity (e.g., a direct Opus consult)
is otherwise ungoverned by this repository's safety and ADR-logging rules.
This file exists so that never happens silently.

Antigravity-specific overrides (turbo tags, `.agents/workflows/` invocation
syntax, etc.) stay in `GEMINI.md` / `.agents/rules/` and are NOT duplicated
here — this file is the portable subset only.

## Tier 0 — Safety (Non-Negotiable, Any Tool)

- MUST NOT fabricate command output. If a command fails or is unavailable in
  this environment, state that explicitly rather than producing synthetic
  results.
- MUST NOT execute destructive operations (`rm -rf`, force-push, DB schema
  drops) without explicit human approval in the current session.
- MUST use strong absolute directives, not weak modals, when writing any new
  rule, ADR, or governance artifact.

## Tier 1 — Security

- MUST NOT import raw LLM provider SDKs outside a dedicated
  security/interceptor module. All LLM calls route through the project's
  `SecureLLMClient` equivalent, regardless of which tool wrote the code.
- MUST validate and sanitize any payload crossing a trust boundary before it
  reaches an LLM call or a persistence layer.

## Decision Governance (Portable Core)

- Before resolving a design ambiguity, check `.agents/architecture/adrs/`
  for precedent. This applies even when the consulting tool cannot read
  `.agents/rules/` directly — the ADR directory itself is plain markdown
  and readable by any tool with filesystem access.
- Any design decision resolved via a consult outside Antigravity (e.g., a
  direct Opus session) MUST be written back as a new ADR in
  `.agents/architecture/adrs/` before being merged, in the same format
  used by the in-IDE Escalation Protocol (trigger type, question asked,
  answer received, target rubric section).

## Why this file exists

Antigravity's own rules docs establish that `GEMINI.md`/`AGENTS.md` take
precedence based on which tool is active, and that teams using multiple
tools should keep shared rules in `AGENTS.md` with tool-specific overrides
in the tool's own file. This repo's actual safety-critical content (Tier 0
and Tier 1 only) is small enough to duplicate here without drift risk — the
rest stays single-sourced in `.agents/rules/`.
