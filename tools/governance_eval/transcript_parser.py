"""Transcript Parser — Reads JSONL transcripts into structured dataclasses.

Parses the Antigravity IDE conversation transcripts stored at:
  <brain_dir>/<conversation-id>/.system_generated/logs/transcript.jsonl

Each line is a JSON object representing one step in the conversation.
"""

import json
import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    """A single tool invocation extracted from a transcript step."""
    name: str
    args: dict[str, Any] = field(default_factory=dict)


@dataclass
class TranscriptStep:
    """A single step in a conversation transcript."""
    step_index: int
    source: str           # USER_EXPLICIT, MODEL, SYSTEM
    step_type: str        # USER_INPUT, PLANNER_RESPONSE, CODE_ACTION, RUN_COMMAND, etc.
    status: str           # DONE, ERROR
    created_at: str       # ISO timestamp
    content: str = ""
    thinking: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    is_truncated: bool = False


@dataclass
class ParsedConversation:
    """A fully parsed conversation with all steps."""
    conversation_id: str
    transcript_path: str
    steps: list[TranscriptStep] = field(default_factory=list)
    total_steps: int = 0


def _parse_tool_calls(raw_calls: list[dict] | None) -> list[ToolCall]:
    """Extract tool calls from raw JSON, handling nested string escaping."""
    if not raw_calls:
        return []
    result = []
    for call in raw_calls:
        name = call.get("name", "unknown")
        args = call.get("args", {})
        # Args values are sometimes double-quoted strings; strip outer quotes
        cleaned_args = {}
        for key, val in args.items():
            if isinstance(val, str):
                cleaned_args[key] = val.strip('"')
            else:
                cleaned_args[key] = val
        result.append(ToolCall(name=name, args=cleaned_args))
    return result


def parse_transcript_file(filepath: str) -> list[TranscriptStep]:
    """Parse a single transcript.jsonl file into a list of TranscriptSteps.

    Args:
        filepath: Absolute path to a transcript.jsonl file.

    Returns:
        List of TranscriptStep dataclasses, one per line.

    Raises:
        FileNotFoundError: If the transcript file does not exist.
        json.JSONDecodeError: If a line is not valid JSON (skipped with warning).
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Transcript file not found: {filepath}")

    steps: list[TranscriptStep] = []
    with open(filepath, encoding="utf-8") as fh:
        for line_num, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                # Skip malformed lines but log the position
                print(f"  [WARN] Skipping malformed JSON at line {line_num}")
                continue

            step = TranscriptStep(
                step_index=data.get("step_index", line_num - 1),
                source=data.get("source", "UNKNOWN"),
                step_type=data.get("type", "UNKNOWN"),
                status=data.get("status", "UNKNOWN"),
                created_at=data.get("created_at", ""),
                content=data.get("content", ""),
                thinking=data.get("thinking", ""),
                tool_calls=_parse_tool_calls(data.get("tool_calls")),
                is_truncated=data.get("is_truncated", False),
            )
            steps.append(step)

    return steps


def discover_conversations(brain_dir: str) -> list[ParsedConversation]:
    """Discover and parse all conversations in the brain directory.

    Args:
        brain_dir: Absolute path to the Antigravity brain directory.
                   e.g. C:\\Users\\zacca\\.gemini\\antigravity-ide\\brain

    Returns:
        List of ParsedConversation objects, sorted by first timestamp.
    """
    if not os.path.isdir(brain_dir):
        raise FileNotFoundError(f"Brain directory not found: {brain_dir}")

    conversations: list[ParsedConversation] = []

    for entry in os.scandir(brain_dir):
        if not entry.is_dir():
            continue

        transcript_path = os.path.join(
            entry.path, ".system_generated", "logs", "transcript.jsonl"
        )
        if not os.path.isfile(transcript_path):
            continue

        conversation_id = entry.name
        steps = parse_transcript_file(transcript_path)

        conversations.append(ParsedConversation(
            conversation_id=conversation_id,
            transcript_path=transcript_path,
            steps=steps,
            total_steps=len(steps),
        ))

    # Sort by the timestamp of the first step
    conversations.sort(
        key=lambda c: c.steps[0].created_at if c.steps else ""
    )
    return conversations


def get_user_messages(conversation: ParsedConversation) -> list[TranscriptStep]:
    """Extract only user input steps from a conversation."""
    return [s for s in conversation.steps if s.step_type == "USER_INPUT"]


def get_agent_responses(conversation: ParsedConversation) -> list[TranscriptStep]:
    """Extract only agent (model) planner responses from a conversation."""
    return [s for s in conversation.steps if s.step_type == "PLANNER_RESPONSE"]


def get_command_executions(conversation: ParsedConversation) -> list[TranscriptStep]:
    """Extract only command execution steps from a conversation."""
    return [s for s in conversation.steps if s.step_type == "RUN_COMMAND"]


def get_all_tool_calls(conversation: ParsedConversation) -> list[ToolCall]:
    """Flatten all tool calls across all steps in a conversation."""
    calls: list[ToolCall] = []
    for step in conversation.steps:
        calls.extend(step.tool_calls)
    return calls
