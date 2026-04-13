"""Truncation utilities for limiting diff output to a maximum number of rows."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from csv_diff_reporter.differ import DiffResult, RowDiff


@dataclass
class TruncateResult:
    """Wraps a DiffResult alongside truncation metadata."""

    diff: DiffResult
    original_count: int
    truncated: bool
    limit: Optional[int]

    @property
    def dropped(self) -> int:
        """Number of rows that were dropped due to the limit."""
        return max(0, self.original_count - len(self.diff.rows))


def truncate_diff(
    result: DiffResult,
    limit: Optional[int] = None,
) -> TruncateResult:
    """Return a new DiffResult containing at most *limit* rows.

    If *limit* is ``None`` or greater than or equal to the number of rows,
    the original result is returned unchanged (wrapped in a TruncateResult).

    Parameters
    ----------
    result:
        The full diff result to (potentially) truncate.
    limit:
        Maximum number of rows to keep.  ``None`` means no limit.

    Returns
    -------
    TruncateResult
        Wrapper containing the (possibly shortened) diff and metadata.
    """
    original_count = len(result.rows)

    if limit is None or limit >= original_count:
        return TruncateResult(
            diff=result,
            original_count=original_count,
            truncated=False,
            limit=limit,
        )

    truncated_rows: list[RowDiff] = result.rows[:limit]
    truncated_diff = DiffResult(rows=truncated_rows, headers=result.headers)

    return TruncateResult(
        diff=truncated_diff,
        original_count=original_count,
        truncated=True,
        limit=limit,
    )


def format_truncation_notice(tr: TruncateResult) -> str:
    """Return a human-readable notice when rows were dropped, else empty string."""
    if not tr.truncated:
        return ""
    return (
        f"[Truncated: showing {tr.limit} of {tr.original_count} changed rows, "
        f"{tr.dropped} row(s) omitted]"
    )
