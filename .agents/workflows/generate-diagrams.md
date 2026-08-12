# Workflow: Generate All Diagrams

**Trigger:** Invoked by `master-sync.md` Phase 4, or manually via `/ask run @[.agents/workflows/generate-diagrams.md]`

## Objective
A dual-engine pipeline that combines repowise AST dependency intelligence with D2 conceptual diagrams:
1. **Repowise** — Tree-sitter AST parsing to build a directed dependency graph (imports, calls, inheritance, PageRank centrality) across all project code.
2. **D2** — Hand-authored conceptual architecture diagrams compiled to images with AI showcase styling.

## Execution Steps

### Phase 1: Repowise AST Index
1. Check for `repowise` CLI: `repowise --version`. If missing: `pip install repowise`.
2. If `.repowise/` directory exists, run incremental update:
   `repowise update`
3. If `.repowise/` does NOT exist, run first-time index (no API key required):
   `repowise init --yes --mode fast --no-editor-setup --no-claude-md --no-agents --no-codex --no-onboarding --no-harvest-decisions`
4. Verify the index is current:
   `repowise status`
5. Report node count, edge count, and any stale files to the user.

### Phase 2: Export Repowise Intelligence
1. Run `repowise status` to confirm the index is current. Report node count, edge count, and health score.
2. Run `repowise dead-code` to surface unreachable files and unused exports.
3. The primary output is the interactive dashboard (`repowise serve` → `localhost:3000`). No static export is needed — the `.repowise/` SQLite index is the source of truth.

### Phase 3: D2 Conceptual Diagrams (Preserved)
1. Scan the `docs/` folder (and any subfolders) for all `.d2` diagram definition files.
2. For each identified diagram file, extract the base `<diagram_name>` (e.g., `handover_flow.d2` -> `handover_flow`).
3. Run `d2 docs/<diagram_name>.d2 docs/assets/<diagram_name>_technical.png --theme=200 --sketch`.
4. Verify that all base `<diagram_name>_technical.png` files exist and are non-zero bytes.
5. If D2 CLI is not available, skip this phase and log a warning. The repowise phase is sufficient.

### Phase 4: The Showcase Styling Pass (D2 Diagrams Only)
1. Iterate through the list of generated `_technical.png` files from Phase 3.
2. For each diagram, read its `.d2` source to extract every node label, cluster name, and edge label.
3. Call `generate_image` with **two images in `ImagePaths`**:
   - `docs/assets/<diagram_name>_technical.png` (structural content base)
   - `docs/assets/handover_flow.png` (canonical aesthetic style reference)
4. Use the exact prompt template from `SKILL.md`, **explicitly listing every label** extracted in step 2.
5. Save the AI-styled output as `docs/assets/<diagram_name>_showcase.png`.

### Phase 5: Verification & Update
1. Ensure `README.md` references:
   - Both `_showcase` and `_technical` D2 diagram versions (for conceptual architecture)
   - Instructions for `repowise serve` to view the interactive AST dependency graph
2. Report the generation of both diagram engines to the user.

### Phase 6: Lossless Compression (JPEG)
1. Execute a Python snippet using the `Pillow` library to convert all newly generated `docs/assets/*.png` files into high-quality `.jpg` format.
   Use: `python -c "from PIL import Image; import glob, os; [ (Image.open(f).convert('RGB').save(f.replace('.png', '.jpg'), 'JPEG', quality=95), os.remove(f)) for f in glob.glob('docs/assets/*.png') ]"`
2. Delete the original `.png` files after successful conversion.
3. Update `README.md` and any other references to point to the `.jpg` files instead of `.png`.
