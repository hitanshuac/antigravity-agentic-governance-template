---
name: Local Bootstrapper
description: Workflow to scaffold and verify the local environment before execution.
---

# Bootstrap Workflow

When initiating the workspace or onboarding a new developer/agent, execute these steps sequentially to ensure the 12-Factor App methodology is satisfied locally.

## Phase 0: Environment Upgrade Protocol (For Existing Repositories)
If you are running `bootstrap.md` in a repository that already has an older version of Antigravity installed:
1. **Clone Latest Upstream:** Run `git clone https://github.com/hitanshuac/Antigravity_Environment_Max.git .agents/tmp/antigravity_latest` (or equivalent URL).
2. **Verify Semantic Release Context:** Ensure the latest `.agents/workflows/semantic-release.md` is pulled down locally to serve as the versioning anchor.
3. **Additive Document Merge:** Copy all entirely *new* `.md` workflows, rules, and product templates from `.agents/tmp/antigravity_latest/` into your local root and `.agents/` directory. Do not destructively overwrite existing modified workflows unless explicitly requested.
4. **Union Merge Boilerplate:** Execute `.agents/workflows/merge-conflict-resolution.md` to safely union-merge lists like `.gitignore` and `requirements.txt`.
5. **Cleanup:** Delete the `.agents/tmp/antigravity_latest` folder and proceed to Phase 1.

## 1. Verify Factor I (Codebase)
Ensure the repository is fully cloned and the `.agents` folder is intact.

## 2. Verify Factor II (Dependencies)
- Confirm `requirements.txt` exists and all dependencies are pinned.
- Run `pip install -r requirements.txt` inside the virtual environment.
- Confirm `.venv/` is excluded by `.gitignore`.

## 3. Verify Factor III (Config)
- Check if `.secrets` exists. If not, generate it.
- Run a search for leaked API keys inside `src/`. If any are found, immediately purge them and move them to `.secrets`.
- Ensure `.gitignore` is active and blocking `.secrets/`, `.env`, and `data/`.
- **Remote CI/CD Alignment:** Execute `.agents/workflows/setup-secrets.md` to ensure the upstream GitHub repository is provisioned with the required Action secrets (`HF_TOKEN`, `HF_SPACE_REPO`).

## 4. Verify Product Design Gate
- Confirm that `.agents/product/templates/` exists and contains all 5 templates (`01_PRD.md`, `02_TAD.md`, `03_SECURITY.md`, `04_FRONTEND.md`, `05_TICKETS.md`).
- If the user is building a new project, execute `.agents/workflows/generate-product-docs.md` to populate them before allowing any code generation.

## 5. Verify Factor VI (Processes)
- Start the ASGI server (e.g., `uvicorn src.server:app`).
- Validate that the router accepts stateless requests and successfully pushes telemetry via lock-free queues.

## 6. Verify Factor XI (Logs)
- Ensure the `data/` directory exists (with `.gitkeep`).
- Confirm `pipeline_metrics.db` is being generated and that Parquet files populate inside `data/quarantine_*` on failure.

## 7. Verify Local Enforcement (Pre-commit)
- Confirm `.pre-commit-config.yaml` exists at the repo root.
- Run `pre-commit install` to ensure hooks are active.
- Run `ruff check .` and `ruff format --check .` to validate the codebase passes linting.

## 8. Verify Testing Infrastructure
- Confirm `src/tests/` exists with at least one test file.
- Run `python -m pytest src/tests/ -v` to ensure all existing tests pass.
- If tests fail, execute `.agents/workflows/error-observability.md` to log and diagnose the failures.
