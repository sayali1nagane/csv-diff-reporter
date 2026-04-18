"""Aggregate diff rows by a column value, counting changes per group."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from csv_diff_reporter.differ import DiffResult, RowDiff


@dataclass
class AggregateGroup:
    key: str
    added: int = 0
    removed: int = 0
    modified: int = 0

    @property
    def total(self) -> int:
        return self.added + self.removed + self.modified

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "added": self.added,
            "removed": self.removed,
            "modified": self.modified,
            "total": self.total,
        }


@dataclass
class AggregateResult:
    column: str
    groups: Dict[str, AggregateGroup] = field(default_factory=dict)

    def get(self, key: str) -> Optional[AggregateGroup]:
        return self.groups.get(key)

    def sorted_groups(self, by: str = "total", descending: bool = True) -> List[AggregateGroup]:
        return sorted(self.groups.values(), key=lambda g: getattr(g, by), reverse=descending)


def aggregate_diff(result: DiffResult, column: str) -> AggregateResult:
    """Group diff rows by the value of *column* and count change types."""
    agg = AggregateResult(column=column)
    for row in result.rows:
        fields = row.new_fields if row.new_fields is not None else row.old_fields
        if fields is None:
            continue
        val = fields.get(column, "")
        if val not in agg.groups:
            agg.groups[val] = AggregateGroup(key=val)
        grp = agg.groups[val]
        if row.change_type == "added":
            grp.added += 1
        elif row.change_type == "removed":
            grp.removed += 1
        elif row.change_type == "modified":
            grp.modified += 1
    return agg
