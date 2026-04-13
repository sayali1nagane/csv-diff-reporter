"""Filtering utilities for DiffResult — include/exclude rows by change type or column."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Set

from csv_diff_reporter.differ import DiffResult, RowDiff


@dataclass
class FilterOptions:
    """Options controlling which rows survive the filter pass."""

    include_added: bool = True
    include_removed: bool = True
    include_modified: bool = True
    # When non-empty, only rows whose *changed* columns intersect this set pass.
    columns: Set[str] = field(default_factory=set)


def _row_matches(row: RowDiff, opts: FilterOptions) -> bool:
    """Return True if *row* should be kept according to *opts*."""
    if row.old is None and row.new is not None:
        if not opts.include_added:
            return False
    elif row.old is not None and row.new is None:
        if not opts.include_removed:
            return False
    else:
        if not opts.include_modified:
            return False

    if opts.columns:
        changed_cols: Set[str] = set()
        if row.old and row.new:
            changed_cols = {
                k for k in set(row.old) | set(row.new) if row.old.get(k) != row.new.get(k)
            }
        elif row.new:
            changed_cols = set(row.new.keys())
        elif row.old:
            changed_cols = set(row.old.keys())
        if not changed_cols.intersection(opts.columns):
            return False

    return True


def filter_diff(result: DiffResult, opts: Optional[FilterOptions] = None) -> DiffResult:
    """Return a new :class:`DiffResult` containing only rows that pass *opts*."""
    if opts is None:
        opts = FilterOptions()

    kept: List[RowDiff] = [row for row in result.rows if _row_matches(row, opts)]
    return DiffResult(rows=kept, headers=result.headers)
