"""Format an AnnotatedResult as plain text or JSON."""
from __future__ import annotations

import json
from typing import List

from csv_diff_reporter.row_annotator import AnnotatedResult, AnnotatedRow

_SEVERITY_ICONS = {
    "info": "ℹ",
    "warning": "⚠",
    "critical": "✖",
}


def _row_to_dict(ar: AnnotatedRow) -> dict:
    d = {
        "key": ar.row.key,
        "change_type": ar.row.change_type,
        "label": ar.label,
        "severity": ar.severity,
    }
    if ar.note:
        d["note"] = ar.note
    if ar.row.diff:
        d["diff"] = {k: {"old": v[0], "new": v[1]} for k, v in ar.row.diff.items()}
    return d


def _as_text(result: AnnotatedResult) -> str:
    if not result.rows:
        return "No annotated changes."
    lines: List[str] = []
    for ar in result.rows:
        icon = _SEVERITY_ICONS.get(ar.severity, "?")
        lines.append(f"{icon} [{ar.severity.upper()}] {ar.label} — key: {ar.row.key}")
        if ar.note:
            lines.append(f"   {ar.note}")
    return "\n".join(lines)


def _as_json(result: AnnotatedResult) -> str:
    return json.dumps([_row_to_dict(ar) for ar in result.rows], indent=2)


def format_annotated(result: AnnotatedResult, fmt: str = "text") -> str:
    """Return *result* formatted as *fmt* ('text' or 'json')."""
    if fmt == "json":
        return _as_json(result)
    return _as_text(result)
