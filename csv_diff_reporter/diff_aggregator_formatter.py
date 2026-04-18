"""Format AggregateResult as text or JSON."""
from __future__ import annotations
import json
from csv_diff_reporter.diff_aggregator import AggregateResult


def _as_text(agg: AggregateResult) -> str:
    if not agg.groups:
        return f"No data to aggregate on column '{agg.column}'."
    lines = [f"Aggregation by '{agg.column}':", ""]
    header = f"  {'Group':<20} {'Added':>6} {'Removed':>8} {'Modified':>9} {'Total':>6}"
    lines.append(header)
    lines.append("  " + "-" * 54)
    for grp in agg.sorted_groups():
        lines.append(
            f"  {grp.key:<20} {grp.added:>6} {grp.removed:>8} {grp.modified:>9} {grp.total:>6}"
        )
    return "\n".join(lines)


def _as_json(agg: AggregateResult) -> str:
    payload = {
        "column": agg.column,
        "groups": [g.as_dict() for g in agg.sorted_groups()],
    }
    return json.dumps(payload, indent=2)


def format_aggregate(agg: AggregateResult, fmt: str = "text") -> str:
    if fmt == "json":
        return _as_json(agg)
    return _as_text(agg)
