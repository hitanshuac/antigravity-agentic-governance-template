---
name: Sync Upstream (Git SSOT)
description: Safely backports locally hardened rules and workflows to a remote Git repository acting as the Single Source of Truth.
---

# Sync Upstream Workflow (Git SSOT)

**Trigger:** Explicit invocation via `/ask run @[.agents/workflows/sync-upstream.md] <URL_OF_SSOT_REPO>`

This workflow automates the backporting of newly hardened rules and workflows from the local project to a central Git repository acting as the **Single Source of Truth (SSOT)**. This solves the issue of keeping the upstream template expanded without relying on manual copy-pasting or risking local hard drive paths.

> **Upgrade Path Role:** This workflow PUSHES battle-tested improvements back to the SSOT template. For pulling SSOT into a project being built, use `bootstrap.md`. For distributing to new child projects, use `copier copy`.

## Execution Steps

### 1. Pre-Flight Check & Repo Validation
- The user MUST provide the remote Git URL of the upstream repository (e.g., `https://github.com/hitanshuac/antigravity-agentic-governance-template.git`).
- The agent must verify it has access to the standard Git CLI tools.

### 2. Autonomous Cloning
- The agent MUST create a temporary directory inside the local workspace (e.g., `./tmp_ssot_sync`).
- Add `./tmp_ssot_sync/` to the `.gitignore` of the current project if not already present.
- Clone the remote upstream repository into `./tmp_ssot_sync/`.

### 3. File Delta Extraction & Patching
- The agent uses Git to programmatically identify modified framework files in the current repository:
  ```bash
  git log --name-status --oneline .agents/ tools/ src/antigravity/security/ tests/
  ```
- Identify all newly created or modified assets that represent "hardened" improvements across the following Golden Master paths:
  1. `.agents/` (Rules, Skills, Workflows) — **EXCLUDING `.agents/architecture/adrs/`**. ADRs are project-specific context and MUST NEVER be backported to the universal SSOT template.
  2. `tools/governance_eval/` (The transcript evaluation framework)
  3. `src/antigravity/security/` (Hardbaked components like `secure_llm_client.py`)
  4. `tests/` (Base testing infrastructure and fixtures)
  5. Base configs: `.pre-commit-config.yaml`, `ruff.toml`, `requirements.txt`
- Copy the identified files from the local project directly into the `./tmp_ssot_sync/` corresponding folders, creating directories if they don't exist.

### 4. Commit and Push to SSOT
- Navigate the terminal into `./tmp_ssot_sync/`.
- Run `git diff` and `git status` to see exactly what is being modified or deleted in the upstream repository.
- **Safety Gate:** If ANY files are marked for deletion or destructive overwrite, STOP and present the diff to the user. You MUST explicitly ask the user for permission to proceed before staging.
- Stage the newly copied files using `git add .` (ensuring all Golden Master paths are staged).
- Commit the changes with a semantic message (e.g., `feat: backport hardened rules and workflows from project`).
- Push the changes to the upstream remote repository (`git push origin main`).

### 5. Cleanup
- Navigate back to the root of the local project.
- Safely delete the `./tmp_ssot_sync` directory using `rm -rf ./tmp_ssot_sync` (or PowerShell `Remove-Item` on Windows).
- Remove the `./tmp_ssot_sync` entry from `.gitignore` if it was added in Step 2.

### 6. Handover Documentation
- Inform the user that the sync is complete.
- Print out the list of rules/workflows that were successfully backported to the remote SSOT repository.
