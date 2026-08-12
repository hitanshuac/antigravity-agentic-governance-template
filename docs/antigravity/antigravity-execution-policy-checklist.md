# Antigravity Execution Policy Checklist
### Backing up `00-01-core-safety.md` (Explicit Approval Mandate) with IDE-level enforcement

## Why this file exists

`00-01-core-safety.md` asks the agent to seek approval before destructive
actions. That's a prompt-level request — under context pressure, over a long
session, or after a compaction event, a rule written in prose is competing
for attention with everything else in the window. Antigravity exposes actual
permission settings under **Settings → Advanced Settings** that gate agent
actions at the IDE level, independent of what the agent currently has in
context. Configure these once; they hold even on a fresh, cold-context
session — which matters specifically because Antigravity starts every
session with no memory of prior sessions.

**Verify against the current UI before relying on this** — Antigravity is
an actively developed product and settings names/locations can move between
releases. Open Settings → Advanced Settings and confirm each item below
still exists under the name given; if a setting has been renamed or moved,
update this file (and note the change in an ADR per `00-03-meta-governance.md`
Section 9, since this file governs a Tier 0 rule's real-world enforcement).

## Checklist

- [ ] **Terminal/shell command execution** — set to require confirmation
  for any command outside an explicit allowlist, rather than "always allow."
  This is the IDE-level backstop for the turbo-tag classification work
  already done across `agentic-refactor.md`, `dead-code-cleanup.md`, and
  `test-automation.md` — turbo-tagged commands should match what you've
  allowlisted here; anything not turbo-tagged should NOT be in the allowlist.
- [ ] **File deletion** — set to require confirmation for any delete outside
  a scratch/temp directory. This is the structural counterpart to the
  Explicit Approval Mandate — if this setting is enabled, an agent can't
  silently delete a file even if it misreads or skips the rule in
  `00-01-core-safety.md`.
- [ ] **Git operations (commit/push/force-push)** — set to require
  confirmation, matching `15-git-protocol.md`'s Mandatory Checkpoint
  Workflow. Force-push specifically should require confirmation even if
  ordinary commits are allowlisted, since it's the one git operation that
  can destroy remote history.
- [ ] **Network/external requests** — set to require confirmation for
  requests to domains not already used in the project, reducing the blast
  radius of a prompt-injected or hallucinated external call.
- [ ] **Package installation** — set to allow without confirmation for
  well-known package managers (`pip install`, `npm install`) matching the
  turbo-tagged installs in `agentic-refactor.md` Phase 1 and
  `dead-code-cleanup.md` Phase 2 — these are additive and reversible via
  `requirements.txt`/`package.json`, so gating them adds friction without
  adding safety.

## What this does and doesn't replace

This checklist doesn't replace `00-01-core-safety.md` — the rule still
matters for *why* the agent should ask, and for actions this settings panel
doesn't cover (e.g., overwriting a specific file's content without deleting
it). What it replaces is the assumption that the rule alone is sufficient.
Treat the rule as the agent's stated intent, and this settings configuration
as the enforcement layer that holds even if that intent gets deprioritized
under context pressure.
