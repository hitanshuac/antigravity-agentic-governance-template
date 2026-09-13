---
name: Product Documentation Generator
description: "Interview-driven product documentation generator. Forces the agent to fill out 5 core Product & Systems Design templates before allowing any code generation. TRIGGERS: 'generate product docs', 'create PRD', 'product requirements', 'technical architecture document', 'project planning', 'new project setup'."
---

# Product Documentation Generator

Before allowing any code generation for a new project, the Agent MUST interview the user and fill out the 5 core Product & Systems Design templates. This ensures a deterministic, hallucination-free coding phase.

## Phase 1: Interview & Context Gathering
1. Ask the user for a high-level description of what they want to build.
2. Ask clarifying questions to narrow down the MVP scope, target audience, and preferred tech stack.

## Phase 2: Document Generation
The Agent must sequentially generate populated versions of the 5 templates (saving them in a `docs/` or `design/` folder for the project):
1. `01_PRD.md` (Product Requirements)
2. `02_TAD.md` (Technical Architecture)
3. `03_SECURITY.md` (Security & Access)
4. `04_FRONTEND.md` (Frontend Spec)
5. `05_TICKETS.md` (Actionable backlog)

## Phase 3: Review & Lock-in
1. Present the completed documents to the user for approval.
2. Once approved, the Agent may proceed to execute `05_TICKETS.md` sequentially. Do NOT write code until all 5 documents are approved.

## Phase 4: Ticket Execution & Testing Loop
For each ticket in `05_TICKETS.md`:
1. Write the implementation code for the ticket.
2. Execute `@.agents/skills/test-engineering/SKILL.md` to auto-generate test cases from the ticket's acceptance criteria.
3. Run all tests. If any fail, check `data/error_logs.json`, fix the code, and re-run.
4. Only proceed to the next ticket when all tests pass.
