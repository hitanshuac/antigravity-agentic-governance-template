---
name: hackathon-sprint
description: Master workflow for hackathon execution. Orchestrates a 5-phase time-boxed sprint from scoping through submission.
slash_command: /hackathon-sprint
---

# Hackathon Sprint Workflow

A time-pressured master workflow that turns a hackathon's constraints into a
structured, phase-gated execution plan. The core principle: **ship a working
demo of one thing, not a broken prototype of five things.**

---

## Pre-Flight: Context Gathering

Before starting the sprint, the agent MUST collect:

1. **Competition brief:** What is the theme/challenge? What are the judging criteria?
2. **Time budget:** How many hours remain until submission deadline?
3. **Team composition:** Is the user working solo or with a team? What are the skill gaps?
4. **Tech constraints:** Any mandatory technologies (e.g., "must use Google AI Studio")?
5. **Deployment target:** Where must the final product be deployed?

If any competition-specific rules exist (e.g., @.agents/rules/50-HACK2SKILL-competition-rules.md),
load them now. Store the brief in `SPEC.md` via @.agents/workflows/spec-first.md.

---

## Phase 1: SCOPE (First 10% of Time Budget)

**Goal:** Define the ONE problem, the demo script, and the "wow moment."

### Steps:
1. Read the competition brief and extract the **top 3 judging criteria** by weight
2. Brainstorm 3 project ideas that align with criteria (keep to 2 sentences each)
3. Score each idea on: **Feasibility** (can it be built in time?), **Impact** (does it solve a real problem?), **Demo-ability** (is it visually impressive?)
4. Pick the highest-scoring idea
5. Write a one-paragraph **elevator pitch** that a non-technical judge would understand
6. Define the **demo script:** the exact 3-minute walkthrough you will present

**Deliverable:** `SPEC.md` with elevator pitch, demo script, and chosen idea. // turbo

**Exit Gate:** The user confirms the chosen idea before moving to Phase 2.

---

## Phase 2: SCAFFOLD (Next 15% of Time Budget)

**Goal:** Working project skeleton with deployment pipeline verified.

### Steps:
1. Initialize the project structure using the fastest appropriate stack:
   - Web app → FastAPI + HTMX or Streamlit (per @.agents/skills/universal/rapid-prototyping/SKILL.md)
   - ML demo → Gradio
   - Data pipeline → DuckDB + Streamlit
2. Set up deployment target and verify it works with a "Hello World" // turbo
   - HF Spaces → @.agents/workflows/deploy-hf-production.md
   - Streamlit Cloud → @.agents/workflows/deploy-streamlit-production.md
3. Set up version control: `git init`, create `.gitignore`, initial commit // turbo
4. Write `TASKS.md` with atomic implementation steps ordered by dependency
5. Create a mock/fallback for any volatile external API dependency

**Deliverable:** A deployed "Hello World" that proves the deployment pipeline works.

**Exit Gate:** Live URL responds with 200 OK.

---

## Phase 3: BUILD (Next 45% of Time Budget)

**Goal:** Core feature implementation with verification loops.

### Steps:
1. Work through `TASKS.md` items in order
2. For each task:
   a. Implement the feature
   b. Run verification per @.agents/rules/25-verification-loop.md
   c. If verification passes, commit via @.agents/workflows/secure-checkpoint.md
   d. If verification fails 3 times, invoke @.agents/skills/universal/loop-detector/SKILL.md
3. Deploy incrementally after every 2-3 features to catch deployment issues early
4. At the halfway point of Phase 3, re-check against the demo script:
   - Is the demo path working end-to-end? If not, deprioritize non-demo features

**Priority Rule:** The demo happy path takes absolute priority over:
- Edge case handling (add try/except with generic messages instead)
- Code elegance (working beats beautiful)
- Feature completeness (3 working features beat 8 half-working ones)

**Exit Gate:** The core demo path works end-to-end locally.

---

## Phase 4: POLISH (Next 20% of Time Budget)

**Goal:** Make the demo flawless and the UI presentable.

### Steps:
1. Run the demo script end-to-end 3 times. Fix any friction points
2. Add error handling for the demo happy path (graceful failures, not crashes)
3. Polish the UI:
   - Add a compelling title/header
   - Ensure readable fonts and adequate contrast
   - Add loading states for any async operations
4. Run @.agents/skills/universal/self-reflection/SKILL.md on the entire codebase
5. Deploy the polished version

**STOP RULE:** Do NOT add new features in Phase 4. If you discover a missing
feature, add it to a "v2" section in `SPEC.md` and move on.

**Exit Gate:** The demo runs 3 times without failure on the deployed URL.

---

## Phase 5: SHIP (Final 10% of Time Budget)

**Goal:** Documentation, submission, and final deploy.

### Steps:
1. Update `README.md` per competition requirements via @.agents/workflows/update-docs.md // turbo
2. Ensure all submission requirements are met (links, documentation, etc.)
3. Final deploy and smoke test on production URL
4. Run `git status` to ensure no uncommitted changes
5. Final checkpoint via @.agents/workflows/secure-checkpoint.md // turbo
6. Verify repository size is within any competition limits
7. Prepare submission (fill in forms, post links, etc.)

**Deliverable:** Submitted project with all required links and documentation.

---

## Time Management Enforcement

The agent MUST announce phase transitions explicitly:

```
⏱️ PHASE TRANSITION: Moving from SCOPE → SCAFFOLD
Time elapsed: [X]h / [Y]h total
Time remaining: [Z]h
```

If a phase overruns its time allocation by more than 50%, the agent MUST
force-transition to the next phase. Perfection in one phase at the cost
of skipping another phase is a losing strategy.

---

## Emergency Protocols

### "It's broken and I have 1 hour left"
1. Revert to the last working commit: `git log --oneline -5` then `git checkout <hash>`
2. Remove the broken feature
3. Deploy the working version
4. Update README to match what actually works

### "The API key stopped working"
1. Switch to mock data immediately
2. Add a note in the README: "Production API integration ready; demo uses sample data"
3. Deploy and submit
