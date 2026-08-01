---
trigger: always_on
---

# Git Version Control Protocol

This rule ensures all version control operations go through the governance checkpoint workflow for observability and consistency. This file is `always_on`, not `manual` — git commands can be issued on any turn regardless of which file path is active, and per `00-03-meta-governance.md` Section 2's Trigger Classification Gate, an action this irreversible (unreviewed commits/pushes) fails the "does violating this even once risk an irreversible action" test and MUST be `always_on`. This brings the total always-on count to 5 of the 5-file budget — do not add another always-on file without first revisiting this budget with the user.

## 1. Mandatory Checkpoint Workflow
- **Rule**: All Git commit-and-push operations MUST be routed through the `.agents/workflows/secure-checkpoint.md` workflow.

## 2. Acceptable Git Commands
- **Read-only commands** are always permitted: `git status`, `git log`, `git diff`, `git remote -v`, `git branch`.
- **State-changing commands** (`git add`, `git commit`, `git push`, `git reset`, `git rebase`) MUST be executed exclusively as part of the `secure-checkpoint.md` workflow.

## 3. Workflow Annotations
- If a workflow file contains a `// turbo` flag next to a checkpoint instruction, it authorizes auto-running the checkpoint workflow.

# Git Remote Provisioning

### Rule: 00-git-remote-hallucination-prevention
- Owner layer: Global
- Scope: All GitHub repository initialization, remote creation, and pushing operations
- Stability: core
- Status: active
- Directive: When a user requests to push or upload code to GitHub and no remote exists, the agent MUST exclusively autonomously provision the remote using the GitHub CLI (`gh repo create`) as defined in the `/setup-git` workflow.
