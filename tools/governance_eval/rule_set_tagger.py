"""Rule Set Tagger — Fingerprints governance rule sets for A/B comparison.

Hashes all .agents/rules/*.md files to create a unique fingerprint
for the rule set that was active during a conversation.
"""

import hashlib
import os
from dataclasses import dataclass, field


@dataclass
class RuleSetFingerprint:
    """A unique fingerprint for a set of governance rules."""
    fingerprint_hash: str
    rule_count: int
    total_bytes: int
    rule_files: dict[str, str] = field(default_factory=dict)  # filename -> md5
    label: str = ""  # User-friendly label like "v1-baseline" or "v2-template"


def hash_rules_directory(rules_dir: str, label: str = "") -> RuleSetFingerprint:
    """Compute a fingerprint for all .md files in a rules directory.

    Args:
        rules_dir: Absolute path to a .agents/rules/ directory.
        label: Optional human-readable label for this rule set.

    Returns:
        RuleSetFingerprint with per-file and aggregate hashes.
    """
    if not os.path.isdir(rules_dir):
        raise FileNotFoundError(f"Rules directory not found: {rules_dir}")

    rule_files: dict[str, str] = {}
    total_bytes = 0

    for entry in sorted(os.scandir(rules_dir), key=lambda e: e.name):
        if not entry.is_file() or not entry.name.endswith(".md"):
            continue

        file_hash = hashlib.md5()
        with open(entry.path, "rb") as fh:
            data = fh.read()
            file_hash.update(data)
            total_bytes += len(data)

        rule_files[entry.name] = file_hash.hexdigest().upper()

    # Aggregate hash: hash of all individual hashes in order
    aggregate = hashlib.md5()
    for filename in sorted(rule_files.keys()):
        aggregate.update(rule_files[filename].encode())
    fingerprint_hash = aggregate.hexdigest().upper()

    return RuleSetFingerprint(
        fingerprint_hash=fingerprint_hash,
        rule_count=len(rule_files),
        total_bytes=total_bytes,
        rule_files=rule_files,
        label=label or fingerprint_hash[:8],
    )


def compare_rule_sets(
    set_a: RuleSetFingerprint,
    set_b: RuleSetFingerprint,
) -> dict:
    """Compare two rule set fingerprints and report differences.

    Returns a dict with:
      - identical: bool
      - added: list of files only in set_b
      - removed: list of files only in set_a
      - modified: list of files present in both but with different hashes
      - unchanged: list of files identical in both
    """
    files_a = set(set_a.rule_files.keys())
    files_b = set(set_b.rule_files.keys())

    added = sorted(files_b - files_a)
    removed = sorted(files_a - files_b)
    common = sorted(files_a & files_b)

    modified = []
    unchanged = []
    for f in common:
        if set_a.rule_files[f] != set_b.rule_files[f]:
            modified.append(f)
        else:
            unchanged.append(f)

    return {
        "identical": len(added) == 0 and len(removed) == 0 and len(modified) == 0,
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged": unchanged,
        "set_a_label": set_a.label,
        "set_b_label": set_b.label,
    }


def fingerprint_to_dict(fp: RuleSetFingerprint) -> dict:
    """Serialize a RuleSetFingerprint to a JSON-compatible dict."""
    return {
        "fingerprint_hash": fp.fingerprint_hash,
        "rule_count": fp.rule_count,
        "total_bytes": fp.total_bytes,
        "label": fp.label,
        "rule_files": fp.rule_files,
    }
