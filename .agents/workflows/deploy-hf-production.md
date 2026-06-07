---
description: Master workflow to synthesize documentation, update schemas, publish to GitHub, and deploy to Hugging Face Spaces.
---

# HF Production Deployment Workflow

This workflow orchestrates the entire deployment pipeline. Every time the code is deployed to Hugging Face, these steps MUST be executed in order:

## Step 1: Pre-Flight Credential Provisioning
1. Before attempting any deployment, you MUST guarantee the CI/CD runner has the credentials it needs.
2. Execute the `.agents/workflows/setup-secrets.md` workflow.
3. This will ensure `HF_TOKEN` and `HF_SPACE_REPO` are securely pushed to GitHub Actions via the `gh` CLI.

## Step 2: Verification & Rule Auditing
1. Read `.agents/rules/hf-deployment-standards.md` to ensure all execution requirements (webhook, port binding, memory limits) are met.
2. If using `python-telegram-bot`, verify that `httpx` is strictly configured within `~=0.26.0` range in your `requirements.txt`.

## Step 3: Codebase-to-Document Synchronization
1. Analyze the updated codebase (`src/capabilities/`, etc.).
2. Synchronize API schemas, route definitions, and cascade rules across:
   - `docs/`
   - `.agents/rules/`
3. Update version designations in all files to the current release (e.g., `v1.0.0`).

## Step 4: Showcase & Flow Asset Updates
1. Ensure the system architecture showcase image (`docs/assets/architecture_diagram.png`) represents the current cascade engine (10-Tier Cascade, SPA web client, webhook bot). If the version has changed, generate a new image and place it in the assets directory.
2. Verify that the Mermaid technical flow diagram in `README.md` is aligned with the codebase's cascading fallback logic.

## Step 5: Publish Showcase on GitHub (Call Sub-Workflow)
1. Run the `publish-showcase.md` workflow.
2. This will synthesize `retrospective.md`, `walkthrough.md`, and `implementation_plan.md` into `README.md`.
3. In `README.md`, ensure **both** the recruiter-facing static PNG and the technical Mermaid flow are visible:
   - Recruiter Showcase: `![Architecture Diagram](docs/assets/architecture_diagram.png)` at the top of the file.
## Step 6: Push to Hugging Face Spaces (CI/CD)
1. Ensure the `.github/workflows/deploy_hf.yml` action exists in the repository.
2. Do NOT run `upload_to_hf.py` locally. It requires secret tokens.
3. Instead, commit and push all changes to GitHub (`origin/main`). The GitHub Action will automatically trigger the `upload_to_hf.py` script using the repository's securely stored `HF_TOKEN`.
