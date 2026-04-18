"""Format ComparisonResult as text or JSON."""
from __future__ import annotations
import json
from csv_diff_reporter.diff_comparator import ComparisonResult


def _as_text(result: ComparisonResult) -> str:
    a = result.labels.get("a", "A")
    b = result.labels.get("b", "B")
    lines = [f"Diff Comparison: {a} vs {b}", "-" * 40]
    for change_type in ("added", "removed", "modified"):
        common = getattr(result, f"common_{change_type}")
        only_a = getattr(result, f"{change_type}_only_in_a")
        only_b = getattr(result, f"{change_type}_only_in_b")
        lines.append(f"{change_type.capitalize()}:")
        lines.append(f"  common: {common}")
        lines.append(f"  only in {a}: {only_a}")
        lines.append(f"  only in {b}: {only_b}")
    return "\n".join(lines)


def _as_json(result: ComparisonResult) -> str:
    data = result.as_dict()
    data["labels"] = result.labels
    return json.dumps(data, indent=2)


def format_comparison(result: ComparisonResult, fmt: str = "text") -> str:
    if fmt == "json":
        return _as_json(result)
    return _as_text(result)
