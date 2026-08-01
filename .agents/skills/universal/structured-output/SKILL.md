---
name: structured-output
description: "Enforces Pydantic-based structured outputs for all LLM calls. Prevents JSON parse failures, hallucinated schema fields, and freeform text extraction anti-patterns. TRIGGERS: 'structured output', 'JSON output from LLM', 'parse LLM response', 'Pydantic model for LLM', 'function calling', 'tool calling schema', 'extract structured data from text'."
---

# Structured Output Skill

The #1 production failure in LLM applications is parse errors on freeform
text output. The agent said it would return JSON but returned markdown.
The JSON was valid but had unexpected keys. The values were strings instead
of integers. This skill eliminates these failures by mandating schema-first
output design.

---

## Core Rules

### 1. Schema Before Call
Before any LLM call that expects structured data, the agent MUST define a
Pydantic model representing the expected output shape:

```python
from pydantic import BaseModel, Field
from enum import Enum

class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class SentimentResult(BaseModel):
    """The LLM's sentiment analysis output."""
    label: SentimentLabel = Field(description="The sentiment classification")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score 0-1")
    reasoning: str = Field(max_length=500, description="Brief explanation")
```

### 2. Use Provider-Native Structured Output
Always prefer the provider's built-in structured output mechanism over
manual JSON parsing:

| Provider | Method |
|:---|:---|
| OpenAI | `response_format={"type": "json_schema", "json_schema": {...}}` |
| Anthropic | Tool-use with single tool matching the schema |
| Google (Gemini) | `response_mime_type="application/json"` + `response_schema` |
| LangChain | `.with_structured_output(MyPydanticModel)` |

### 3. Never Parse Freeform Text
The agent MUST NOT use regex, string splitting, or `json.loads()` on raw
LLM text output to extract structured data. If the provider does not support
native structured output, use a two-step approach:

```python
# Step 1: Ask the LLM to generate
raw_response = llm.invoke(prompt)

# Step 2: Use a SECOND call with structured output to parse
class ExtractedData(BaseModel):
    key_findings: list[str]
    recommendation: str

parsed = llm.with_structured_output(ExtractedData).invoke(
    f"Extract the following structured data from this text:\n{raw_response}"
)
```

### 4. Validation Layer
After receiving structured output, always validate before using:

```python
try:
    result = SentimentResult.model_validate(llm_response)
except ValidationError as e:
    # Log the validation failure for the error pattern library
    logger.error(f"LLM output validation failed: {e}")
    # Retry with explicit schema reminder in prompt
    result = retry_with_schema_hint(prompt, SentimentResult)
```

---

## Common Schema Patterns

### List Extraction
```python
class ExtractedItems(BaseModel):
    items: list[str] = Field(min_length=1, description="Extracted items")
    total_count: int = Field(ge=0)
```

### Classification with Confidence
```python
class Classification(BaseModel):
    category: str = Field(description="The assigned category")
    confidence: float = Field(ge=0.0, le=1.0)
    alternatives: list[str] = Field(default_factory=list, max_length=3)
```

### Multi-Step Reasoning
```python
class ReasoningStep(BaseModel):
    step_number: int
    thought: str = Field(max_length=200)
    action: str
    result: str

class ReasoningChain(BaseModel):
    steps: list[ReasoningStep]
    final_answer: str
    confidence: float = Field(ge=0.0, le=1.0)
```

---

## Anti-Patterns

- **The `json.loads(response.text)` gamble:** Raw LLM text is not guaranteed
  JSON. Even if the prompt says "respond in JSON," models regularly include
  markdown fences, explanatory text, or trailing commas.
- **Schema-less tool calls:** Defining a tool without a Pydantic schema and
  then hoping the LLM provides the right argument types.
- **Over-constrained schemas:** Using `Literal["exact_value"]` for fields that
  the LLM might reasonably phrase differently. Use `Enum` with a small set of
  valid values instead.
