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

### Phase 3: Generate Technical Diagram (D2 CLI)
1. Run `d2 docs/architecture.d2 docs/assets/architecture_diagram_technical.png --theme=200 --sketch` to produce the programmatic diagram.
2. Verify the output file exists and is non-zero bytes. This is the **Technical** asset.

### Phase 4: The Showcase Styling Overlay (Mandatory for Publish)
1. Per the `.agents/skills/diagram-generator/SKILL.md` rules, pass `docs/assets/architecture_diagram_technical.png` into the `generate_image` tool.
2. Use the exact strict-spelling prompt defined in `SKILL.md` to have the AI redraw the diagram with high-end aesthetics while preserving 100% of the text.
3. Save the output as `docs/assets/architecture_diagram_showcase.png`.

### Phase 5: Verification
1. Confirm `README.md` references the showcase image at the top: `![Architecture Diagram](docs/assets/architecture_diagram_showcase.png)`.
2. Report the generation of the dual diagrams to the user.
