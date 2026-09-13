---
name: Build ETL Pipeline
description: "Scaffold fault-tolerant ETL pipelines for data ingestion. Integrates Pipeline Architect and DuckDB Optimizer skills with circuit breaker error recovery. TRIGGERS: 'build etl', 'data pipeline', 'etl pipeline', 'data ingestion', 'extract transform load'."
---

# Build ETL Pipeline

Scaffold and build a fault-tolerant ETL (Extract, Transform, Load) pipeline for a given data source. The agent must strictly follow the Pipeline Architect skill and all relevant governance rules.

## Pre-Conditions
1. The Product Templates in `.agents/product/templates/` MUST be populated. Specifically, the `02_TAD.md` (data flow) and `05_TICKETS.md` (backlog) must be complete.
2. The agent must load skills: **Pipeline Architect** (`@.agents/skills/pipeline-architect/SKILL.md`) and **DuckDB Optimizer** (`@.agents/skills/duckdb-optimizer/SKILL.md`).

## Phase 1: Schema Design
1. Read `02_TAD.md` § Database Schema to understand the target schema.
2. Design the DuckDB tables following `20-phase-execute.md` (idempotent `INSERT OR REPLACE`).
3. Define Pydantic models for incoming data following `20-phase-execute.md`.

## Phase 2: Pipeline Construction
1. Build the Extract layer (HTTP clients, file readers, API integrations).
2. Build the Transform layer (data cleaning, normalization, type coercion).
3. Build the Load layer (DuckDB ingestion via staging tables).
4. Wire up the Dead-Letter Queue for Pydantic validation failures (`data/quarantine_*.parquet`).

## Phase 3: Observability
1. Integrate telemetry logging.
2. Apply the Circuit Breaker protocol from `rules/20-phase-execute.md` § Circuit Breaker.

## Phase 4: Testing
1. Execute `@.agents/skills/test-engineering/SKILL.md` to generate and run the test plan for the ETL pipeline.
2. All tests must pass before handing the pipeline back to the user.
