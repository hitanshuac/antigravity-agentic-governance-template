---
name: error-pattern-library
description: "A living reference library of common failure patterns with proven fixes. Reduces debugging time by matching errors against known solutions before starting from scratch. TRIGGERS: 'I keep seeing this error', 'common error', 'known issue', 'error pattern', 'why does this keep happening', 'debug this recurring error'. Also auto-referenced by the loop-detector skill during diagnosis."
---

# Error Pattern Library

Instead of debugging every error from first principles, match it against
known patterns first. This library captures recurring failure patterns
encountered in agentic coding workflows, organized by category with
symptoms, root causes, and proven fixes.

---

## How to Use This Library

### During Debugging
1. Read the error message
2. Match against the patterns below by category
3. If a match is found, apply the proven fix
4. If no match, debug from first principles and ADD the resolution as a new pattern

### Adding New Patterns
When a novel error is resolved, add it to this library using this template:
```markdown
### [Pattern Name]
- **Symptoms:** [exact error message or behavioral description]
- **Root Cause:** [why this actually happens]
- **Fix:** [step-by-step resolution]
- **Prevention:** [how to avoid this in the future]
```

---

## Category: Dependency & Import Errors

### ModuleNotFoundError in Virtual Environment
- **Symptoms:** `ModuleNotFoundError: No module named 'X'` even after `pip install X`
- **Root Cause:** Package was installed in global Python, not the active venv
- **Fix:** `which python` to verify active interpreter, then `pip install X` in the correct venv
- **Prevention:** Always activate venv before installing: `source .venv/bin/activate` (Unix) or `.venv\Scripts\activate` (Windows)

### Version Conflict Between Dependencies
- **Symptoms:** `ERROR: pip's dependency resolver does not currently consider all packages...`
- **Root Cause:** Two packages require incompatible versions of a shared dependency
- **Fix:** Pin the conflicting dependency to the version that satisfies both, or use `pip install --upgrade` with explicit version constraints
- **Prevention:** Use `pip-compile` (pip-tools) to resolve dependency graphs before installing

---

## Category: LLM API Errors

### Rate Limit Exceeded
- **Symptoms:** `429 Too Many Requests` or `RateLimitError`
- **Root Cause:** Too many API calls within the provider's rate window
- **Fix:** Implement exponential backoff with jitter: `time.sleep(2**attempt + random.uniform(0, 1))`
- **Prevention:** Add rate limiting to the SecureLLMClient wrapper per @.agents/rules/20-phase-execute.md

### Context Length Exceeded
- **Symptoms:** `InvalidRequestError: This model's maximum context length is X tokens`
- **Root Cause:** Input prompt + expected output exceeds model limits
- **Fix:** Truncate input using @.agents/skills/universal/context-compactor/SKILL.md sliding window
- **Prevention:** Pre-calculate token count before sending; use `tiktoken` for OpenAI, model-specific tokenizers for others

### Structured Output Parse Failure
- **Symptoms:** `json.decoder.JSONDecodeError` when parsing LLM response
- **Root Cause:** LLM returned freeform text instead of JSON despite prompt instructions
- **Fix:** Use provider-native structured output per @.agents/skills/universal/structured-output/SKILL.md
- **Prevention:** Never use `json.loads()` on raw LLM text; always use `.with_structured_output()`

---

## Category: Deployment Errors

### Docker Build Fails on pip install
- **Symptoms:** `ERROR: Could not find a version that satisfies the requirement`
- **Root Cause:** Package not available for the Docker image's Python version or architecture
- **Fix:** Check Python version in Dockerfile matches local dev (`python --version`). Use `--platform linux/amd64` if building on ARM Mac
- **Prevention:** Always specify Python version in Dockerfile: `FROM python:3.11-slim`

### HF Spaces Health Check Timeout
- **Symptoms:** Space shows "Building" indefinitely or "Runtime error"
- **Root Cause:** App not binding to `0.0.0.0:7860` (Gradio) or `0.0.0.0:8501` (Streamlit)
- **Fix:** Ensure `server_name="0.0.0.0"` in Gradio launch, or `--server.address=0.0.0.0` for Streamlit
- **Prevention:** Always test locally with the exact same port binding before deploying

### Port Already in Use
- **Symptoms:** `OSError: [Errno 98] Address already in use`
- **Root Cause:** Previous process still bound to the port
- **Fix:** `lsof -i :PORT` then `kill -9 PID` (Unix), or `netstat -ano | findstr :PORT` then `taskkill /PID PID /F` (Windows)
- **Prevention:** Add graceful shutdown handling; use `uvicorn --reload` with `--host 0.0.0.0`

---

## Category: Git & Version Control

### Commit Rejected Due to Large Files
- **Symptoms:** `remote: error: File X is Y MB; this exceeds GitHub's file size limit`
- **Root Cause:** Binary files, datasets, or dependency folders committed to git
- **Fix:** `git filter-branch` or `git-filter-repo` to remove the large file from history. Add to `.gitignore`
- **Prevention:** Always run `git status` before committing. Keep `.gitignore` updated for `.duckdb`, `node_modules/`, `.venv/`, `__pycache__/`

### Merge Conflict in Generated Files
- **Symptoms:** Merge conflicts in `requirements.txt`, `package-lock.json`, or `.lock` files
- **Root Cause:** Both branches modified dependency files
- **Fix:** Accept one side entirely, then re-run the dependency resolution tool (`pip-compile`, `npm install`)
- **Prevention:** Per @.agents/workflows/merge-conflict-resolution.md, resolve lock files by regenerating, not hand-editing

---

## Category: Testing Errors

### Test Passes Locally, Fails in CI
- **Symptoms:** `pytest` passes on dev machine but fails in GitHub Actions
- **Root Cause:** Environment differences (Python version, OS, env vars, timezone, file paths)
- **Fix:** Check CI logs for the exact error. Common causes: missing env vars, Windows vs Unix path separators, timezone-dependent assertions
- **Prevention:** Use `pytest-env` to set consistent env vars. Avoid `datetime.now()` in assertions; use `freezegun`

### Flaky Tests (Intermittent Failures)
- **Symptoms:** Test passes 9/10 times, fails randomly
- **Root Cause:** Race conditions, network-dependent tests, order-dependent test state
- **Fix:** Isolate the flaky test with `pytest -x --count=20 tests/test_flaky.py`. Check for shared mutable state
- **Prevention:** Use `pytest-randomly` to detect order dependence. Mock all network calls in unit tests

---

## Extending This Library

This library is a living document. The agent MUST add new patterns when:
1. The @.agents/skills/universal/loop-detector/SKILL.md resolves a novel error
2. The @.agents/workflows/error-observability.md captures a recurring failure
3. A hackathon reveals a new class of deployment or API error

Format new entries using the template above. Keep each pattern under 5 lines.
