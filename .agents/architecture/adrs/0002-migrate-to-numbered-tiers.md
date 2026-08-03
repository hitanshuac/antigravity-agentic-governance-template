# ADR-0002: Migrate from MASTER rule files to numbered tier system

## Status
Accepted

## Context
Previously, governance rules were stored in monolithic `MASTER` files (e.g., `10-MASTER-security.md`). This led to contextual fragmentation, as different tools required different specific rules to be loaded. Agent performance suffered due to overly broad rules.

## Decision
We migrated to a numbered tier system (e.g., `00-01-core-safety.md`, `10-phase-audit.md`), allowing for more granular inclusion and strict hierarchical enforcement.

## Consequences
- Better context management for agent prompts.
- Clearer hierarchy for conflict resolution (Tier 0 overrides Tier 1).
- Broken references in legacy files needed manual updating.
