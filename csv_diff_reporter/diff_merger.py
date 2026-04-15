"""Merge two DiffResult objects into one, combining their rows and headers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from csv_diff_reporter.differ import DiffResult, RowDiff


@dataclass
class MergeOptions:
    """Options controlling how two diffs are merged."""
    deduplicate: bool = True  # drop rows whose key appears in both diffs (keep first)
    tag_source: bool = False  # add a '__source__' field indicating origin ("a" or "b")
    source_a_label: str = "a"
    source_b_label: str = "b"


@dataclass
class MergeResult:
    result: DiffResult
    duplicate_keys: List[str] = field(default_factory=list)


def _tag_row(row: RowDiff, label: str) -> RowDiff:
    """Return a copy of *row* with a '__source__' field appended to old/new."""
    def _add(d: dict | None) -> dict | None:
        if d is None:
            return None
        return {**d, "__source__": label}

    return RowDiff(
        key=row.key,
        change_type=row.change_type,
        old_row=_add(row.old_row),
        new_row=_add(row.new_row),
    )


def merge_diffs(
    diff_a: DiffResult,
    diff_b: DiffResult,
    options: MergeOptions | None = None,
) -> MergeResult:
    """Merge *diff_a* and *diff_b* into a single :class:`DiffResult`.

    Parameters
    ----------
    diff_a:
        Primary diff.  Rows from this diff are always included.
    diff_b:
        Secondary diff.  Rows are appended after *diff_a* rows.
    options:
        Merge behaviour; defaults to :class:`MergeOptions` defaults.

    Returns
    -------
    MergeResult
        Combined diff plus a list of keys that appeared in both inputs.
    """
    if options is None:
        options = MergeOptions()

    keys_a = {row.key for row in diff_a.rows}
    duplicate_keys: List[str] = []
    merged_rows: List[RowDiff] = []

    for row in diff_a.rows:
        r = _tag_row(row, options.source_a_label) if options.tag_source else row
        merged_rows.append(r)

    for row in diff_b.rows:
        if options.deduplicate and row.key in keys_a:
            duplicate_keys.append(row.key)
            continue
        r = _tag_row(row, options.source_b_label) if options.tag_source else row
        merged_rows.append(r)

    # Merge headers — preserve order, union of both
    seen: dict[str, None] = {}
    for h in list(diff_a.headers) + list(diff_b.headers):
        seen[h] = None
    if options.tag_source:
        seen["__source__"] = None
    merged_headers = list(seen.keys())

    merged_diff = DiffResult(rows=merged_rows, headers=merged_headers)
    return MergeResult(result=merged_diff, duplicate_keys=duplicate_keys)
