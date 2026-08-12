---
name: OmniRoute Gateway
description: "Optional local AI gateway integration. Checks if OmniRoute is running, assists with configuration, and provides routing guidance. TRIGGERS: 'set up omniroute', 'configure omniroute', 'configure routing', 'omniroute setup', 'AI gateway', 'omniroute'."
---

# OmniRoute Gateway (Optional)

OmniRoute is a local AI gateway that routes LLM calls across 290+ providers
with automatic fallback and token compression. This skill assists with setup
and configuration. It is entirely optional — the governance template works
without it.

## Pre-Flight Check

Before configuring, verify OmniRoute is running:

```bash
curl http://localhost:20128/health
```

If the health check fails, direct the user to the setup guide at
`docs/antigravity/omniroute-setup.md`.

## Configuration Guidance

1. **Verify installation:** Run the health check above.
2. **Point the IDE:** Set the LLM base URL in Antigravity IDE settings to
   `http://localhost:20128/v1`.
3. **Select a routing model:** Use `auto/coding` for quality-first code
   generation, or `auto/cheap` for cost-optimized routing.
4. **Verify routing:** Make a test request and check the OmniRoute dashboard
   at `http://localhost:20128` to confirm which provider handled it.

## MCP Server (Optional)

OmniRoute ships with an MCP server exposing 104+ tools. To register it:

1. Confirm the MCP server is running alongside OmniRoute.
2. Add the OmniRoute MCP endpoint to your IDE's MCP server configuration.
3. **Curate tools carefully** — registering all 104 tools pollutes the
   agent's tool namespace. Only register tools you actively use.

## Graceful Degradation

This skill MUST NOT create any hard dependency on OmniRoute. If OmniRoute
is not running:

- All governance rules, skills, and workflows MUST function identically.
- The agent MUST inform the user that OmniRoute is not detected and point
  to `docs/antigravity/omniroute-setup.md` for installation instructions.
- The agent MUST NOT retry OmniRoute health checks in a loop — check once,
  report the result, and move on.

## Reference

- Setup guide: `docs/antigravity/omniroute-setup.md`
- OmniRoute repository: https://github.com/diegosouzapw/OmniRoute
