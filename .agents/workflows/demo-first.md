---
name: demo-first
description: Build the demo script BEFORE the implementation. Ensures the "wow moment" works flawlessly by designing backwards from the presentation.
slash_command: /demo-first
---

# Demo-First Workflow

Most hackathon losses come from demos that crash, not from missing features.
This workflow inverts the build order: design the demo script first, identify
the exact happy path that MUST work, build only what the demo needs, then
harden it until it cannot fail during presentation.

---

## Step 1: Write the Demo Script

Create `DEMO_SCRIPT.md` in the project root. // turbo

The demo script is a second-by-second walkthrough of what you will show:

```markdown
# Demo Script ([Project Name])
**Duration:** [3-5 minutes]
**Presenter:** [name]

## Opening (30 seconds)
"[Opening line that hooks the audience. State the problem in one sentence.]"
- Show: [what's on screen — landing page, dashboard, etc.]

## The Problem (30 seconds)
"[Explain the pain point. Use a concrete example.]"
- Show: [visual showing the problem — messy data, manual process, etc.]

## The Solution (60 seconds)
"[Demonstrate the core feature. This is the 'wow moment'.]"
- Action: [exact click/input sequence]
- Expected: [exact output/response the audience will see]
- Fallback: [what to show if the API is slow or fails]

## Deep Dive (60 seconds)
"[Show a second use case or the AI reasoning behind the output.]"
- Action: [click/input]
- Expected: [output]

## Architecture (30 seconds)
"[Brief technical overview — keep it high-level for judges.]"
- Show: [architecture diagram or tech stack slide]

## Impact (30 seconds)
"[Quantify the value. 'This saves X hours per week' or 'This serves Y users'.]"
- Show: [metrics dashboard or before/after comparison]

## Close (30 seconds)
"[Call to action. 'We're live at [URL]. Try it now.']"
- Show: [the deployed URL on screen]
```

**Exit Gate:** User approves the demo script before any code is written.

---

## Step 2: Identify the Critical Path

From the demo script, extract the **exact sequence of interactions** that MUST work:

```markdown
## Critical Path (MUST NOT FAIL)
1. Page loads within 3 seconds → shows [landing UI]
2. User enters [specific input] → system processes in under 5 seconds
3. System displays [specific output] → matches expected format
4. User clicks [specific button] → triggers [specific behavior]
5. Final state shows [specific result]

## Volatile Dependencies
| Dependency | Risk | Fallback |
|:---|:---|:---|
| [External API X] | Rate limits, downtime | Mock response from `data/mock_api_x.json` |
| [LLM API] | Slow response, token limits | Pre-cached response for demo input |
| [Database] | Cold start | Pre-seeded sample data |
```

---

## Step 3: Build the Fallback Layer

Before implementing the real features, build the fallback/mock layer:

1. Create `data/demo/` directory with mock responses for every external API // turbo
2. Create a `DEMO_MODE` environment variable that switches between real and mock
3. For each volatile dependency, implement:
   ```python
   if os.getenv("DEMO_MODE") == "true":
       return load_mock_response("api_x_response.json")
   else:
       return call_real_api(params)
   ```

This ensures the demo ALWAYS works, even if external services are down.

---

## Step 4: Implement Against the Demo Script

Build features in demo-script order, not in logical/architectural order:

1. Build whatever produces the "wow moment" output FIRST
2. Build the UI that displays it SECOND
3. Build supporting features THIRD
4. Polish error states LAST

After each feature, run the full critical path to verify nothing broke.

---

## Step 5: Demo Rehearsal

Before the presentation, execute this rehearsal protocol:

1. **Cold start test:** Close everything. Open a fresh browser. Navigate to the
   deployed URL. Run the full demo script. Record any friction.
2. **Slow network test:** Throttle to 3G in browser devtools. Run the demo.
   Does it still work within acceptable timeframes?
3. **Failure injection:** Temporarily break an external API (set a wrong key).
   Does the fallback activate cleanly?
4. **Timing test:** Time the full demo. Is it within the time limit?

Fix any issues found. Run the rehearsal again until all 4 tests pass.

---

## Anti-Patterns

- **Building features the demo never shows:** Every feature costs time. If it's
  not in the demo script, it doesn't exist for judges.
- **Live-coding during the demo:** Everything MUST be pre-built and working.
  The demo shows a finished product, not a development process.
- **No fallback:** If your demo depends on a live API and that API goes down
  during judging, you lose. Always have a mock layer.
- **Feature creep post-demo-script:** Once the demo script is approved, adding
  new features to it requires removing existing ones to stay within time.
