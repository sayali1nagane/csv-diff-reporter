"""Formatters for PivotResult output."""
from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from csv_diff_reporter.diff_pivot import PivotResult


def _as_text(pivot: "PivotResult") -> str:
    if not pivot.columns:
        return "No pivot data available.\n"

    lines: list[str] = ["Column Change Pivot", "=" * 40]
    for col in pivot.columns:
        cp = pivot.get(col)
        if cp is None:
            continue
        lines.append(f"\n{col}")
        lines.append("-" * len(col))
        lines.append(f"  Total changes : {cp.change_count()}")
        d = cp.as_dict()
        for val, count in sorted(d["value_counts"].items(), key=lambda x: -x[1]):
            lines.append(f"  {val!r:30s} {count}")
    lines.append("")
    return "\n".join(lines)


def _as_json(pivot: "PivotResult") -> str:
    payload: dict = {"columns": {}}
    for col in pivot.columns:
        cp = pivot.get(col)
        if cp is not None:
            payload["columns"][col] = cp.as_dict()
    return json.dumps(payload, indent=2)


def format_pivot(pivot: "PivotResult", fmt: str = "text") -> str:
    """Return a formatted string for *pivot*.

    Parameters
    ----------
    pivot:
        A :class:`~csv_diff_reporter.diff_pivot.PivotResult` instance.
    fmt:
        ``"text"`` (default) or ``"json"``.
    """
    if fmt == "json":
        return _as_json(pivot)
    return _as_text(pivot)
