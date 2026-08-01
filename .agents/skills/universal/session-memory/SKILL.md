---
name: session-memory
description: "Persists key decisions, blockers, and progress across long coding sessions using a structured SESSION_LOG.md. Prevents context drift when the agent's context window fills up. TRIGGERS: 'save session state', 'what have we done so far', 'session log', 'where were we', 'resume from last session', 'context is getting long'. Distinct from episodic-memory-manager (which handles cross-session Mem0/Zep integration for production apps)."
---

# Session Memory Skill

Long coding sessions (4+ hours) cause context drift: the agent "forgets"
early decisions, re-reads files it already analyzed, and contradicts its own
earlier recommendations. This skill provides a lightweight, file-based memory
system that the agent maintains throughout a session.

This is NOT a replacement for Mem0/Zep episodic memory (see
@.agents/skills/python/episodic-memory-manager/SKILL.md for that). This skill
is for the agent's own working memory within a single Antigravity session.

---

## The SESSION_LOG.md Protocol

### Initialization

At the start of any session that is expected to last more than 1 hour, or when
the user invokes this skill, create `SESSION_LOG.md` in the project root:

```markdown
# Session Log
**Started:** [timestamp]
**Goal:** [the user's high-level objective]
**Active Spec:** [link to SPEC.md if it exists]

## Decisions Made
| # | Decision | Rationale | Reversible? |
|:---|:---|:---|:---|
| 1 | [e.g., Chose FastAPI over Flask] | [e.g., async support needed] | Yes |

## Files Modified
| File | What Changed | Tests Pass? |
|:---|:---|:---|
| [path] | [summary] | [/] |

## Blockers Hit
| Blocker | Resolution | Time Lost |
|:---|:---|:---|
| [e.g., API rate limit] | [e.g., added retry with backoff] | ~15min |

## Current State
**Last completed task:** [task description]
**Next task:** [task description]
**Open questions:** [anything unresolved]
```

### Maintenance

The agent MUST update `SESSION_LOG.md` at these checkpoints:
1. After completing each task from `TASKS.md`
2. After resolving any blocker
3. After making any architecture or design decision
4. Before invoking @.agents/workflows/secure-checkpoint.md

### Compaction

When `SESSION_LOG.md` exceeds 200 lines:
1. Summarize the "Decisions Made" table into a `## Summary` section
2. Archive completed "Files Modified" entries (keep only the last 10)
3. Move resolved blockers to a `## Resolved Blockers (Archived)` section
4. Keep "Current State" always up-to-date

### Recovery

When the agent detects context loss (symptoms: re-asking questions already
answered, re-reading files already analyzed, proposing approaches already
rejected), it MUST:

1. Read `SESSION_LOG.md` to rebuild context
2. Announce: "I've re-loaded the session log. Last completed task was [X]. Resuming from [Y]."
3. Continue from the current state

---

## Integration Points

- The @.agents/workflows/hackathon-sprint.md workflow auto-creates a session log
  at the start of Phase 2 (SCAFFOLD)
- The @.agents/workflows/spec-first.md workflow records the spec approval as
  a decision in the session log
- The @.agents/skills/universal/loop-detector/SKILL.md records loop detections
  as blockers in the session log

---

## Anti-Patterns

- **Log-as-diary:** The session log is NOT a narrative of everything the agent
  did. It captures decisions, state changes, and blockers — structured data,
  not prose.
- **Stale log:** A session log that was last updated 2 hours ago is useless.
  Regular updates are mandatory, not optional.
- **Log-as-spec:** The session log records what WAS decided, not what SHOULD
  be done. Forward-looking plans belong in `TASKS.md` or `SPEC.md`.
