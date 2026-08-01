"""CLI Entry Point — Transcript-Based Governance Evaluation.

Usage:
    python -m tools.governance_eval.cli analyze [--brain-dir DIR] [--rules-dir DIR] [--output FILE]
    python -m tools.governance_eval.cli compare --rules-a DIR --rules-b DIR [--brain-dir DIR] [--output FILE]

Commands:
    analyze     Scan all conversation transcripts, extract metrics, generate scorecard.
    compare     A/B compare two rule sets (requires --rules-a and --rules-b).
"""

import argparse
import os
import sys

from tools.governance_eval.metric_extractors import compute_governance_metrics
from tools.governance_eval.rule_set_tagger import (
    compare_rule_sets,
    hash_rules_directory,
)
from tools.governance_eval.scorecard_generator import (
    generate_aggregate_scorecard,
    generate_comparison_scorecard,
)
from tools.governance_eval.transcript_parser import discover_conversations

# Default paths
DEFAULT_BRAIN_DIR = os.path.expanduser(
    os.path.join("~", ".gemini", "antigravity-ide", "brain")
)
DEFAULT_RULES_DIR = os.path.join(os.getcwd(), ".agents", "rules")
DEFAULT_OUTPUT = "governance_scorecard.md"


def cmd_analyze(args: argparse.Namespace) -> int:
    """Run the analyze command: scan transcripts and generate scorecard."""
    brain_dir = args.brain_dir or DEFAULT_BRAIN_DIR
    rules_dir = args.rules_dir or DEFAULT_RULES_DIR
    output_path = args.output or DEFAULT_OUTPUT

    print(f"📂 Brain directory: {brain_dir}")
    print(f"📜 Rules directory: {rules_dir}")
    print()

    # Discover conversations
    print("🔍 Discovering conversations...")
    try:
        conversations = discover_conversations(brain_dir)
    except FileNotFoundError as exc:
        print(f"❌ {exc}")
        return 1

    if not conversations:
        print("⚠️  No conversations found with transcripts.")
        return 1

    print(f"   Found {len(conversations)} conversations")
    print()

    # Compute metrics for each conversation
    print("📊 Computing governance metrics...")
    all_metrics = []
    for conv in conversations:
        metrics = compute_governance_metrics(conv)
        all_metrics.append(metrics)
        print(
            f"   {conv.conversation_id[:12]}... "
            f"| steps={conv.total_steps:>4} "
            f"| score={metrics.overall_governance_score:.3f} "
            f"| loops={metrics.loop_count} "
            f"| errors={metrics.failed_commands}/{metrics.total_commands}"
        )

    print()

    # Fingerprint current rule set
    rule_set = None
    if os.path.isdir(rules_dir):
        print("🏷️  Fingerprinting active rule set...")
        rule_set = hash_rules_directory(rules_dir, label="current")
        print(f"   Hash: {rule_set.fingerprint_hash}")
        print(f"   Rules: {rule_set.rule_count} files, {rule_set.total_bytes} bytes")
        print()

    # Generate scorecard
    scorecard = generate_aggregate_scorecard(all_metrics, rule_set)

    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(scorecard)

    print(f"✅ Scorecard written to: {output_path}")
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    """Run the compare command: A/B test two rule sets."""
    rules_a = args.rules_a
    rules_b = args.rules_b
    brain_dir = args.brain_dir or DEFAULT_BRAIN_DIR
    output_path = args.output or "governance_comparison.md"

    if not rules_a or not rules_b:
        print("❌ Both --rules-a and --rules-b are required for comparison.")
        return 1

    print(f"📂 Brain directory: {brain_dir}")
    print(f"📜 Rule Set A: {rules_a}")
    print(f"📜 Rule Set B: {rules_b}")
    print()

    # Fingerprint both rule sets
    try:
        fp_a = hash_rules_directory(rules_a, label="A")
        fp_b = hash_rules_directory(rules_b, label="B")
    except FileNotFoundError as exc:
        print(f"❌ {exc}")
        return 1

    diff = compare_rule_sets(fp_a, fp_b)
    if diff["identical"]:
        print("⚠️  WARNING: Rule sets are byte-identical!")
    else:
        print(f"   Added:    {diff['added']}")
        print(f"   Removed:  {diff['removed']}")
        print(f"   Modified: {diff['modified']}")
    print()

    # Discover and compute metrics
    print("🔍 Discovering conversations...")
    try:
        conversations = discover_conversations(brain_dir)
    except FileNotFoundError as exc:
        print(f"❌ {exc}")
        return 1

    print(f"   Found {len(conversations)} conversations")
    print()

    print("📊 Computing governance metrics...")
    all_metrics = []
    for conv in conversations:
        metrics = compute_governance_metrics(conv)
        all_metrics.append(metrics)

    # For true A/B, you would tag conversations by which rule set was active.
    # Since we can't retroactively determine that from transcripts alone,
    # we use all conversations as a single cohort and compare rule sets structurally.
    # The comparison scorecard will note this limitation.
    scorecard = generate_comparison_scorecard(
        metrics_a=all_metrics,
        metrics_b=all_metrics,
        label_a=f"Rule Set A ({fp_a.label})",
        label_b=f"Rule Set B ({fp_b.label})",
        rule_diff=diff,
    )

    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(scorecard)

    print(f"✅ Comparison scorecard written to: {output_path}")
    return 0


def main() -> int:
    """Parse arguments and dispatch to the appropriate command."""
    parser = argparse.ArgumentParser(
        prog="governance_eval",
        description="Transcript-Based Governance Evaluation Framework",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # analyze subcommand
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Scan transcripts, extract metrics, generate scorecard",
    )
    analyze_parser.add_argument(
        "--brain-dir",
        help=f"Path to the Antigravity brain directory (default: {DEFAULT_BRAIN_DIR})",
    )
    analyze_parser.add_argument(
        "--rules-dir",
        help="Path to .agents/rules/ directory to fingerprint",
    )
    analyze_parser.add_argument(
        "--output", "-o",
        help=f"Output file path (default: {DEFAULT_OUTPUT})",
    )

    # compare subcommand
    compare_parser = subparsers.add_parser(
        "compare",
        help="A/B compare two rule sets",
    )
    compare_parser.add_argument("--rules-a", required=True, help="Path to Rule Set A")
    compare_parser.add_argument("--rules-b", required=True, help="Path to Rule Set B")
    compare_parser.add_argument("--brain-dir", help="Path to the brain directory")
    compare_parser.add_argument("--output", "-o", help="Output file path")

    args = parser.parse_args()

    if args.command == "analyze":
        return cmd_analyze(args)
    elif args.command == "compare":
        return cmd_compare(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
