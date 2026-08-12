# ADR 0006: Adopt Repowise as AST Dependency Engine

## Status
Accepted

## Date
2025-08-11

## Context
The existing diagram generation pipeline uses hand-authored D2 files (`docs/architecture.d2`, `docs/handover_flow.d2`) compiled into static images. These diagrams are manually maintained and describe conceptual architecture — they do not reflect actual code-level dependencies (imports, calls, inheritance).

The user requested repowise.dev-style dependency AST diagrams: Tree-sitter-parsed directed dependency graphs with import/call/inheritance edges and PageRank-based influence ranking.

### Trigger
User request: "Could we upgrade the generate diagrams to dependency AST like repowise.dev"

### Options Evaluated
1. **Custom Python AST parser** — Build a script using `ast` stdlib to walk `src/` and emit D2 graphs. Fragile, single-language, no centrality analysis.
2. **Repowise integration** — `pip install repowise && repowise init --yes`. Tree-sitter across 16 languages, PageRank, interactive dashboard, MCP tools, deterministic. Open source (AGPL-3.0).
3. **D2-only (status quo)** — Keep hand-authored D2 files. No actual dependency analysis.

### Decision
Adopt repowise (Option 2). Retain D2 files for conceptual diagrams (different audience).

### Rationale
- **Ponytail Rung 5**: An installed dependency already solves this — repowise provides production-grade AST parsing, graph analysis, and visualization out of the box.
- **Multi-language**: Tree-sitter supports 16+ languages vs. Python-only `ast` stdlib.
- **Interactive**: Force-directed dependency graph at `localhost:7337` with clickable nodes.
- **MCP integration**: Repowise exposes 10 MCP tools compatible with the project's existing MCP server architecture (ADR 0004).
- **Deterministic**: Same code always produces the same graph (no LLM in the layout path).
- **Zero API key**: `--index-only` / `--yes` mode requires no external API key, consistent with the 12-factor BYOK rule.

## Consequences
- `.repowise/` directory added to `.gitignore` (SQLite index, machine-specific).
- `generate-diagrams.md` workflow becomes a dual-engine pipeline (repowise + D2).
- New dependency: `repowise` in `requirements.txt`.
- Existing D2 diagrams and showcase pipeline are preserved unchanged.
