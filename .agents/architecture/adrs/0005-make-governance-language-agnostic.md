# ADR-0005: Make governance language-agnostic in v2.0.0

## Status
Accepted

## Context
Originally, the governance templates and bootstrap scripts were heavily biased towards Python and specific tools (e.g., hardcoded Python dependencies in workflows). As the system scales to support multiple ecosystems (Node, Go, etc.), this bias caused friction.

## Decision
We refactored workflows and rules to be language-agnostic where possible, explicitly removing hardcoded Python dependencies from workflows and adding multi-language discovery logic to the bootstrap script (e.g., detecting `package.json`, `go.mod`, etc.).

## Consequences
- The `.agents` directory can now be injected into any project, regardless of the target ecosystem.
- Python-specific skills were moved from `universal/` to `python/` to maintain boundary clarity.
