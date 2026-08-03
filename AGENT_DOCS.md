# Antigravity Base Agentic Environment: Skills & Workflows Index

This document provides a comprehensive index of all the Skills, Workflows, and Rules included in the Antigravity Agentic Governance template.

Because this template is designed with a **"batteries-included" (everything included)** philosophy, it relies on a Single Source of Truth (SSOT). Users who inject this template via Copier receive the full suite of governance rules and capabilities. This index helps human developers understand what each component does and when an AI agent will leverage it.

---

## 1. Governance & Quality Control (The Foundation)
Ensures zero-defect compliance, data integrity, and deterministic execution.

### Skills
- **`code-quality`**: Enforces Enterprise Code Quality Standards (SAST, Ruff formatting).
- **`defensive-programming`**: Defines Pydantic schema-first data contracts and fail-fast operations to prevent silent data loss.
- **`design-standards`**: Prevents AI-slop UI design. Enforces anti-over-engineering and high-fidelity UI design.
- **`error-pattern-library`**: A living reference of common failure patterns (e.g., port exhaustion, cyclic imports) with proven fixes.
- **`sast-compliance`**: Strict engineering rules for zero-defect compliance, wrapping Semgrep.
- **`test-engineering`**: Pytest rules, fixture management, and state-aware integration tests.

### Workflows
- **`error-observability`**: Injects mandatory error logging and intercepts unhandled exceptions.
- **`lint`**: Orchestrates rapid static analysis via Ruff.
- **`security-sast`**: Runs security and code smell checks.
- **`test-automation`**: End-to-end test suite execution and coverage mapping.

---

## 2. Agentic Engineering & Harnesses (The Inner Loop)
Patterns that improve how the LLM communicates with itself, reflects, and self-corrects.

### Skills
- **`agent-evals`**: Builds evaluation harnesses using trajectory scoring.
- **`context-compactor`**: Manages LLM context window limits using AST compaction and sliding windows.
- **`hitl-interrupts`**: Compiles LangGraph workflows with strict Human-in-the-Loop checkpoints.
- **`langgraph-orchestrator`**: Scaffolds production-grade LangGraph state machines.
- **`llm-council`**: Runs architectural decisions through a council of AI peer-reviewers for consensus.
- **`loop-detector`**: Detects runaway retry cycles and forces structured escalation to the user.
- **`mcp-server-architect`**: Scaffolds custom Model Context Protocol (MCP) servers.
- **`multi-agent-crew`**: Builds multi-agent teams with strict role contracts.
- **`prompt-registry-sync`**: Externalizes embedded LLM prompts into versionable markdown files.
- **`quota-optimizer`**: Monitors token usage and prevents excessive API quota drain.
- **`self-reflection`**: A 5-point Reflexion protocol for structured self-critique.
- **`session-memory`**: Persists architectural decisions and context across long sessions (`SESSION_LOG.md`).
- **`structured-output`**: Enforces strict Pydantic-based JSON schemas for all LLM calls.
- **`telemetry-tracing`**: Implements LangSmith and OpenTelemetry tracing.

---

## 3. Product & Execution (The Outer Loop)
Rapid prototyping, spec-driven development, and time-pressured hackathon velocity.

### Skills
- **`competitive-recon`**: Rapid landscape scan, gap analysis, and differentiation framing.
- **`developing-with-streamlit`**: [REQUIRED] Master skill for all Streamlit UI tasks.
- **`meta-agent-formats`**: Output templates for Rules, Proposals, and Reviews.
- **`rapid-prototyping`**: 5-minute scaffolds for Streamlit, Gradio, and FastAPI+HTMX.

### Workflows
- **`code-generation-preflight`**: Mandatory pre-coding checklist before an agent writes code.
- **`demo-first`**: Reverses the development cycle by building the demo script BEFORE implementation.
- **`generate-diagrams`**: Translates code structures into Mermaid diagrams.
- **`generate-product-docs`**: Scaffolds Product Requirement Documents (PRDs).
- **`hackathon-sprint`**: Master 5-phase time-boxed sprint orchestrator for hackathons.
- **`spec-first`**: Spec-Driven Development. Produces `SPEC.md`, `ARCHITECTURE.md`, `TASKS.md` before coding.

---

## 4. Data Engineering & Infrastructure (The Data Plane)
Scalable pipelines, RAG systems, and memory stores.

### Skills
- **`duckdb-optimizer`**: Configures DuckDB for maximum reliability, idempotency, and speed.
- **`episodic-memory-manager`**: Integrates Episodic Memory systems (e.g., Mem0, Zep).
- **`pipeline-architect`**: Designs minimalist, fault-tolerant ETL pipelines.
- **`rag-pipeline`**: Production-grade RAG with structure-aware chunking strategies.
- **`universal-ingestion`**: Implements MarkItDown to flatten unstructured files.

### Workflows
- **`build-api-router`**: Scaffolds FastAPI router logic.
- **`build-etl`**: Executes ETL pipeline generation.
- **`daily-ingestion`**: Automates cron-based data ingestion.
- **`error-recovery`**: Triggers Dead Letter Queue (DLQ) processing and recovery schemas.

---

## 5. CI/CD & Operations (The Deployment Plane)
Deployment, Git orchestration, and automated maintenance.

### Skills
- **`deployment-ops`**: Handles Hugging Face Spaces deployments and Upstream Git syncing.

### Workflows
- **Deployments**
  - **`deploy-hf-production`**: Publishes the workspace to Hugging Face Spaces.
  - **`deploy-streamlit-production`**: Deploys a Streamlit interface natively.
- **Version Control**
  - **`git-discovery-preflight`**: Inspects local git state safely before any commits.
  - **`merge-conflict-resolution`**: Analyzes and resolves git rebase/merge conflicts.
  - **`secure-checkpoint`**: Wraps commits in verification gates to prevent broken builds.
  - **`setup-git`**: Initializes repos and links remotes via GitHub CLI.
  - **`sync-upstream`**: Re-syncs a child project with this Copier template OS.
- **Refactoring**
  - **`agentic-refactor`**: Decomposes monoliths into micro-architectures.
  - **`compliant-refactor`**: Similar to agentic, but enforces strict compliance boundaries.
  - **`dead-code-cleanup`**: Aggressively prunes unused code and scope creep via static analysis.
- **Orchestration**
  - **`bootstrap`**: The master initialization script when first cloning the template.
  - **`master-sync`**: A massive orchestration script triggering all tests, docs, and commits sequentially.
  - **`publish-showcase`**: Polishes the repository for public portfolio consumption.
  - **`semantic-release`**: Automates changelogs and semver tags.
  - **`setup-secrets`**: Pulls necessary environment variables and syncs them to GitHub Secrets.
  - **`sync-ci-errors`**: Extracts failures from GitHub Actions directly into the local agent context.
  - **`update-docs`**: Triggers a pass over `README.md` and `HANDOVER.md` to ensure they match reality.
