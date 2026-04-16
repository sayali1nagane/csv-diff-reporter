"""Deduplicates rows in a DiffResult based on key and change type."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from csv_diff_reporter.differ import DiffResult, RowDiff


@dataclass
class DeduplicateOptions:
    keep: str = "first"  # "first" or "last"
    ignore_change_type: bool = False


def _row_key(row: RowDiff, ignore_change_type: bool) -> tuple:
    change = "" if ignore_change_type else row.change_type
    return (row.key, change)


def deduplicate_diff(
    result: DiffResult,
    options: Optional[DeduplicateOptions] = None,
) -> DiffResult:
    """Return a new DiffResult with duplicate rows removed."""
    if options is None:
        options = DeduplicateOptions()

    seen: dict[tuple, int] = {}
    rows = list(result.rows)

    if options.keep == "last":
        rows = list(reversed(rows))

    deduped: list[RowDiff] = []
    for row in rows:
        k = _row_key(row, options.ignore_change_type)
        if k not in seen:
            seen[k] = 1
            deduped.append(row)

    if options.keep == "last":
        deduped = list(reversed(deduped))

    return DiffResult(
        headers=result.headers,
        rows=deduped,
    )


def format_deduplicate_notice(original_count: int, deduped_count: int) -> str:
    dropped = original_count - deduped_count
    if dropped == 0:
        return "No duplicate rows found."
    return f"Removed {dropped} duplicate row(s) ({deduped_count} remaining)."
