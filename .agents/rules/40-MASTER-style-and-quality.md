# 40-MASTER-style-and-quality



---
### Source: `40-40-MASTER-style-and-quality.md`
---

# Enterprise Code Quality Standards

This document codifies the strict requirements for achieving a perfect maintainability and reliability score against automated SAST and AI Code Analyzers (e.g., SonarQube, DeepSource). These rules must be strictly adhered to during all code generation and refactoring.

> **Language Scope**: The examples below use Python tooling as a reference implementation. When the host project uses a different language, apply the equivalent idiomatic standards (e.g., ESLint for JS/TS, golangci-lint for Go, Clippy for Rust).

## 1. Project Structure & Imports (Pylint/Flake8 Compliance)
- **Rule**: Never use `sys.path.append()` hacks.
- **Why**: Analyzers heavily penalize runtime `sys.path` manipulation, flagging them as `E0401` (Unable to import) and `C0413` (Wrong import position).
- **Action**:
  - Ensure every package directory (`src/`, subdirectories, `tests/`) has an `__init__.py` file.
  - Rely on `pyproject.toml` or `conftest.py` for path resolution.
  - All imports must be at the top of the file, ordered: stdlib -> third-party -> local (isort standard).

## 2. Formatting & Cleanliness
- **Rule**: Code must be meticulously formatted with zero PEP-8 hygiene violations.
- **Why**: Evaluators deduct points proportionally for trailing whitespace (W291) and structural issues.
- **Action**:
  - **Zero trailing whitespace** in any file.
  - Exactly **2 blank lines** between top-level function/class definitions.
  - Maximum line length of **120 characters**.
  - No blank line at the end of the file (W391), just a single newline.

## 3. Strict Linting Requirements
- **Rule**: Eliminate all code smells and anti-patterns.
- **Why**: Analyzers look for common Python pitfalls.
- **Action**:
  - **No broad exceptions**: Replace `except Exception as e:` with specific exceptions like `except (ValueError, ConnectionError):`.
  - **No inline imports**: Never `import` inside a function.
  - **No mutable defaults**: Change `def func(arg: dict = None):` to `def func(arg: Optional[dict] = None):`.
  - **No pointless re-raises**: Avoid using `raise e` inside an except block without adding context.
  - **Zero Hacks**: NEVER use `# pylint: disable` or `# noqa` suppression comments. You must natively fix the underlying AST violation to pass structural AI evaluators.

## 3.5 Structured Error Handling (12-Factor XI: Logs)
- **Rule**: Exception handlers must NEVER swallow errors with generic static messages.
- **Why**: Generic fallback strings (e.g., "Something went wrong", "I'm having trouble connecting") violate 12-Factor Factor XI (Logs as Event Streams), make debugging impossible, and waste significant developer time. See `00-MASTER-safety-and-guardrails.md` Rule 2 for the full mandate.
- **Action**:
  - Every `except` block must log `type(e).__name__` and `str(e)` to the observability layer (`error-observability.md`) BEFORE returning any user-facing message.
  - The user-facing message MAY be friendly and generic, but the log entry MUST contain the real exception class, message, and component.
  - Replace bare `except:` and `except Exception:` with specific exception types. If a catch-all is truly needed, it must be the LAST handler and must log at ERROR level with full context.
  - Reference: `00-MASTER-safety-and-guardrails.md` Rule 2, `00-MASTER-safety-and-guardrails.md` Tier 0.

## 4. Cyclomatic Complexity (Radon CC = A-Grade)
- **Rule**: All functions must score an 'A' grade (CC ≤ 5).
- **Why**: High complexity scores (B-grade and above) deduct from the maintainability index.
- **Action**:
  - If a function exceeds CC=5, extract branching logic into private helper functions.
  - **Pre-compile regex patterns** (`re.compile`) at the module level rather than inside functions.
  - Extract magic numbers and strings into uppercase module constants.
  - Keep functions under 25 lines of core logic.

## 5. Documentation & Typing
- **Rule**: Every function and module must be typed and documented.
- **Why**: Missing docstrings and types trigger Pylint/Mypy penalties.
- **Action**:
  - Include a module-level docstring at the top of every `.py` file.
  - Use **Google-style docstrings** with explicit `Args:`, `Returns:`, and `Raises:` sections.
  - Add explicit type hints on every parameter and return value.
  - Void functions must explicitly declare `-> None`.

## 6. Pre-Push Verification Commands
Before concluding any major codebase update, run the verification suite appropriate for the host language. Python example:
```bash
pylint src/ --fail-under=9.5
flake8 src/ tests/ --max-line-length=120 --count
radon cc src/ -a -s -n B   # Output must be empty
radon mi src/ -s           # All must be 'A'
pytest tests/ -v           # All must pass
```
For other languages, use the equivalent toolchain (e.g., `eslint . && jest`, `golangci-lint run && go test ./...`).


---
### Source: `41-40-MASTER-style-and-quality.md`
---

# Rule: Linting & Formatting Standards

**Trigger:** Pre-commit and CI/CD pipelines.

## Objective
Enforce exponential-speed static analysis and formatting using **Ruff**. This replaces legacy tooling (`flake8`, `black`, `isort`, `bandit` syntax checks).

## Configuration
- Target Python Version: 3.11+
- Line Length: 120 (to accommodate Agentic payload signatures)
- Rules Enforced:
  - `E`, `F` (Pyflakes, pycodestyle)
  - `I` (isort)
  - `UP` (pyupgrade)
  - `RUF` (Ruff-specific rules)

## Agent Guidelines
1. **Never Bypass:** Do not use `# noqa` unless absolutely necessary (e.g., complex DuckDB macro imports). If used, you must document the reason.
2. **Auto-fixing:** The CI/CD pipeline does not auto-fix. All code must pass `ruff check .` and `ruff format --check .` locally before pushing.


---
### Source: `42-40-MASTER-style-and-quality.md`
---

# Context Compaction: v2.4.0 Specification

This rule enforces strict token conservation on all conversation payloads transiting the Agentic Application cascade. It eliminates wasteful verbosity, caps history depth, and mandates telemetry persistence.

## 1. Processing Pipeline (Mandatory Order)
All operations execute on a **deep copy** of the inbound messages array. The caller's data must never be mutated.

The 5-step sequence within `src/capabilities/compaction.py` is:
1. **Deep Copy** — `copy.deepcopy(messages)` at function entry.
2. **Grounding** — System prompt injected at index 0 (`ground_messages()`). See `20-MASTER-correctness-and-data.md` §1.
3. **Prefix Stripping** — Verbose AI filler removed from `role: assistant` messages (`strip_boilerplate()`).
4. **Sliding Window** — Oldest messages beyond the cap are evicted (`apply_sliding_window()`).
5. **Cascade** — Compacted payload forwarded to `query_cloud()`. Admission Control (PRE-FLIGHT BYPASS) runs inside `llm_cloud.py`.

## 2. Prefix Stripping Rules
- Strip verbose AI conversational filler from `role: assistant` messages **only**.
- The following prefix patterns must be removed if they appear at the start of an assistant message:
  - `"Sure! "`, `"Sure, "`, `"Of course! "`, `"Of course, "`
  - `"Great question! "`, `"That's a great question! "`
  - `"Absolutely! "`, `"Certainly! "`
  - `"I'd be happy to help! "`, `"I'd be happy to help you with that! "`
  - `"Let me help you with that. "`
- Stripping is **prefix-only** and **case-sensitive**. The substantive content after the filler must be preserved verbatim.
- If stripping a prefix would result in an empty string, the original message must be kept intact.
- Multiple matching prefixes on the same message: strip only the **first** (longest) match.

## 3. Sliding Window Limit
- Hard cap: **10 messages** in any outbound payload (including the `role: system` message).
- The `role: system` message at index 0 is **pinned** and never evicted.
- When the payload exceeds 10 messages, retain only the system message + the **most recent 9** conversation messages. All older messages are dropped.

## 4. System Message Immunity
- The `role: system` message injected by `20-MASTER-correctness-and-data.md` is **exempt** from both sliding window eviction and boilerplate stripping.
- It must always occupy index 0 of the outbound payload.

## 5. Observability
- Every compaction event must emit an `INFO`-level log line containing `[CONTEXT COMPACTION]`.
- The log must include:
  - The **before** and **after** message counts (e.g., `"Compacted 24 → 10 messages"`).
  - The number of boilerplate prefixes stripped (e.g., `"Stripped 3 filler prefixes"`).
- If no compaction was necessary (payload already within limits and no boilerplate found), no log line is emitted.

## 6. Telemetry Persistence
- Every request must record compaction metrics to `data/pipeline_metrics.db` (DuckDB).
- Required fields: `raw_tokens`, `compact_tokens`, `tokens_saved`, `savings_pct`, `messages_dropped`, `prefixes_stripped`, `latency_sec`, `tier`.
- The DuckDB connection must follow the DuckDB Optimizer skill directives: WAL mode enabled, memory capped at 256MB.
- Telemetry writes must be non-blocking to the request path — a failed write must not crash the cascade.

---
### Source: `43-40-MASTER-style-and-quality.md`
---

# Anti-Over-Engineering Protocol (Ponytail Ladder)

This rule strictly enforces a minimalist, anti-bloat philosophy to counteract the tendency of LLMs to generate excessive boilerplate, unnecessary wrappers, or complex architectures for simple problems.

## The 7-Step Decision Ladder
Before writing any code to solve a task, the agent MUST evaluate the solution through this exact ladder in order. If a step satisfies the requirement, stop there and DO NOT proceed to the next step.

1. **YAGNI (You Aren't Gonna Need It)**: Does this feature or abstraction need to exist at all? If the user's core problem can be solved without it, skip it entirely.
2. **Context (Codebase Reuse)**: Is there already a helper function, utility class, or architectural pattern in the existing codebase that solves this? If yes, reuse it.
3. **Stdlib (Standard Library)**: Does the language's standard library natively support this? If yes, use the standard library instead of downloading a package.
4. **Native (Platform Features)**: Is there a native platform feature (e.g., standard HTML `<input type="date">` instead of a custom React datepicker component)? If yes, use the native feature.
5. **Dependencies**: Does an already-installed dependency solve this? Check the `package.json` or `requirements.txt`. Do not install a new dependency if an existing one can do the job.
6. **One-Liner**: Can the solution be expressed in a single line of clear, idiomatic code? If yes, write the one-liner instead of a full class or helper function.
7. **Minimum Viable Code**: Only if steps 1-6 fail, write the absolute minimum amount of code required to solve the task. No preemptive abstractions, no future-proofing wrappers, no speculative error handling for impossible states.

## Zero Boilerplate Enforcement
- **Rule**: If you generate a wrapper class around a standard library function that adds zero value, you have failed.
- **Action**: Strive for a codebase with negative lines of code. The best code is the code you never wrote.
