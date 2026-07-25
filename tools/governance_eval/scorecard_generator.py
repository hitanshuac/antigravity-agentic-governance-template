"""Scorecard Generator — Produces markdown governance scorecards.

Takes computed GovernanceMetrics and generates human-readable reports
with tables, comparisons, and per-conversation breakdowns.
"""

from dataclasses import fields
from datetime import datetime
from typing import Dict, List, Optional

from tools.governance_eval.metric_extractors import GovernanceMetrics
from tools.governance_eval.rule_set_tagger import RuleSetFingerprint


def _format_duration(seconds: float) -> str:
    """Format seconds into a human-readable duration string."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    minutes = seconds / 60
    if minutes < 60:
        return f"{minutes:.1f}m"
    hours = minutes / 60
    return f"{hours:.1f}h"


def _score_emoji(score: float) -> str:
    """Map a 0-1 score to a visual emoji."""
    if score >= 0.9:
        return "🟢"
    if score >= 0.7:
        return "🟡"
    if score >= 0.5:
        return "🟠"
    return "🔴"


def _score_grade(score: float) -> str:
    """Map a 0-1 score to a letter grade."""
    if score >= 0.95:
        return "A+"
    if score >= 0.9:
        return "A"
    if score >= 0.85:
        return "A-"
    if score >= 0.8:
        return "B+"
    if score >= 0.75:
        return "B"
    if score >= 0.7:
        return "B-"
    if score >= 0.6:
        return "C"
    if score >= 0.5:
        return "D"
    return "F"


def generate_single_scorecard(metrics: GovernanceMetrics) -> str:
    """Generate a markdown scorecard for a single conversation."""
    lines = [
        f"### Conversation `{metrics.conversation_id[:12]}...`",
        "",
        f"| Metric | Value | Score | Grade |",
        f"|--------|-------|-------|-------|",
        f"| 🔄 Loop Count | {metrics.loop_count} retry cycles | "
        f"{metrics.loop_efficiency_score:.2f} | "
        f"{_score_emoji(metrics.loop_efficiency_score)} {_score_grade(metrics.loop_efficiency_score)} |",
        f"| ❌ Error Rate | {metrics.failed_commands}/{metrics.total_commands} commands failed | "
        f"{metrics.error_resilience_score:.2f} | "
        f"{_score_emoji(metrics.error_resilience_score)} {_score_grade(metrics.error_resilience_score)} |",
        f"| 🛡️ Safety Violations | {metrics.safety_violations} | "
        f"{metrics.safety_score:.2f} | "
        f"{_score_emoji(metrics.safety_score)} {_score_grade(metrics.safety_score)} |",
        f"| 🧠 Hallucination Flags | {metrics.hallucination_flags} | "
        f"{metrics.hallucination_score:.2f} | "
        f"{_score_emoji(metrics.hallucination_score)} {_score_grade(metrics.hallucination_score)} |",
        f"| 👤 Human Interventions | {metrics.human_interventions} corrections | "
        f"{metrics.autonomy_score:.2f} | "
        f"{_score_emoji(metrics.autonomy_score)} {_score_grade(metrics.autonomy_score)} |",
        f"| 💀 Dead Ends | {metrics.dead_end_count} abandoned approaches | — | — |",
        f"| ⏱️ Duration | {_format_duration(metrics.time_to_success_seconds)} | — | — |",
        f"| 🔧 Total Tool Calls | {metrics.total_tool_calls} | — | — |",
        f"| 📊 Agent Turns | {metrics.total_agent_turns} | — | — |",
        "",
        f"**Overall Governance Score: {_score_emoji(metrics.overall_governance_score)} "
        f"{metrics.overall_governance_score:.3f} "
        f"({_score_grade(metrics.overall_governance_score)})**",
        "",
    ]
    return "\n".join(lines)


def generate_aggregate_scorecard(
    all_metrics: List[GovernanceMetrics],
    rule_set: Optional[RuleSetFingerprint] = None,
) -> str:
    """Generate a full governance scorecard across all conversations.

    Args:
        all_metrics: List of GovernanceMetrics, one per conversation.
        rule_set: Optional fingerprint of the active rule set.

    Returns:
        Complete markdown scorecard as a string.
    """
    if not all_metrics:
        return "# Governance Scorecard\n\nNo conversations found to analyze.\n"

    # Aggregate statistics
    n = len(all_metrics)
    total_loops = sum(m.loop_count for m in all_metrics)
    total_errors = sum(m.failed_commands for m in all_metrics)
    total_commands = sum(m.total_commands for m in all_metrics)
    total_tool_calls = sum(m.total_tool_calls for m in all_metrics)
    total_hallucinations = sum(m.hallucination_flags for m in all_metrics)
    total_safety = sum(m.safety_violations for m in all_metrics)
    total_interventions = sum(m.human_interventions for m in all_metrics)
    total_dead_ends = sum(m.dead_end_count for m in all_metrics)
    total_time = sum(m.time_to_success_seconds for m in all_metrics)

    avg_overall = sum(m.overall_governance_score for m in all_metrics) / n
    avg_loop = sum(m.loop_efficiency_score for m in all_metrics) / n
    avg_error = sum(m.error_resilience_score for m in all_metrics) / n
    avg_safety = sum(m.safety_score for m in all_metrics) / n
    avg_halluc = sum(m.hallucination_score for m in all_metrics) / n
    avg_autonomy = sum(m.autonomy_score for m in all_metrics) / n

    lines = [
        "# 📋 Governance Evaluation Scorecard",
        "",
        f"*Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}*",
        "",
    ]

    if rule_set:
        lines.extend([
            f"**Rule Set:** `{rule_set.label}` "
            f"({rule_set.rule_count} rules, {rule_set.total_bytes} bytes)",
            f"**Fingerprint:** `{rule_set.fingerprint_hash}`",
            "",
        ])

    lines.extend([
        "## Summary",
        "",
        f"| Metric | Aggregate | Average per Conversation |",
        f"|--------|-----------|--------------------------|",
        f"| Conversations Analyzed | {n} | — |",
        f"| Total Tool Calls | {total_tool_calls} | {total_tool_calls / n:.1f} |",
        f"| Total Commands | {total_commands} | {total_commands / n:.1f} |",
        f"| Failed Commands | {total_errors} | {total_errors / n:.1f} |",
        f"| Retry Loops | {total_loops} | {total_loops / n:.1f} |",
        f"| Hallucination Flags | {total_hallucinations} | {total_hallucinations / n:.1f} |",
        f"| Safety Violations | {total_safety} | {total_safety / n:.1f} |",
        f"| Human Interventions | {total_interventions} | {total_interventions / n:.1f} |",
        f"| Dead Ends | {total_dead_ends} | {total_dead_ends / n:.1f} |",
        f"| Total Time | {_format_duration(total_time)} | {_format_duration(total_time / n)} |",
        "",
        "## Dimension Scores",
        "",
        f"| Dimension | Avg Score | Grade | Rule Category |",
        f"|-----------|-----------|-------|---------------|",
        f"| {_score_emoji(avg_loop)} Loop Efficiency | {avg_loop:.3f} | "
        f"{_score_grade(avg_loop)} | `00-00-core-safety` |",
        f"| {_score_emoji(avg_error)} Error Resilience | {avg_error:.3f} | "
        f"{_score_grade(avg_error)} | `00-02-core-safety` |",
        f"| {_score_emoji(avg_safety)} Safety Compliance | {avg_safety:.3f} | "
        f"{_score_grade(avg_safety)} | `00-01-core-safety` |",
        f"| {_score_emoji(avg_halluc)} Hallucination Guard | {avg_halluc:.3f} | "
        f"{_score_grade(avg_halluc)} | `00-00-core-safety` |",
        f"| {_score_emoji(avg_autonomy)} Autonomy | {avg_autonomy:.3f} | "
        f"{_score_grade(avg_autonomy)} | `20-00-phase-execute` |",
        "",
        f"### **Overall Governance Score: {_score_emoji(avg_overall)} "
        f"{avg_overall:.3f} ({_score_grade(avg_overall)})**",
        "",
        "---",
        "",
        "## Per-Conversation Breakdown",
        "",
    ])

    # Sort by overall score (worst first, so issues are visible)
    sorted_metrics = sorted(all_metrics, key=lambda m: m.overall_governance_score)
    for m in sorted_metrics:
        lines.append(generate_single_scorecard(m))
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def generate_comparison_scorecard(
    metrics_a: List[GovernanceMetrics],
    metrics_b: List[GovernanceMetrics],
    label_a: str = "Baseline (A)",
    label_b: str = "Treatment (B)",
    rule_diff: Optional[Dict] = None,
) -> str:
    """Generate a side-by-side comparison scorecard for A/B testing.

    Args:
        metrics_a: Metrics from conversations under rule set A.
        metrics_b: Metrics from conversations under rule set B.
        label_a: Human-readable label for rule set A.
        label_b: Human-readable label for rule set B.
        rule_diff: Optional output from compare_rule_sets().

    Returns:
        Markdown comparison scorecard.
    """
    def _avg(lst: List[GovernanceMetrics], attr: str) -> float:
        if not lst:
            return 0.0
        return sum(getattr(m, attr) for m in lst) / len(lst)

    def _sum(lst: List[GovernanceMetrics], attr: str) -> int:
        return sum(getattr(m, attr) for m in lst)

    def _delta_str(val_a: float, val_b: float, inverse: bool = False) -> str:
        """Format delta with arrow. For scores, positive delta = improvement."""
        delta = val_b - val_a
        if abs(delta) < 0.001:
            return "→ *no change*"
        if inverse:
            # For raw counts (errors, loops), negative delta = improvement
            arrow = "↓" if delta < 0 else "↑"
            color = "improvement" if delta < 0 else "regression"
        else:
            # For scores, positive delta = improvement
            arrow = "↑" if delta > 0 else "↓"
            color = "improvement" if delta > 0 else "regression"
        return f"{arrow} {abs(delta):.3f} ({color})"

    lines = [
        "# 📊 Governance A/B Comparison",
        "",
        f"*Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}*",
        "",
    ]

    if rule_diff:
        lines.extend([
            "## Rule Set Differences",
            "",
        ])
        if rule_diff["identical"]:
            lines.append("> [!WARNING]")
            lines.append("> The two rule sets are **identical**. "
                         "Any metric differences are due to task variance, not rules.")
        else:
            if rule_diff["added"]:
                lines.append(f"**Added:** {', '.join(f'`{f}`' for f in rule_diff['added'])}")
            if rule_diff["removed"]:
                lines.append(f"**Removed:** {', '.join(f'`{f}`' for f in rule_diff['removed'])}")
            if rule_diff["modified"]:
                lines.append(f"**Modified:** {', '.join(f'`{f}`' for f in rule_diff['modified'])}")
        lines.append("")

    na = len(metrics_a)
    nb = len(metrics_b)

    lines.extend([
        "## Side-by-Side Comparison",
        "",
        f"| Metric | {label_a} (n={na}) | {label_b} (n={nb}) | Delta |",
        f"|--------|{'-' * (len(label_a) + 8)}|{'-' * (len(label_b) + 8)}|-------|",
        f"| Avg Overall Score | {_avg(metrics_a, 'overall_governance_score'):.3f} | "
        f"{_avg(metrics_b, 'overall_governance_score'):.3f} | "
        f"{_delta_str(_avg(metrics_a, 'overall_governance_score'), _avg(metrics_b, 'overall_governance_score'))} |",
        f"| Avg Loop Efficiency | {_avg(metrics_a, 'loop_efficiency_score'):.3f} | "
        f"{_avg(metrics_b, 'loop_efficiency_score'):.3f} | "
        f"{_delta_str(_avg(metrics_a, 'loop_efficiency_score'), _avg(metrics_b, 'loop_efficiency_score'))} |",
        f"| Avg Error Resilience | {_avg(metrics_a, 'error_resilience_score'):.3f} | "
        f"{_avg(metrics_b, 'error_resilience_score'):.3f} | "
        f"{_delta_str(_avg(metrics_a, 'error_resilience_score'), _avg(metrics_b, 'error_resilience_score'))} |",
        f"| Avg Safety Score | {_avg(metrics_a, 'safety_score'):.3f} | "
        f"{_avg(metrics_b, 'safety_score'):.3f} | "
        f"{_delta_str(_avg(metrics_a, 'safety_score'), _avg(metrics_b, 'safety_score'))} |",
        f"| Avg Hallucination Guard | {_avg(metrics_a, 'hallucination_score'):.3f} | "
        f"{_avg(metrics_b, 'hallucination_score'):.3f} | "
        f"{_delta_str(_avg(metrics_a, 'hallucination_score'), _avg(metrics_b, 'hallucination_score'))} |",
        f"| Avg Autonomy | {_avg(metrics_a, 'autonomy_score'):.3f} | "
        f"{_avg(metrics_b, 'autonomy_score'):.3f} | "
        f"{_delta_str(_avg(metrics_a, 'autonomy_score'), _avg(metrics_b, 'autonomy_score'))} |",
        "",
        "### Raw Counts",
        "",
        f"| Metric | {label_a} | {label_b} | Delta |",
        f"|--------|{'-' * (len(label_a) + 2)}|{'-' * (len(label_b) + 2)}|-------|",
        f"| Total Loops | {_sum(metrics_a, 'loop_count')} | {_sum(metrics_b, 'loop_count')} | "
        f"{_delta_str(_sum(metrics_a, 'loop_count'), _sum(metrics_b, 'loop_count'), inverse=True)} |",
        f"| Total Errors | {_sum(metrics_a, 'failed_commands')} | {_sum(metrics_b, 'failed_commands')} | "
        f"{_delta_str(_sum(metrics_a, 'failed_commands'), _sum(metrics_b, 'failed_commands'), inverse=True)} |",
        f"| Total Tool Calls | {_sum(metrics_a, 'total_tool_calls')} | {_sum(metrics_b, 'total_tool_calls')} | "
        f"{_delta_str(_sum(metrics_a, 'total_tool_calls'), _sum(metrics_b, 'total_tool_calls'), inverse=True)} |",
        f"| Human Interventions | {_sum(metrics_a, 'human_interventions')} | {_sum(metrics_b, 'human_interventions')} | "
        f"{_delta_str(_sum(metrics_a, 'human_interventions'), _sum(metrics_b, 'human_interventions'), inverse=True)} |",
        "",
    ])

    return "\n".join(lines)
