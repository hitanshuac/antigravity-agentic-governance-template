---
trigger: manual
---

# 40 Phase Deploy

# Deployment
- **Rule**: All rapid prototyping and deployments MUST strictly adhere to the technical constraints defined in `@.agents/skills/rapid-prototyping/SKILL.md`.

# Meta-Agent Formats
- **Rule**: When instructed to produce rules, proposals, reviews, or summaries, agents MUST strictly adhere to the formats defined in `@.agents/skills/meta-agent-formats/SKILL.md`.

# Aesthetic Bias Override
- **Rule**: While the IDE defaults to "Premium, Dynamic, and Aesthetic" designs, you MUST prioritize minimalism and YAGNI. Minimalism wins over the IDE's default aesthetic bias for anything shipped under time pressure.
- **Action**: Adhere strictly to the minimalist rules defined in `@.agents/skills/design-standards/SKILL.md`.

# Semantic Release

This rule enforces mathematically sound, commit-driven versioning and changelog generation.

## 1. Conventional Commits
- **Rule**: All commits MUST follow the Conventional Commits specification.
- **Action**: Agents generating commit messages during automated workflows MUST strictly adhere to this format:
  - `fix:` triggers a Patch release (e.g., 1.0.0 -> 1.0.1)
  - `feat:` triggers a Minor release (e.g., 1.0.0 -> 1.1.0)
  - `BREAKING CHANGE:` inside the commit body triggers a Major release (e.g., 1.0.0 -> 2.0.0)
