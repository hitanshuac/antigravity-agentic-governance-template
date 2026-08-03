---
name: Git Discovery Pre-Flight
description: Instructs the agent to search for existing open-source solutions before writing custom code.
---

# Git Discovery Pre-Flight Workflow

**Trigger:** Explicit invocation before implementing a new feature or library.

## Precedent Check
Before running, the agent MUST `grep_search` `.agents/architecture/adrs/` for any
prior decisions about the library or feature being researched.

## Execution Steps

1. Extract the core capability being requested (e.g., "PDF parsing," "rate limiting,"
   "auth middleware").
2. Search for existing open-source solutions using the GitHub CLI. Read-only, safe to auto-run:
   // turbo
   `gh search repos <keywords> --sort stars --limit 5`
3. For each candidate, evaluate:
   - **Stars / activity:** Is it actively maintained (commits in last 6 months)?
   - **License:** Is it compatible with our project license?
   - **Size:** Would it introduce excessive dependency weight?
4. Present the top 3 candidates to the user with a recommendation.
5. **Exit Gate:** The user approves one of the candidates OR explicitly authorizes
   writing a custom implementation. The agent MUST NOT proceed without approval.

## Failure Handling
- If `gh` CLI is not installed or not authenticated, halt with:
  ```
  ## Pre-Flight Failed
  **Task:** Git Discovery
  **Error Category:** Environment-Issue
  **Hypothesis:** GitHub CLI not available
  **Recommended Next Step:** Run `gh auth login` or install gh CLI
  ```
- **Write-Back:** If a custom implementation is chosen over an existing library,
  log an ADR explaining why the existing solutions were rejected.
