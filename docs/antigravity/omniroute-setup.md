# OmniRoute Setup Guide (Optional Enhancement)

OmniRoute is an open-source local AI gateway that aggregates 290+ AI providers
behind a single OpenAI-compatible endpoint (`localhost:20128/v1`). It provides
automatic fallback across providers, token compression, and cost-optimized
routing. This guide documents how to set it up alongside the Antigravity
governance template.

> **This is entirely optional.** The governance template works perfectly
> without OmniRoute. Nothing in `.agents/rules/`, `.agents/skills/`, or
> `.agents/workflows/` depends on it.

## What OmniRoute gives you

- **Auto-fallback:** If your primary provider (e.g., Gemini Pro) hits rate
  limits, OmniRoute silently routes to the next available provider.
- **Token compression:** RTK + Caveman stacked compression saves 15–95% of
  tokens on tool-heavy sessions (~89% average). This means more room in the
  context window for governance rules.
- **Free-tier aggregation:** Access to 90+ free AI provider tiers through
  one endpoint, extending your effective quota without additional cost.
- **MCP server:** 104+ tools accessible via the Model Context Protocol.

## Installation

### Option A: npm (Recommended)

```bash
npm i -g omniroute
```

### Option B: Docker

```bash
docker pull diegosouzapw/omniroute
docker run -p 20128:20128 diegosouzapw/omniroute
```

### Option C: Electron Desktop App

Download from the [OmniRoute Releases](https://github.com/diegosouzapw/OmniRoute/releases) page.

## Verify it's running

```bash
curl http://localhost:20128/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"Hello!"}]}'
```

If you get a response, OmniRoute is live.

## Configure Antigravity IDE

In Antigravity IDE, update your LLM base URL to point to OmniRoute:

1. Open **Settings → Advanced Settings**
2. Set the API base URL to `http://localhost:20128/v1`
3. Set the model to `auto/coding` for quality-first code generation routing

## Recommended Combo Strategy

For a user with free Gemini Pro and occasional Claude Opus access, this
routing priority maximizes value:

| Tier | Provider | Purpose |
|------|----------|---------|
| 1 (Primary) | Gemini Pro (subscription) | Your default — zero additional cost |
| 2 (Secondary) | Claude Opus (API key) | Complex reasoning, large context tasks |
| 3 (Cheap) | DeepSeek, Groq | Budget API calls for simple tasks |
| 4 (Free) | OpenCode Free, Felo | Fallback when all else is exhausted |

OmniRoute's `auto/coding` model ID handles this cascade automatically
based on your connected providers.

## Governance Compatibility Notes

- OmniRoute's token compression is a black box — there is no way to verify
  whether it preserves or strips `.agents/rules/` content from the context
  window. If you notice governance rules being ignored after enabling
  compression, disable it and test again to isolate the cause.
- If OmniRoute falls back from a flagship model (e.g., Opus) to a free-tier
  model mid-session, the weaker model may not follow complex governance rules
  as reliably. Monitor the OmniRoute dashboard at `http://localhost:20128`
  to see which provider is actually handling your requests.

## Version Tested

This guide was written against OmniRoute as of August 2026. OmniRoute is
actively developed — if commands or configuration options have changed,
consult the [official README](https://github.com/diegosouzapw/OmniRoute).
