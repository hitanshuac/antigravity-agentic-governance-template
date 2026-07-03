# Workflow: Generate All Diagrams

**Trigger:** Invoked by `master-sync.md` Phase 4, or manually via `/ask run @[.agents/workflows/generate-diagrams.md]`

## Objective
A generalized, universal pipeline to scan the project for any programmatic diagram definitions (D2 or Python) and compile them directly into deterministic, high-fidelity images. No AI styling passes are permitted to prevent hallucination.

## Execution Steps

### Phase 0: Codebase Extraction (Auto-Sync)
1. Execute `python scripts/diagram_extractor.py` to parse the `src/` directory.
2. Ensure the script successfully outputs `docs/assets/auto_architecture.d2`.

### Phase 1: Diagram Discovery
1. Scan the `docs/` folder (and any subfolders) for all `.d2` and `.py` diagram definition files.
2. For each identified diagram file, extract the base `<diagram_name>` (e.g., `handover_flow.d2` -> `handover_flow`).

### Phase 2: Generate Diagrams
1. Iterate through the discovered `.d2` files. Run `d2 docs/<diagram_name>.d2 docs/assets/<diagram_name>.png --theme=200`.
2. Iterate through any discovered `.py` diagram files. Run `python docs/<diagram_name>.py` (Output must be configured to generate `docs/assets/<diagram_name>.png`).
3. Verify that all base `<diagram_name>.png` files exist and are non-zero bytes.

### Phase 3: Verification & Update
1. Ensure `README.md` correctly references the final `.png` (or `.webp`) diagrams.
2. Report the generation to the user.

### Phase 4: Lossless Compression (WebP)
1. You MUST execute a Python snippet using the `Pillow` library to convert all newly generated `docs/assets/*.png` files into lossless `.webp` format.
2. You MUST delete the original `.png` files after successful conversion.
3. You MUST update `README.md` and any other references to point to the `.webp` files instead of `.png`.
