---
name: AI Security Guardrails
description: "Prompt injection defense, PII redaction, and output bounds enforcement for LLM-powered applications. Extends the SecureLLMClient pattern with runtime guardrails. TRIGGERS: 'ai security', 'prompt injection', 'PII redaction', 'guardrails', 'llm security', 'output validation', 'red teaming'."
---

# AI Security Guardrails

Runtime security guardrails for LLM-powered applications. Extends the
`SecureLLMClient` interceptor pattern (defined in `rules/20-phase-execute.md`)
with concrete defense implementations.

## 1. Prompt Injection Defense

### Input Sanitization (Pre-Flight)
All user inputs MUST pass through these filters before reaching the LLM:

```python
import re

def sanitize_prompt(user_input: str) -> str:
    """Strip injection delimiters and dangerous patterns."""
    # Remove system prompt override attempts
    patterns = [
        r'(?i)ignore\s+(all\s+)?previous\s+instructions',
        r'(?i)you\s+are\s+now\s+',
        r'(?i)system\s*:\s*',
        r'(?i)<\|.*?\|>',  # Special token injection
        r'(?i)\[INST\].*?\[/INST\]',  # Instruction delimiters
    ]
    for pattern in patterns:
        user_input = re.sub(pattern, '[REDACTED]', user_input)
    # Truncate to safe max length
    return user_input[:4096]
```

### Structural Defense
- MUST use delimiter-separated prompts: wrap user input in XML tags
  (`<user_input>...</user_input>`) so the LLM can distinguish system vs. user text.
- MUST NOT concatenate raw user text directly into the system prompt.

## 2. PII Redaction (Output Post-Flight)

### Detection Patterns
Before returning LLM output to the user or logging it:

```python
PII_PATTERNS = {
    'email': r'\b[\w.-]+@[\w.-]+\.\w{2,}\b',
    'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
    'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
    'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
    'api_key': r'\b(sk|pk|api|key|token)[-_][a-zA-Z0-9]{20,}\b',
}
```

### Redaction Rule
- MUST scan all LLM outputs for PII patterns before returning to caller.
- Matched patterns MUST be replaced with `[REDACTED-{type}]`.
- Redaction events MUST be logged to `data/error_logs.json` for audit.

## 3. Output Bounds Enforcement

### Length Bounds
- MUST enforce maximum output token limits per use case.
- MUST truncate gracefully with `[OUTPUT TRUNCATED]` marker.

### Content Bounds
- MUST NOT allow LLM to generate executable code in user-facing chat responses
  unless explicitly requested.
- MUST NOT allow LLM to reveal system prompt contents.

## 4. Integration with SecureLLMClient
All guardrails MUST be implemented inside the `SecureLLMClient` wrapper,
not in application code. This ensures they cannot be bypassed:

```python
class SecureLLMClient:
    def generate(self, prompt: str, user_input: str) -> str:
        sanitized = sanitize_prompt(user_input)        # Pre-flight
        raw_output = self._call_provider(prompt, sanitized)
        redacted = redact_pii(raw_output)              # Post-flight
        bounded = enforce_bounds(redacted)              # Bounds check
        return bounded
```
