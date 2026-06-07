# Workflow: Generate Architecture Diagrams

**Trigger:** Invoked by `master-sync.md` Phase 4, or manually via `/ask run @[.agents/workflows/generate-architecture.md]`

## Objective
Programmatically regenerate the architecture diagram assets whenever the codebase structure changes. This workflow bridges the gap between the existing Python scripts (`docs/generate_architecture.py`, `docs/composite_diagram.py`) and the `diagram-generator` skill, ensuring they are actually invoked rather than sitting idle.

## Execution Steps

### Phase 1: Architecture Analysis
1. Read the current state of `src/capabilities/` to identify all active modules.
2. Read `.agents/rules/`, `.agents/workflows/`, and `.agents/skills/` to catalog components.
3. Compare the discovered components against the existing `docs/architecture.d2` script to determine if the diagram is stale.

### Phase 2: Update D2 File
1. If new components have been added, update `docs/architecture.d2` to include them as new nodes or clusters.
2. Ensure strict adherence to D2 syntax and maintain the declarative structure.

### Phase 3: Generate Base PNG (D2 CLI)
1. Run `d2 docs/architecture.d2 docs/assets/architecture_diagram.png --theme=200 --sketch` to produce the programmatic diagram.
2. Verify the output file exists at `docs/assets/architecture_diagram.png` and is non-zero bytes.

### Phase 4: AI Styling Pass (Optional — Recruiter-Facing)
1. If the diagram is intended for a recruiter-facing showcase, execute the styling instructions from `.agents/skills/diagram-generator/SKILL.md` §"The Strict AI Styling Pass".
2. Pass the base PNG into the `generate_image` tool with the exact prompt specified in the skill.
3. Overwrite `docs/assets/architecture_diagram.png` with the styled version.

### Phase 5: Verification
1. Confirm `README.md` references the image at the top: `![Architecture Diagram](docs/assets/architecture_diagram.png)`.
2. Report the result to the user.
