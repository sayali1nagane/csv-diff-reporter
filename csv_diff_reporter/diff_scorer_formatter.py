"""Formats a DiffScore for text or JSON output."""
from __future__ import annotations
import json
from csv_diff_reporter.diff_scorer import DiffScore

_SEVERITY_ICONS = {
    "none": "✔",
    "low": "ℹ",
    "medium": "⚠",
    "high": "✖",
}


def _as_text(score: DiffScore) -> str:
    icon = _SEVERITY_ICONS.get(score.severity, "?")
    pct = f"{score.change_rate * 100:.1f}%"
    lines = [
        "=== Diff Score ===",
        f"  Severity : {icon} {score.severity.upper()}",
        f"  Score    : {score.score}/100",
        f"  Changed  : {score.changed_rows} / {score.total_rows} rows ({pct})",
    ]
    return "\n".join(lines)


def _as_json(score: DiffScore) -> str:
    return json.dumps(score.as_dict(), indent=2)


def format_score(score: DiffScore, fmt: str = "text") -> str:
    if fmt == "json":
        return _as_json(score)
    return _as_text(score)
