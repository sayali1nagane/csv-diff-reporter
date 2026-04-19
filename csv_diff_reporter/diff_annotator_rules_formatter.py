"""Formatter for rule-based annotation results."""
from __future__ import annotations
import json
from csv_diff_reporter.diff_annotator_rules import RuleResult


def _as_text(result: RuleResult) -> str:
    lines = []
    lines.append(f"Rule Check: {result.total_checked} rows checked")
    if not result.has_violations:
        lines.append("  No violations found.")
        return "\n".join(lines)
    lines.append(f"  Violations: {len(result.matches)}")
    lines.append("")
    for m in result.matches:
        lines.append(f"  [{m.change_type.upper()}] key={m.row_key} | {m.rule_name}: {m.message}")
    return "\n".join(lines)


def _as_json(result: RuleResult) -> str:
    data = {
        "total_checked": result.total_checked,
        "violations": len(result.matches),
        "matches": [m.as_dict() for m in result.matches],
    }
    return json.dumps(data, indent=2)


def format_rule_result(result: RuleResult, fmt: str = "text") -> str:
    if fmt == "json":
        return _as_json(result)
    return _as_text(result)
