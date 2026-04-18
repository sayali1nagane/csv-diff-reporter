"""Pivot a DiffResult into a column-oriented summary.

For each column that appears in the diff, collect the old and new values
from modified rows so callers can see how a single field changed across
all affected rows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from csv_diff_reporter.differ import DiffResult, RowDiff


@dataclass
class ColumnPivot:
    """All observed value transitions for a single column."""

    column: str
    # Each entry is (row_key, old_value, new_value).  old/new are None for
    # added/removed rows where only one side exists.
    changes: List[Tuple[str, Optional[str], Optional[str]]] = field(default_factory=list)

    @property
    def change_count(self) -> int:
        return len(self.changes)

    def as_dict(self) -> dict:
        return {
            "column": self.column,
            "change_count": self.change_count,
            "changes": [
                {"key": k, "old": o, "new": n} for k, o, n in self.changes
            ],
        }


@dataclass
class PivotResult:
    """Column-oriented view of a DiffResult."""

    # Ordered list of column names present in the pivot.
    columns: List[str] = field(default_factory=list)
    # Mapping from column name to its pivot data.
    pivots: Dict[str, ColumnPivot] = field(default_factory=dict)

    def get(self, column: str) -> Optional[ColumnPivot]:
        return self.pivots.get(column)

    def as_dict(self) -> dict:
        return {
            "columns": self.columns,
            "pivots": {col: pv.as_dict() for col, pv in self.pivots.items()},
        }


def _record(pivot: ColumnPivot, row_key: str, old: Optional[str], new: Optional[str]) -> None:
    pivot.changes.append((row_key, old, new))


def _ensure_column(result: PivotResult, column: str) -> ColumnPivot:
    if column not in result.pivots:
        result.columns.append(column)
        result.pivots[column] = ColumnPivot(column=column)
    return result.pivots[column]


def pivot_diff(diff: DiffResult) -> PivotResult:
    """Build a :class:`PivotResult` from *diff*.

    - **Modified rows**: each field whose value changed contributes an entry
      with both old and new values.
    - **Added rows**: every field contributes an entry with ``old=None``.
    - **Removed rows**: every field contributes an entry with ``new=None``.
    - Unchanged rows are ignored.
    """
    result = PivotResult()

    for row_diff in diff.rows:
        key = row_diff.key

        if row_diff.is_added:
            for col, new_val in (row_diff.new_row or {}).items():
                pv = _ensure_column(result, col)
                _record(pv, key, None, new_val)

        elif row_diff.is_removed:
            for col, old_val in (row_diff.old_row or {}).items():
                pv = _ensure_column(result, col)
                _record(pv, key, old_val, None)

        elif row_diff.is_modified:
            old_row = row_diff.old_row or {}
            new_row = row_diff.new_row or {}
            all_cols = dict.fromkeys(list(old_row) + list(new_row))
            for col in all_cols:
                old_val = old_row.get(col)
                new_val = new_row.get(col)
                if old_val != new_val:
                    pv = _ensure_column(result, col)
                    _record(pv, key, old_val, new_val)

    return result
