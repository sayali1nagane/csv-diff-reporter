"""Column-level filtering for diff results.

Allows including or excluding specific columns from the diff output,
so users can focus on the fields that matter.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from csv_diff_reporter.differ import DiffResult, RowDiff


@dataclass
class ColumnFilterOptions:
    include_columns: Optional[List[str]] = None  # None means include all
    exclude_columns: List[str] = field(default_factory=list)


def _filter_row_fields(row_diff: RowDiff, options: ColumnFilterOptions) -> RowDiff:
    """Return a new RowDiff with field dicts restricted to the selected columns."""
    include = options.include_columns
    exclude = set(options.exclude_columns)

    def _keep(col: str) -> bool:
        if col in exclude:
            return False
        if include is not None and col not in include:
            return False
        return True

    old = (
        {k: v for k, v in row_diff.old_row.items() if _keep(k)}
        if row_diff.old_row is not None
        else None
    )
    new = (
        {k: v for k, v in row_diff.new_row.items() if _keep(k)}
        if row_diff.new_row is not None
        else None
    )
    changed = (
        [c for c in row_diff.changed_fields if _keep(c)]
        if row_diff.changed_fields is not None
        else None
    )

    return RowDiff(
        key=row_diff.key,
        change_type=row_diff.change_type,
        old_row=old,
        new_row=new,
        changed_fields=changed,
    )


def filter_columns(result: DiffResult, options: ColumnFilterOptions) -> DiffResult:
    """Apply column filtering to every RowDiff in *result*."""
    if not options.include_columns and not options.exclude_columns:
        return result

    filtered_rows = [_filter_row_fields(rd, options) for rd in result.rows]
    return DiffResult(rows=filtered_rows, headers=result.headers)
