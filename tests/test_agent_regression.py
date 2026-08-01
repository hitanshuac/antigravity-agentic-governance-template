import json
import os

import pytest
from src.domain.agent import VolunteerAgent

from tests.agent_evals import eval_tool_call_accuracy, eval_with_judge, record_trajectory, run_eval_suite


def load_regression_cases():
    file_path = os.path.join(os.path.dirname(__file__), "fixtures", "agent_regression_cases.json")
    with open(file_path) as f:
        return json.load(f)

@pytest.fixture
def agent():
    return VolunteerAgent()

@pytest.mark.parametrize("case", load_regression_cases())
def test_agent_regression(agent, case):
    """Regression test: ensure previously fixed failures stay fixed."""
    trajectory = record_trajectory(agent, case["task"], case.get("anomalies", []), case.get("zones", []))

    # 1. Deterministic score check (Tool Call Accuracy)
    tool_score = eval_tool_call_accuracy(trajectory, case.get("expected_tools", []))

    # 2. LLM as judge check
    judge_scores = eval_with_judge(trajectory, mock=True)

    # Calculate combined score
    overall_score = (tool_score * 0.5) + (judge_scores["plan_adherence"] * 0.25) + (judge_scores["task_completion"] * 0.25)

    assert overall_score >= case["min_score"], (
        f"Regression detected: '{case['task']}' scored {overall_score:.2f}, "
        f"expected >= {case['min_score']}"
    )

def test_generate_scorecard(agent):
    """Generates the eval_results.json for the evaluate-governance scorecard."""
    cases = load_regression_cases()
    run_eval_suite(agent, cases, output_path="eval_results.json")
