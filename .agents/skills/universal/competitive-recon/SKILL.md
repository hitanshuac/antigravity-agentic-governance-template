---
name: competitive-recon
description: "Rapidly analyzes competition landscape and prior art before building. Finds what exists, identifies gaps, and frames your project as a clear improvement. TRIGGERS: 'what else exists', 'competitive analysis', 'prior art', 'similar projects', 'how is this different', 'market research', 'landscape analysis', 'what are others doing'."
---

# Competitive Recon Skill

Before building anything, understand what already exists. This skill provides
a structured approach to competitive analysis that takes 15-30 minutes and
produces actionable differentiation points.

---

## The 4-Step Recon Protocol

### Step 1: Landscape Scan (10 minutes)

Search for existing solutions using these queries:

1. **GitHub:** `[problem domain] [tech stack]` — sort by stars, filter to last 6 months
2. **Product Hunt / HN:** `[problem domain] AI` — look for launched products
3. **Academic:** If the problem has a research angle, check arXiv for recent papers

For each relevant result, capture:

```markdown
## Landscape Scan

| Project | Stars/Users | Approach | Strengths | Weaknesses |
|:---|:---|:---|:---|:---|
| [Name](URL) | [count] | [how they solve it] | [what they do well] | [what's missing] |
```

### Step 2: Gap Analysis (5 minutes)

From the landscape scan, identify the gaps:

```markdown
## Gap Analysis

### What Everyone Does
- [Common approach 1]
- [Common approach 2]

### What Nobody Does (Your Opportunity)
- [Gap 1]: [why it matters]
- [Gap 2]: [why it matters]

### What They Do Badly (Your Improvement)
- [Weakness 1]: [how you'd do it better]
```

### Step 3: Differentiation Statement (5 minutes)

Write a single sentence that captures your unique value:

```
"Unlike [existing solutions] which [limitation], [your project]
[unique capability] by [technical approach]."
```

Examples:
- "Unlike existing stadium chatbots which only answer FAQs, our system
  proactively alerts fans about crowd density using real-time sensor data."
- "Unlike manual code review tools which flag issues after the fact, our
  system prevents architectural drift in real-time using AST analysis."

### Step 4: Judge-Ready Framing (5 minutes)

Frame your differentiation in terms judges care about:

```markdown
## Why This Wins

### Technical Innovation
[What's novel about your approach — not just "we used AI"]

### Real-World Impact
[Quantifiable benefit — hours saved, errors prevented, users served]

### Execution Quality
[What shows craftsmanship — UI polish, error handling, deployment]

### Completeness
[Working demo > feature list. What works end-to-end?]
```

---

## Integration with Other Workflows

- Run this skill BEFORE @.agents/workflows/spec-first.md to inform the spec
- Feed the differentiation statement into @.agents/workflows/demo-first.md
  to ensure the demo highlights what makes you unique
- Store the recon results in `SPEC.md` under a "## Competitive Context" section

---

## Anti-Patterns

- **Paralysis by comparison:** The goal is to find gaps, not to catalog every
  competitor. 15-30 minutes max, then move on.
- **Feature-matching:** Do NOT try to build everything competitors have. Build
  ONE thing they do NOT have, and build it well.
- **Dismissing competitors:** If a strong competitor exists, acknowledge it and
  clearly articulate why your approach is different or better. Judges respect
  awareness more than ignorance.
