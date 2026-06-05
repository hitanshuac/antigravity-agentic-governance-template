# Workflow: Safe Merge & Conflict Resolution

**Trigger:** MANDATORY Pre-flight check. Must be executed *before* scaffolding or merging this Base Agentic Environment into any existing project.

## Objective
This repository must act purely as an addon, booster, or enhancer. It must **NEVER** instruct the deletion of any existing project files without explicit manual approval from the user. This is a strict mandate rule.

## Execution Steps

### 1. Identify File Collisions
- Scan the target repository and compare it against the incoming Base Environment files.
- Identify all file collisions (e.g., if the target project already has a `README.md`, `data/error_logs.json`, or `HANDOVER.md`).

### 2. Markdown Override Protocol (Pending Approval)
- For Markdown (`.md`) files and structural logs, the design intent is that the file coming from this Base Environment should supercede the file in the existing project.
- **MANDATORY HOLD:** You must pause execution and present a list of all colliding `.md` files to the user.
- You must wait for explicit manual approval for *each* conflict before overwriting the file.

### 3. Absolute No-Deletion Mandate
- If you encounter obsolete folders (like a stale `.antigravity/` cache) or files that you believe should be deleted to prevent conflicts, **DO NOT DELETE THEM AUTOMATICALLY.**
- Any deletion must be proposed to the user and requires explicit authorization to proceed.

### 4. Proceed to Scaffolding
- Only after all collisions have been manually approved by the user may you proceed with the actual merge and bootstrapping phases.
