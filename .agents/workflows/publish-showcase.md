---
description: Automatically synthesize project logs, verify show-case assets, and push updated documentation to GitHub.
---

# Publish Showcase Workflow

1. Read the current project documentation (`README.md`, `HANDOVER.md`, and any existing `retrospective.md` or `walkthrough.md` if present).
2. Synthesize these files to update the `README.md` with the newest version baseline, SRE guardrails, and metrics.
3. **Verify Documentation Assets (Dual-Presentation Mandate):**
   - Confirm that the recruiter-facing showcase PNG (`docs/assets/architecture_diagram.png`) exists and is referenced at the top of `README.md`.
   - **Asset Generation Rules:** If the PNG is missing or is a placeholder, you must **NEVER** use an AI image generator (like DALL-E or Imagen). Instead, execute the `@[.agents/skills/diagram-generator/SKILL.md]` to programmatically generate the diagram using either Python `diagrams` or `D2`. Ensure the output path correctly overwrites `docs/assets/architecture_diagram.png`.
   - Confirm that the technical Mermaid diagram is present in the flow/architecture section.
4. Show the proposed changes to the user for approval.
5. Once approved, stage the files:
   - Run `git add README.md retrospective.md walkthrough.md docs/assets/architecture_diagram.png`
6. Commit the changes:
   - Run `git commit -m "docs: sync v1.0.0 showcase documentation and SRE assets"`
7. **Push to the main GitHub repository:**
   - Execute `git remote -v` to check if an `origin` remote exists.
   - If an `origin` remote **is missing**, halt and execute the `@[.agents/workflows/setup-git.md]` workflow to autonomously provision the repository using the GitHub CLI.
   - Run `git branch -M main`.
   - Run `git push -u origin main`.
8. Confirm to the user that the showcase and SRE metrics are live on GitHub.