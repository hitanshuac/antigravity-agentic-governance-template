---
name: spec-first
description: Spec-Driven Development workflow. Forces structured requirements, architecture, and task decomposition BEFORE any code is written.
slash_command: /spec-first
---

# Spec-First Workflow

Write the specification before writing the code. This workflow produces three
artifacts that serve as the "context anchor" for the entire implementation,
preventing intent drift during long sessions and multi-agent handoffs.

Based on GitHub Spec Kit, Kiro's three-document system, and the industry-standard
Specify → Plan → Tasks → Implement methodology.

---

## When to Use

Invoke this workflow at the start of any project that involves:
- More than 3 files to create or modify
- External API integrations
- A deployment target
- Multiple features that depend on each other
- Any hackathon project (mandatory via @.agents/workflows/hackathon-sprint.md Phase 1)

Do NOT use for single-file scripts, quick fixes, or documentation updates.

---

## Step 1: Write SPEC.md

Create `SPEC.md` in the project root. // turbo

```markdown
# [Project Name]

## Elevator Pitch
[One paragraph: what it does, who it's for, why it matters]

## Requirements (EARS Notation)
Use structured requirement syntax for precision:

### Functional
- WHEN [trigger] THE SYSTEM SHALL [behavior]
- IF [condition] THEN THE SYSTEM SHALL [behavior]
- THE SYSTEM SHALL [behavior] (ubiquitous)

### Non-Functional
- THE SYSTEM SHALL respond within [X]ms for [operation]
- THE SYSTEM SHALL handle [X] concurrent users
- THE SYSTEM SHALL deploy to [target platform]

## Acceptance Criteria
For each requirement, define testable pass/fail criteria:
- [ ] [Criterion 1]: [exact condition that proves the requirement is met]
- [ ] [Criterion 2]: ...

## Constraints
- Tech stack: [mandatory technologies]
- Time budget: [hours remaining]
- Deployment: [target platform and any limits]
- Dependencies: [external APIs, services, data sources]

## Out of Scope (Explicit)
- [Feature X] — not in v1
- [Feature Y] — stretch goal only
```

**Exit Gate:** The user reviews and approves `SPEC.md` before proceeding.

---

## Step 2: Write ARCHITECTURE.md

Create `ARCHITECTURE.md` in the project root. // turbo

```markdown
# Architecture

## System Overview
[One-paragraph description of the system architecture]

## Component Diagram
[Mermaid diagram showing major components and data flow]

## Data Flow
1. [Input source] → [Processing component] → [Output/Storage]
2. ...

## Tech Stack
| Layer | Technology | Rationale |
|:---|:---|:---|
| Frontend | [e.g., HTMX] | [why this choice] |
| Backend | [e.g., FastAPI] | [why this choice] |
| Database | [e.g., DuckDB] | [why this choice] |
| LLM | [e.g., Gemini 2.5] | [why this choice] |
| Deployment | [e.g., HF Spaces] | [why this choice] |

## Key Design Decisions
- [Decision 1]: [choice made] because [rationale]
- [Decision 2]: ...

## File Structure
```
project/
├── src/
│   ├── main.py          # Entry point
│   ├── routes/           # API endpoints
│   └── services/         # Business logic
├── tests/
├── SPEC.md
├── ARCHITECTURE.md
├── TASKS.md
└── README.md
```
```

**Exit Gate:** Architecture is consistent with SPEC.md requirements.

---

## Step 3: Write TASKS.md

Create `TASKS.md` in the project root. // turbo

Break the implementation into atomic, ordered tasks. Each task MUST be:
- **Small:** Completable in under 30 minutes
- **Testable:** Has a clear pass/fail verification
- **Ordered:** Dependencies are resolved (tasks that depend on others come later)

```markdown
# Implementation Tasks

## Foundation
- [ ] Initialize project structure and install dependencies
- [ ] Set up deployment pipeline (verify Hello World deploys)
- [ ] Configure environment variables and secrets

## Core Features
- [ ] [Feature 1 Task 1]: [specific implementation step]
  - Verify: [how to test this task is done]
- [ ] [Feature 1 Task 2]: ...

## Integration
- [ ] Connect [component A] to [component B]
  - Verify: end-to-end data flow works

## Polish
- [ ] Error handling for happy path
- [ ] UI polish (title, loading states, responsive layout)
- [ ] Final deployment and smoke test

## Documentation
- [ ] Write README.md
- [ ] Final checkpoint
```

**Exit Gate:** Every SPEC.md requirement maps to at least one task.
Every task has a verification step.

---

## Step 4: Execute

With all three artifacts in place, proceed to implementation:
1. Work through `TASKS.md` in order
2. Check off tasks as completed
3. If a task reveals a spec gap, update `SPEC.md` first, THEN implement
4. If architecture changes are needed, update `ARCHITECTURE.md` and get user approval

The three documents serve as the **living context anchor** — if the agent
loses context during a long session, re-reading `SPEC.md` and `TASKS.md`
rebuilds the full picture.

---

## Anti-Patterns

- **Spec as ceremony:** Writing a spec and then ignoring it during implementation.
  The spec is the contract. Deviations require explicit updates.
- **Premature detail:** The spec defines WHAT and WHY. Implementation defines HOW.
  Avoid putting code snippets in `SPEC.md`.
- **Spec drift:** If the spec diverges from reality during implementation, the
  spec is wrong. Update it immediately.
