---
trigger: glob
glob: ".agents/**/*.md"
---

# 26 Context Budget Management

This rule extends the character budget enforcement from @.agents/rules/00-03-meta-governance.md
to cover ALL governance artifacts (not just rules), and adds proactive token-cost awareness.

This rule uses the same glob trigger as `00-03-meta-governance.md`. Per Section 2 of that
file, this is a genuinely distinct concern (budget enforcement vs. creation process) that
fires on the same paths, justified by the distinct failure mode it prevents: token bloat
from governance artifacts consuming the agent's context window.

---

## 1. Character Limits by Artifact Type

| Artifact Type | Hard Cap | Warning Threshold (80%) |
|:---|:---|:---|
| Rules (`.agents/rules/`) | 12,000 chars | 9,600 chars |
| Skills (`.agents/skills/**/SKILL.md`) | 8,000 chars | 6,400 chars |
| Workflows (`.agents/workflows/`) | 10,000 chars | 8,000 chars |

Skills have a lower cap than rules because they use progressive disclosure:
the description field in frontmatter is loaded for matching, and the full body
is loaded only when the skill triggers. A bloated skill body directly taxes
the context window on every invocation.

---

## 2. Progressive Disclosure Enforcement

Every SKILL.md file MUST follow this structure:

1. **Frontmatter (YAML):** `name` and `description` only. The description MUST
   be under 500 characters and MUST include trigger phrases.
2. **Body (Markdown):** The full instructions. MUST be under the 8,000-char cap.
3. **References (optional):** For content exceeding the cap, use a `references/`
   subdirectory with additional markdown files that the agent reads on demand.

The agent MUST NOT load reference files unless the skill has already triggered.

---

## 3. Workflow Command Classification Enforcement

Per @.agents/rules/00-03-meta-governance.md Section 5, every terminal command in a
workflow MUST be classified. This rule adds a verification step:

Before saving a new or modified workflow, the agent MUST scan for any `backtick`
command blocks that lack a `// turbo` tag or an explicit approval gate. Unclassified
commands MUST be classified before the file is saved.

---

## 4. Skill Deduplication by Capability

Before creating a new skill, the agent MUST check if an existing skill already
covers the same capability by searching for:
- The same tool/library name in skill descriptions
- The same trigger phrases across all SKILL.md files
- Overlapping `name` fields

If overlap is found, extend the existing skill instead of creating a new one.
This prevents the "skill sprawl" anti-pattern where 5 thin skills exist for
aspects of the same domain (e.g., separate skills for "DuckDB queries,"
"DuckDB optimization," and "DuckDB schema design").
