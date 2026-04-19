"""Profile a DiffResult to produce field-level value frequency statistics."""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import Counter
from typing import Dict, List
from csv_diff_reporter.differ import DiffResult, RowDiff


@dataclass
class FieldProfile:
    column: str
    total_values: int
    unique_values: int
    top_values: List[tuple]  # (value, count)

    def as_dict(self) -> dict:
        return {
            "column": self.column,
            "total_values": self.total_values,
            "unique_values": self.unique_values,
            "top_values": [{"value": v, "count": c} for v, c in self.top_values],
        }


@dataclass
class ProfileResult:
    headers: List[str]
    profiles: Dict[str, FieldProfile] = field(default_factory=dict)

    def get(self, column: str) -> FieldProfile | None:
        return self.profiles.get(column)

    def as_dict(self) -> dict:
        return {
            "headers": self.headers,
            "profiles": {k: v.as_dict() for k, v in self.profiles.items()},
        }


def _collect_values(rows: List[RowDiff]) -> Dict[str, List[str]]:
    values: Dict[str, List[str]] = {}
    for row in rows:
        fields = row.new_fields if row.new_fields is not None else (row.old_fields or {})
        for col, val in fields.items():
            values.setdefault(col, []).append(str(val) if val is not None else "")
    return values


def profile_diff(result: DiffResult, top_n: int = 5) -> ProfileResult:
    """Compute per-column value frequency profiles across all diff rows."""
    all_rows = result.added + result.removed + result.modified
    value_map = _collect_values(all_rows)
    profiles: Dict[str, FieldProfile] = {}
    for col, vals in value_map.items():
        counter = Counter(vals)
        profiles[col] = FieldProfile(
            column=col,
            total_values=len(vals),
            unique_values=len(counter),
            top_values=counter.most_common(top_n),
        )
    return ProfileResult(headers=result.headers, profiles=profiles)
