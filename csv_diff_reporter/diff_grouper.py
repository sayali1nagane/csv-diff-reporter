"""Group diff rows by a column value for structured reporting."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csv_diff_reporter.differ import DiffResult, RowDiff


@dataclass
class GroupOptions:
    column: str
    include_ungrouped: bool = True
    ungrouped_label: str = "(other)"


@dataclass
class GroupedDiff:
    column: str
    groups: Dict[str, List[RowDiff]] = field(default_factory=dict)

    def group_keys(self) -> List[str]:
        """Return sorted group keys."""
        return sorted(self.groups.keys())

    def rows_for(self, key: str) -> List[RowDiff]:
        return self.groups.get(key, [])

    def total_rows(self) -> int:
        return sum(len(rows) for rows in self.groups.values())


def _group_value(row: RowDiff, column: str, fallback: str) -> str:
    """Extract the grouping value from a RowDiff."""
    fields: Optional[Dict[str, str]] = None
    if row.new_fields is not None:
        fields = row.new_fields
    elif row.old_fields is not None:
        fields = row.old_fields
    if fields is None:
        return fallback
    return fields.get(column, fallback)


def group_diff(result: DiffResult, options: GroupOptions) -> GroupedDiff:
    """Partition rows in *result* into buckets keyed by *options.column*.

    Rows that lack the grouping column are placed under
    *options.ungrouped_label* when *options.include_ungrouped* is True;
    otherwise they are silently dropped.
    """
    grouped: Dict[str, List[RowDiff]] = {}

    for row in result.rows:
        value = _group_value(row, options.column, options.ungrouped_label)
        if value == options.ungrouped_label and not options.include_ungrouped:
            continue
        grouped.setdefault(value, []).append(row)

    return GroupedDiff(column=options.column, groups=grouped)
