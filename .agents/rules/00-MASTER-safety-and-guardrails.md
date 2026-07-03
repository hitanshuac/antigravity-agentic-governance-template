# 00-MASTER-safety-and-guardrails



---
### Source: `00-00-MASTER-safety-and-guardrails.md`
---

# Agent Terminal Execution Constraint (Anti-Hallucination Protocol)

This rule defines the strict operational boundaries for the AI Agent when executing terminal commands, specifically targeting the prevention of synthetic data hallucination caused by asynchronous race conditions or failed executions.

## 1. Zero-Tolerance for Hallucinated Output
- **Rule**: If an exploratory or ad-hoc terminal command (e.g., `run_command`) fails with a non-zero exit code or encounters a missing dependency, the agent **MUST NEVER** attempt to answer the user's prompt based on anticipated success or pre-training priors.
- **Why**: Providing synthetic snippets when actual data is unavailable corrupts the user's trust and violates the core principles of data engineering.

## 2. Explicit Failure Reporting
- **Rule**: Upon a failed command execution, the agent MUST explicitly state to the user: "The command failed with [Error Message]."
- **Action**: Do not hide Python tracebacks, module not found errors, or syntax errors behind conversational apologies. Surface the exact exception.

## 3. Mandatory Re-Execution Loop
- **Rule**: If the agent attempts to autonomously fix the error (e.g., by running `pip install` or fixing a syntax error), it MUST explicitly re-run the original extraction/analysis command and successfully read the output BEFORE formulating a response about the data.
- **Action**: You must verify the exit code of the final command is `0` and wait for the `command_status` to return the real textual output before parsing it for the user.

## 4. Interaction with Other Rules
- This rule is considered Tier 0 (Safety & Truthfulness) under `00-MASTER-safety-and-guardrails.md`. It overrides any conversational bias to "be helpful" or "keep the chat moving." The truthfulness of the terminal output is absolute.

## 5. Meta-Agent SOP: Building New Rules
Because the Antigravity repository relies heavily on autonomous execution, any future AI Agent tasked with creating or modifying a rule in `.agents/rules/` MUST adhere strictly to the **Rule Entry Template** defined in `30-MASTER-compliance-and-deploy.md`.

If an agent builds a rule without following the exact `Scope`, `Stability`, `Directive`, `Rationale`, and `Conflict handling` structure, it is considered invalid.

### Checkpoints and Deliverables
When generating proposals, orchestrating council peer-reviews, or pausing for human intervention, the agent MUST use the precise formatting templates defined in `30-MASTER-compliance-and-deploy.md`.

### Hierarchy Checks
Before saving a new rule, the agent MUST run `grep_search` across `.agents/rules/` or view `00-MASTER-safety-and-guardrails.md` to ensure the new rule does not conflict with existing Tier 0 or Tier 1 safety constraints.


---
### Source: `00-agent-execution-standards.md`
---

# Agent Execution Standards

This rule governs the fundamental operational behaviors of any AI agent operating within or pulling from this environment.

## 1. Assert State Currency (Anti-Staleness Protocol)
AI agents have a tendency to hallucinate templates or operate blindly on stale local clones.
- **Rule:** You MUST always assert state currency by running `git pull origin main` immediately prior to executing read/scaffold workflows on any cloned reference repository.
- Ensure your context is 100% current before reading architectural workflows or applying templates.


---
### Source: `00-00-MASTER-safety-and-guardrails.md`
---

---
description: Defensive programming standards to prevent silent data corruption, schema mismatches, and error swallowing across all SDLC phases.
trigger: always_on
priority: tier_0_safety
---

# Defensive Programming Standards

This rule codifies senior-engineer defensive programming SOPs that prevent silent data loss, schema drift, and error obfuscation. It applies to ALL code generation, regardless of project constraints (e.g., strict rules, MVP, production).

> **Post-Mortem Origin:** This rule was created after a root-cause analysis where an agent silently wiped a JSON error log because it assumed a flat `[]` list schema while the existing file used a `{"session_errors": [...]}` dictionary. Unit tests passed because they ran against empty temp directories, never touching the real file.

## 1. Schema-First Data Contracts (Mandatory for All I/O)

- **Rule**: Before writing ANY code that reads or writes a persistent file (JSON, TOML, YAML, CSV, Parquet), the agent MUST first read the existing file (if it exists) and document its exact schema.
- **Why**: LLMs lose file-schema context after 100+ conversation steps. Without an explicit contract, the agent will make statistically probable assumptions about file structure that may silently destroy data.
- **Action**:
  - Define a Pydantic model or `TypedDict` at module level for every persistent data structure. Raw `json.load()` followed by `isinstance()` type-guessing is **strictly forbidden**.
  - The Pydantic model is the **single source of truth**. If the existing file does not match the model, the code must raise a descriptive `ValueError` or `SchemaError` and halt. It must **NEVER** silently overwrite or reset the file.
  - When Pydantic is unavailable (e.g., dependency constraints), use Python `TypedDict` with explicit runtime validation using `assert` or `if not` guard clauses.

### Example (Correct):
```python
from pydantic import BaseModel

class ErrorLogEntry(BaseModel):
    timestamp: str
    error_type: str
    component: str
    message: str
    status: str  # "UNRESOLVED" | "RESOLVED"

# Module-level schema: the log file is a JSON array of ErrorLogEntry
ErrorLogSchema = list[ErrorLogEntry]
```

### Example (Forbidden):
```python
# FORBIDDEN: guessing the schema at runtime
logs = json.load(f)
if not isinstance(logs, list):
    logs = []  # THIS SILENTLY DESTROYS DATA
```

## 2. Fail Fast, Never Fail Silent

- **Rule**: Functions that interact with external services (APIs, file I/O, databases) MUST surface the actual error to the caller. Generic fallback strings without logging are forbidden.
- **Why**: Generic messages like "Something went wrong" or "I'm having trouble connecting" make debugging impossible and waste significant developer time.
- **Action**:
  - Every `except` block MUST log `type(e).__name__` and `str(e)` to the observability layer (see `error-observability.md`) BEFORE returning any user-facing message.
  - The user-facing message MAY be friendly and generic, but the log entry MUST contain the real exception class, message, and the component where it occurred.
  - Replace bare `except:` and `except Exception:` with specific exception types. If a catch-all is truly necessary, it must be the LAST handler and must log at ERROR level with full context.

### Example (Correct):
```python
except google.api_core.exceptions.ResourceExhausted as e:
    log_error_to_json("ResourceExhausted", "llm_engine", str(e))
    return fallback_message
except Exception as e:
    log_error_to_json(type(e).__name__, "llm_engine", str(e))
    return fallback_message
```

### Example (Forbidden):
```python
except Exception:
    return "I'm having trouble connecting right now."
```

## 3. Idempotent File Operations

- **Rule**: All file append operations MUST be idempotent. Running the same write operation twice must not corrupt, duplicate, or lose data.
- **Why**: Agentic pipelines frequently retry operations after crashes. Without idempotency, retries cause data duplication or loss.
- **Action**:
  - For JSON append operations: Read the file, deserialize, validate the schema, append the new entry, serialize, and write back atomically.
  - Use atomic write patterns where possible: write to a `.tmp` file first, then rename to the production path. This prevents partial writes from corrupting the file if the process crashes mid-write.
  - After every write, perform a post-write verification: re-read the file and assert `len(after) >= len(before)`. If the assertion fails, the write corrupted data and the agent must halt immediately.

## 4. Guard Clauses and Input Validation at Boundaries

- **Rule**: Every public function must validate its inputs in the first 3 lines using guard clauses.
- **Why**: Invalid inputs propagating deep into call stacks produce confusing, hard-to-trace errors.
- **Action**:
  - Validate type, nullability, and range at function entry.
  - Invalid inputs must raise `ValueError` or `TypeError` with a descriptive message including the parameter name and the invalid value.
  - Never trust data from disk, network, or user input. Always validate after deserialization.

### Example (Correct):
```python
def log_error_to_json(error_type: str, component: str, message: str) -> bool:
    if not error_type or not isinstance(error_type, str):
        raise ValueError(f"error_type must be a non-empty string, got: {error_type!r}")
    if not component or not isinstance(component, str):
        raise ValueError(f"component must be a non-empty string, got: {component!r}")
    # ... proceed with validated inputs
```

## 5. Relationship to Other Rules

- This rule is **Tier 0 (Safety)** in the rule priority hierarchy defined in `00-MASTER-safety-and-guardrails.md`.
- When project constraints (e.g., a "no databases" rule) conflict with this rule, the agent must find an alternative implementation that satisfies BOTH rules, not silently skip data integrity.
- Example: If DuckDB is forbidden, use Pydantic + JSON files instead of raw `json.load()` guessing. The schema validation mandate is non-negotiable.


---
### Source: `00-deterministic-guardrails.md`
---

# Deterministic Guardrails Protocol

This is a Tier 0 Master Rule. LLMs are probability engines, not human developers. Conversational English, weak modals, and implicit instructions drastically increase the hallucination probability. This rule dictates how all other rules, workflows, and skills MUST be interpreted and written.

## 1. No Weak Modals
- You MUST interpret all instructions as absolute constraints.
- Words like "MUST", "could", "MUST", or "strictly" are strictly forbidden in all agentic documentation. Treat any existing weak modals as "MUST".

## 2. Positive Framing over Negative Banning
- Do NOT use negative framing (e.g., "do not use raw SQL").
- ALWAYS use positive boundary framing (e.g., "ONLY use DuckDB Pydantic models"). Negative framing injects the forbidden concept into the context window, increasing hallucination probability.

## 3. Strict Command Sandboxing
- Workflow files MUST NOT use abstract verbs for tooling (e.g., "Execute the Git tool").
- Every executable action MUST provide the exact CLI string required, sandboxed inside markdown backticks (e.g., `python src/capabilities/git_manager.py checkpoint`).
- If a workflow step lacks an exact CLI string, you MUST halt and ask the user for clarification. Do not hallucinate a command to fulfill the abstract intent.

## 4. Architectural Adherence (XML Boundaries)
- Where possible, instructions and constraints MUST be enclosed in strict XML tags (e.g., `<trigger>`, `<action>`, `<constraint>`) to provide explicit semantic boundaries for the LLM context window.

> **Post-Mortem Origin:** This master rule was implemented after an LLM Council analysis identified that conversational English, split instructions, and weak modals were the root cause of multiple agentic IDE hallucinations, including the bypass of the secure checkpoint workflow.


---
### Source: `00-git-ban.md`
---

# Global Git Command Ban (Anti-Hallucination Protocol)

This rule was implemented to prevent Semantic Override failures where the agent hallucinates a local git command instead of executing upstream synchronization protocols.

## 1. Strict Prohibition of Raw Git Commands
- **Rule**: You MUST NEVER execute raw `git` commands in the terminal (e.g., `git add`, `git commit`, `git push`, `git pull`).
- **Why**: Bypassing the Python Git Manager (`git_manager.py`) disables the error observability layer, breaks pre-commit hooks, and can result in local checkpoints that fail to synchronize with remote state.

## 2. Mandatory Method for Version Control
- All source control and versioning operations MUST be routed exclusively through the Python Git Manager.
- **Command**: `python src/capabilities/git_manager.py checkpoint "[Your descriptive commit message]"`
- This Python script safely wraps the staging, committing, and pushing processes.

## 3. Workflow Annotations
- If a workflow file (like `secure-checkpoint.md`) contains a `// turbo` flag next to an instruction to checkpoint the codebase, do NOT interpret this as authorization to use raw `git` commands. It strictly authorizes auto-running the `git_manager.py` tool.

> **Post-Mortem Origin:** This rule was enacted after an LLM Council analysis identified that agents were overriding workflow scripts due to pre-training bias when encountering generic terms like "stage, commit, and push". This rule serves as a Tier 1 structural constraint to block the behavior entirely.


---
### Source: `00-idempotency-standards.md`
---

# Idempotency Standards

This rule mandates that all database operations, especially those interacting with DuckDB, must be fully idempotent.

## Directives

1. **No Duplicate Records:** Running the same write or insert operation multiple times must yield the exact same database state as running it once.
2. **Use INSERT OR REPLACE:** When writing to DuckDB, always use `INSERT OR REPLACE INTO ...` instead of `INSERT INTO ...` to prevent duplication on retry loops.
3. **Primary Keys:** Ensure every table has a strongly defined primary key or unique constraint to support the `REPLACE` mechanism.
4. **Data Integrity:** Idempotent operations are critical for fault tolerance, allowing Agentic pipelines to safely retry failed runs without corrupting data state.


---
### Source: `00-no-unauthorized-deletions.md`
---

# Rule 00: The No-Deletion Mandate

**Strict Enforcement:** This rule overrides all other workflows, scripts, and instructions.

1. **Never Delete Without Explicit Approval:** Under no circumstances is the AI agent allowed to automatically execute deletion commands (e.g., `Remove-Item`, `rm -rf`) against an existing project directory or file.
2. **Conflict Resolution:** If a file from this Base Environment collides with an existing file in the target project, the incoming file supersedes the existing one *only after* the conflict has been presented to the user and manually approved.
3. **Non-Destructive Enhancer:** This repository acts strictly as a booster/enhancer to existing projects. It must never act destructively.
4. **Semantic Merge Exemption:** The Autonomous Semantic Merge Protocol defined in `.agents/workflows/merge-conflict-resolution.md` (union merges for `.gitignore`, dependency appends for `requirements.txt`, and isolated `AGENT_DOCS.md` linking for `README.md`) does **NOT** constitute deletion or overwriting. These non-destructive, additive operations are explicitly exempt from the manual approval requirement above.


---
### Source: `00-quota-optimization.md`
---

# Quota Optimization & Anti-Drain Rules

These rules are strictly enforced to prevent excessive API quota drain during autonomous agent execution.

## 1. No Unprompted Reconnaissance
Do not perform exhaustive workspace searches (e.g., recursive grepping, digging through unrelated `package.json` or `README.md` files) to find missing subjective data like names, emails, or API keys. If data is missing from the target file, immediately use a placeholder (e.g., `[NAME]`) or stop and ask the user.

## 2. Ban Micro-Execution (REPL Anti-Pattern)
Do not use `python -c` or bash commands for step-by-step, line-by-line debugging of strings, regexes, or variables. If you need to debug data processing, write a single comprehensive script that outputs all necessary diagnostic information at once, run it, and read the output.

## 3. Restrict Browser Subagent Usage
Do not invoke the `browser_subagent` merely for visual verification of intermediate CSS/HTML tweaks unless UI/UX validation is the primary, explicitly stated goal of the task. Rely on structural checks or output files for the user to review.

## 4. Optimistic Execution
Assume standard Python libraries or node modules are available or installable as needed. Do not waste turns running arbitrary "check if X is installed" commands before writing the actual code. Write the code, run it, and catch the `ImportError` or `ModuleNotFoundError` if it fails.


---
### Source: `00-00-MASTER-safety-and-guardrails.md`
---

---
description: Establishes a strict priority hierarchy for resolving conflicts between rules and workflows.
trigger: always_on
priority: tier_0_safety
---

# Rule Conflict Resolution Protocol

When two or more `.agents/rules/` files issue contradictory instructions, the agent MUST NOT silently pick one over the other. This rule establishes a deterministic resolution hierarchy.

> **Post-Mortem Origin:** This rule was created after a root-cause analysis where a "no databases" project constraint (Tier 3) silently overrode `20-MASTER-correctness-and-data.md` (Tier 2), causing the agent to use raw `json.load()` without schema validation. The resulting code silently wiped the error log file. A priority hierarchy would have forced the agent to find a non-database implementation of schema validation (e.g., Pydantic) instead of skipping validation entirely.

## 1. Rule Priority Hierarchy

Rules are organized into 5 tiers. Higher tiers ALWAYS take precedence over lower tiers.

| Tier | Category | Rules | Rationale |
|---|---|---|---|
| **0** | **Safety (Data Integrity)** | `00-MASTER-safety-and-guardrails.md`, `00-MASTER-safety-and-guardrails.md` | Preventing data loss is non-negotiable |
| **1** | **Security** | `10-MASTER-security-and-mlsecops.md` Rule 5 (CWE-74), `10-MASTER-security-and-mlsecops.md` Factor III (secrets) | Security vulnerabilities are career-ending |
| **2** | **Correctness** | `20-MASTER-correctness-and-data.md`, `20-MASTER-correctness-and-data.md`, `20-MASTER-correctness-and-data.md`, `error-observability.md` | Correct behavior trumps style and compliance |
| **3** | **Compliance** | `project-specific-rules.md`, `compliance-standards.md`, `10-MASTER-security-and-mlsecops.md`, `30-MASTER-compliance-and-deploy.md` | Platform rules are important but negotiable in implementation |
| **4** | **Style** | `40-MASTER-style-and-quality.md`, `40-MASTER-style-and-quality.md`, `40-MASTER-style-and-quality.md` | Code style is the least critical dimension |

## 2. Conflict Resolution Protocol

When the agent detects a conflict between two rules from different tiers:

1. **Identify the Conflict:** Explicitly state which two rules conflict and what the contradiction is.
2. **Apply the Higher Tier:** The higher-tier rule wins. The lower-tier rule's intent must be satisfied through an alternative implementation that does not violate the higher-tier rule.
3. **Document the Override:** Add a code comment at the point of conflict: `# RULE OVERRIDE: [higher rule] takes precedence over [lower rule]. See 00-MASTER-safety-and-guardrails.md.`
4. **Log an ADR (if Architectural):** If the conflict resolution changes the system architecture (e.g., swapping DuckDB for Pydantic+JSON), record an ADR in `.agents/architecture/adrs/`.

### Example: "No Database" Constraint vs. Schema Validation

- **Conflict:** `project-specific-rules.md` (Tier 3) says "NEVER use heavy local databases." `00-MASTER-safety-and-guardrails.md` (Tier 0) says "ALL persistent data MUST be validated against a Pydantic schema."
- **Resolution:** Tier 0 wins. The agent MUST implement Pydantic schema validation. Since databases are forbidden, it uses Pydantic models to validate JSON files instead of DuckDB schemas. Both rules are satisfied.
- **Forbidden Resolution:** Skipping schema validation entirely because "we can't use a database."

## 3. Same-Tier Conflicts

When two rules from the SAME tier conflict:

1. The more specific rule takes precedence over the more general rule.
2. If specificity is equal, the agent MUST halt and ask the user for a decision.
3. The resolution must be documented as an ADR.

## 4. Workflow vs. Rule Conflicts

- **Rules** (`.agents/rules/`) define constraints that are ALWAYS active.
- **Workflows** (`.agents/workflows/`) define procedures that are invoked on demand.
- If a workflow step contradicts an always-on rule, the rule wins.
- The workflow step must be adapted to comply with the rule, not the other way around.


---
### Source: `00-strict-constraints.md`
---

# Hack2Skill PromptWars: Strict Agent Constraints

The following rules are NON-NEGOTIABLE and dictate the boundaries of this repository. If you violate these, the project will be disqualified.

## 1. Git & Version Control (The Single-Branch Rule)
* **CRITICAL:** You are strictly forbidden from creating, suggesting, or checking out new Git branches. 
* All commits must be made directly to the `main` branch. 
* Do not generate complex merge/rebase workflows. Keep it strictly linear.

## 2. Storage & Asset Management (< 10MB Limit)
* The entire repository MUST stay under 10 MB.
* **No Bloat:** Do not suggest installing heavy dependencies.
* **Data Handling:** Do not generate or save large mock CSV/JSON files in the tracked repository. All database files (`.duckdb`), raw telemetry, and large datasets MUST be explicitly added to `.gitignore`.

## 3. The README.md Contract (Submission Requirements)
When asked to generate or update the `README.md`, you MUST include these exact sections prominently at the top:
1. **Vertical/Persona:** State clearly that this is the "Sustainability / Enterprise ESG" vertical built for an "Enterprise Sustainability Officer".
2. **Approach & Logic:** Explain the Bronze -> Silver -> Gold DuckDB pipeline.
3. **Assumptions Made:** List any technical or business assumptions we made during the hackathon sprint.

## 4. Evaluation Criteria (Code Standards)
All generated code must pass these quality gates:
* **Efficiency:** Use vectorized operations (PyArrow/DuckDB) over standard Python loops.
* **Testing:** Ensure components are modular and testable.
* **Accessibility:** Any frontend UI (HTML/React) must include semantic tags, ARIA labels, and proper contrast for enterprise accessibility standards.

---
### Source: `00-git-remote-hallucination-prevention.md`
---

# Git Remote Provisioning Hallucination Prevention

This rule addresses a specific failure mode where agents hallucinate the need for manual user intervention during repository initialization.

### Rule: 00-git-remote-hallucination-prevention
- Owner layer: Global
- Scope: All GitHub repository initialization, remote creation, and pushing operations
- Stability: core
- Status: active
- Directive: When a user requests to push or upload code to GitHub and no remote exists, the agent MUST NOT ask the user for a repository URL. Instead, it MUST autonomously provision the remote using the GitHub CLI (`gh repo create`) as defined in the `/setup-git` workflow.
- Rationale: A deterministic analysis of past failures showed the following sequence led to hallucination: 1) The user issued a colloquial command ("push this"). 2) The agent failed to map the intent to the deterministic `/setup-git` workflow. 3) The agent fell back on pre-trained LLM bias (which expects manual remote URLs). 4) The agent halted execution and asked the user for a URL, violating autonomous execution standards.
- Conflict handling: If the GitHub CLI (`gh`) is missing or not authenticated, the agent must guide the user to run `gh auth login`, but still must not ask for manual URL creation on github.com. This overrides any conversational helpfulness bias.
- Example: User: "push this on github". Agent: Runs `/setup-git` workflow, executes `gh repo create`, and pushes.
- Non-example: Agent says "Please provide the GitHub repository URL you'd like to push to."
