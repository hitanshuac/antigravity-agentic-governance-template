---
name: Data Quality Contracts
description: "Schema validation at pipeline boundaries using Pandera or Great Expectations. Prevents silent data corruption by enforcing typed contracts at ingestion, transformation, and export points. TRIGGERS: 'data quality', 'data contracts', 'schema validation', 'data testing', 'pandera', 'great expectations', 'data integrity'."
---

# Data Quality Contracts

Enforce typed schema contracts at every pipeline boundary to prevent silent data
corruption. This skill implements the "Shift Left" data quality philosophy —
catching bad data at ingestion time rather than discovering it in production dashboards.

## When to Use
- Any ETL/ELT pipeline with external data sources
- API ingestion endpoints that accept user-provided data
- Database migration scripts
- ML feature pipelines

## Contract Definition Pattern (Pandera)

```python
import pandera as pa
from pandera.typing import DataFrame, Series

class IncomingDataContract(pa.DataFrameModel):
    """Contract for raw data arriving from external API."""
    id: Series[int] = pa.Field(ge=0, unique=True)
    name: Series[str] = pa.Field(str_length={"min_value": 1, "max_value": 255})
    created_at: Series[pa.DateTime] = pa.Field(nullable=False)
    amount: Series[float] = pa.Field(ge=0, le=1_000_000)

    class Config:
        strict = True  # Reject extra columns
        coerce = True  # Attempt type coercion before failing
```

## Implementation Rules

### 1. Boundary Placement
- MUST place contracts at every trust boundary: API → Extract, Extract → Transform, Transform → Load.
- MUST NOT validate inside business logic — contracts live at layer interfaces only.

### 2. Failure Routing
- Failed records MUST be routed to a Dead-Letter Queue (`data/quarantine_*.parquet`).
- The pipeline MUST continue processing valid records — never halt on partial bad data.
- MUST log: `total_received`, `total_valid`, `total_quarantined` after each run.

### 3. Contract Versioning
- Contracts MUST be versioned alongside the codebase.
- Breaking schema changes MUST be logged as an ADR in `.agents/architecture/adrs/`.

### 4. Testing
- Every contract MUST have at least one "happy path" and one "sad path" test.
- Use `@.agents/skills/test-engineering/SKILL.md` for test generation.
