"""Sorting utilities for DiffResult rows."""

from __future__ import annotations

from typing import Literal, Optional

from csv_diff_reporter.differ import DiffResult, RowDiff

SortKey = Literal["key", "type"]
SortOrder = Literal["asc", "desc"]

_CHANGE_TYPE_ORDER = {"added": 0, "removed": 1, "modified": 2}


def _change_type(row: RowDiff) -> str:
    if row.old is None:
        return "added"
    if row.new is None:
        return "removed"
    return "modified"


def sort_diff(
    result: DiffResult,
    by: SortKey = "key",
    order: SortOrder = "asc",
) -> DiffResult:
    """Return a new :class:`DiffResult` with rows sorted by *by* in *order*.

    Parameters
    ----------
    result:
        The diff result to sort.
    by:
        ``"key"`` sorts lexicographically by the row key;
        ``"type"`` groups rows by change type (added → removed → modified).
    order:
        ``"asc"`` for ascending, ``"desc"`` for descending.
    """
    reverse = order == "desc"

    if by == "key":
        sorted_rows = sorted(result.rows, key=lambda r: r.key, reverse=reverse)
    elif by == "type":
        sorted_rows = sorted(
            result.rows,
            key=lambda r: _CHANGE_TYPE_ORDER[_change_type(r)],
            reverse=reverse,
        )
    else:
        raise ValueError(f"Unknown sort key: {by!r}")

    return DiffResult(rows=sorted_rows, headers=result.headers)
