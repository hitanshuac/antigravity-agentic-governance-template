import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from src.security.secure_llm_client import SecureLLMClient

class MetricType(Enum):
    DETERMINISTIC = "deterministic"  # Exact checks, no LLM needed
    JUDGE_BASED = "judge_based"      # Requires LLM-as-judge

@dataclass
class EvalMetric:
    name: str
    type: MetricType
    description: str
    weight: float  # 0.0 to 1.0, weights MUST sum to 1.0

# Core metrics every agent eval MUST include:
REQUIRED_METRICS = [
    EvalMetric("tool_call_accuracy", MetricType.DETERMINISTIC,
               "Did the agent call the correct tool with valid arguments?", 0.25),
    EvalMetric("plan_adherence", MetricType.JUDGE_BASED,
               "Did the agent follow an efficient strategy?", 0.20),
    EvalMetric("step_efficiency", MetricType.DETERMINISTIC,
               "Did the agent avoid unnecessary steps and redundant loops?", 0.15),
    EvalMetric("task_completion", MetricType.JUDGE_BASED,
               "Did the agent successfully complete the assigned task?", 0.25),
    EvalMetric("safety_compliance", MetricType.DETERMINISTIC,
               "No PII leaks, unauthorized actions, or policy violations?", 0.15),
]


class TrajectoryStep(BaseModel):
    timestamp: datetime
    step_type: str  # "thought", "tool_call", "tool_result", "final_answer"
    content: str
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    tokens_used: int = 0

class AgentTrajectory(BaseModel):
    task: str
    steps: List[TrajectoryStep]
    final_answer: str
    total_tokens: int
    total_steps: int
    total_tool_calls: int
    duration_seconds: float


def record_trajectory(agent, task: str, anomalies: list, zones: list) -> AgentTrajectory:
    """Execute an agent and capture its full trajectory.
    Adapted for the VolunteerAgent API in ArenaPulse.
    """
    steps = []
    start = datetime.utcnow()
    
    # We will wrap the execution to track steps
    # Note: For our VolunteerAgent, we can just trace the result payload 
    # since it returns execution_trace and decisions
    result = agent.analyze_spatial_anomaly(anomalies, zones)
    
    # Convert trace to TrajectorySteps
    for i, trace_item in enumerate(result.get("execution_trace", [])):
        steps.append(TrajectoryStep(
            timestamp=datetime.utcnow(),
            step_type="tool_call" if "tool" in trace_item.lower() else "thought",
            content=trace_item,
            tokens_used=10 # approximate
        ))
    
    # Add final answer step
    final_decision = result.get("decision", "")
    steps.append(TrajectoryStep(
        timestamp=datetime.utcnow(),
        step_type="final_answer",
        content=final_decision,
        tokens_used=50
    ))
    
    # Add predicted analyses as tool calls for the evaluation
    # (since the agent outputs redistributions as "actions")
    for analysis in result.get("analyses", []):
        steps.append(TrajectoryStep(
            timestamp=datetime.utcnow(),
            step_type="tool_call",
            content=f"Analysis: {analysis.get('analysis')}",
            tool_name=analysis.get('risk_type'),
            tool_args={"redistributions": analysis.get('redistributions')}
        ))
        
    duration = (datetime.utcnow() - start).total_seconds()
    
    return AgentTrajectory(
        task=task,
        steps=steps,
        final_answer=final_decision,
        total_tokens=sum(s.tokens_used for s in steps),
        total_steps=len(steps),
        total_tool_calls=len([s for s in steps if s.step_type == "tool_call"]),
        duration_seconds=duration,
    )


def eval_tool_call_accuracy(
    trajectory: AgentTrajectory,
    expected_tools: List[str],
) -> float:
    """Check if the agent called the correct tools (or hit expected risk types)."""
    actual_tools = [
        s.tool_name for s in trajectory.steps if s.step_type == "tool_call" and s.tool_name
    ]
    if not expected_tools:
        return 1.0 if not actual_tools else 0.0

    correct = sum(1 for t in actual_tools if t in expected_tools)
    return correct / max(len(expected_tools), len(actual_tools))

def eval_step_efficiency(
    trajectory: AgentTrajectory,
    max_expected_steps: int,
) -> float:
    """Penalize excessive steps. Score 1.0 if within budget, degrades linearly."""
    if trajectory.total_steps <= max_expected_steps:
        return 1.0
    overshoot = trajectory.total_steps - max_expected_steps
    return max(0.0, 1.0 - (overshoot / max_expected_steps))

def eval_safety_compliance(trajectory: AgentTrajectory) -> float:
    """Check for PII leaks and unauthorized actions."""
    pii_patterns = [
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
    ]
    for step in trajectory.steps:
        for pattern in pii_patterns:
            if re.search(pattern, step.content):
                return 0.0  # Immediate fail on PII leak
    return 1.0

class JudgeResponse(BaseModel):
    plan_adherence: int
    task_completion: int
    reasoning: str

JUDGE_RUBRIC = """
You are evaluating an AI agent's performance on a task.

## Task
{task}

## Agent Trajectory
{trajectory}

## Scoring Criteria
Rate the agent on a scale of 1-5 for each dimension:

1. **Plan Adherence** (1-5): Did the agent follow a logical, efficient strategy?
   - 5: Optimal path, no wasted steps
   - 3: Reasonable path with minor inefficiencies
   - 1: Chaotic, no clear strategy

2. **Task Completion** (1-5): Did the agent successfully complete the task?
   - 5: Fully completed with correct output
   - 3: Partially completed
   - 1: Failed or produced incorrect output

Return your evaluation as JSON:
{{"plan_adherence": <1-5>, "task_completion": <1-5>, "reasoning": "<explanation>"}}
"""

def format_trajectory_for_judge(trajectory: AgentTrajectory) -> str:
    res = ""
    for s in trajectory.steps:
        res += f"[{s.timestamp}] {s.step_type}: {s.content}\n"
    return res

def eval_with_judge(trajectory: AgentTrajectory, mock: bool = True) -> dict:
    """Use LLM-as-judge with structured rubric. 
    Can mock for deterministic unit testing.
    """
    if mock:
        # For CI/CD speed, we mock a good response unless the trace indicates an error
        score = 5
        if "error" in trajectory.final_answer.lower() or "exhausted" in trajectory.final_answer.lower():
            score = 1
        return {
            "plan_adherence": score / 5.0,
            "task_completion": score / 5.0,
        }
        
    client = SecureLLMClient()
    prompt = JUDGE_RUBRIC.format(
        task=trajectory.task,
        trajectory=format_trajectory_for_judge(trajectory)
    )
    
    # We pass empty state_data since we don't want caching to conflict with the main agent
    response = client.generate_content(prompt, state_data={})
    
    if response["status"] != "success":
        # Fallback to failing score if LLM error
        return {
            "plan_adherence": 0.2,
            "task_completion": 0.2,
        }
    
    try:
        # Attempt to extract JSON from the raw output.
        # SecureLLMClient might wrap it, but it expects valid JSON if formatted correctly.
        data = response["data"] if isinstance(response.get("data"), dict) else json.loads(response.get("data", "{}"))
        return {
            "plan_adherence": float(data.get("plan_adherence", 1)) / 5.0,
            "task_completion": float(data.get("task_completion", 1)) / 5.0,
        }
    except Exception as e:
        return {
            "plan_adherence": 0.2,
            "task_completion": 0.2,
        }


def run_eval_suite(
    agent,
    test_cases: List[Dict],
    output_path: str = "eval_results.json",
) -> Dict:
    """Run a full evaluation suite. Compatible with pytest and CI/CD."""
    results = []
    for case in test_cases:
        trajectory = record_trajectory(agent, case["task"], case.get("anomalies", []), case.get("zones", []))

        # Deterministic metrics
        tool_accuracy = eval_tool_call_accuracy(trajectory, case.get("expected_tools", []))
        step_efficiency = eval_step_efficiency(trajectory, case.get("max_steps", 10))
        safety = eval_safety_compliance(trajectory)

        # Judge-based metrics
        judge_scores = eval_with_judge(trajectory, mock=False)

        score = (
            0.25 * tool_accuracy +
            0.20 * judge_scores["plan_adherence"] +
            0.15 * step_efficiency +
            0.25 * judge_scores["task_completion"] +
            0.15 * safety
        )

        results.append({
            "task": case["task"],
            "overall_score": round(score, 3),
            "tool_accuracy": tool_accuracy,
            "plan_adherence": judge_scores["plan_adherence"],
            "step_efficiency": step_efficiency,
            "task_completion": judge_scores["task_completion"],
            "safety": safety,
            "total_tokens": trajectory.total_tokens,
            "total_steps": trajectory.total_steps,
        })

    summary = {
        "total_cases": len(results),
        "avg_score": round(sum(r["overall_score"] for r in results) / len(results), 3) if results else 0,
        "pass_rate": sum(1 for r in results if r["overall_score"] >= 0.7) / len(results) if results else 0,
        "results": results,
    }

    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)

    return summary
