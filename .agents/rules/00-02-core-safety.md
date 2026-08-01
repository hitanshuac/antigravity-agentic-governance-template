---
trigger: always_on
---

# Anti-Sycophancy Protocol

### Rule: 00-anti-sycophancy-protocol
- Owner layer: Global
- Scope: All agentic actions, tool calls, and architecture planning
- Stability: core
- Status: active
- Directive: If the USER requests an action, filename, or architecture pattern that violates the established `.agents/` conventions, the agent MUST explicitly reject the user's specific instruction, explain the violation, and implement it exclusively using the correct framework standard.

# Local-First Verification Gate

### Rule: 00-local-first-verification
- Owner layer: Global
- Scope: All architectural planning and environmental setup
- Stability: core
- Status: active
- Directive: The agent MUST explicitly verify the local host environment via terminal commands (checking IDE versions, dependencies, etc.) BEFORE proposing architectural changes from external web searches. If the local environment does not support the external concept, the agent MUST halt and discard the external data.
