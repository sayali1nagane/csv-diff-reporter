"""Flatten a DiffResult into a list of plain dicts for easy serialisation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from csv_diff_reporter.differ import DiffResult, RowDiff


@dataclass
class FlattenOptions:
    include_unchanged: bool = False
    change_type_key: str = "_change"
    key_column: Optional[str] = "_key"


@dataclass
class FlattenResult:
    rows: List[Dict[str, Any]] = field(default_factory=list)
    headers: List[str] = field(default_factory=list)
    total: int = 0

    def as_dicts(self) -> List[Dict[str, Any]]:
        return list(self.rows)


def _change_label(row: RowDiff) -> str:
    if row.old is None:
        return "added"
    if row.new is None:
        return "removed"
    return "modified"


def _flatten_row(row: RowDiff, opts: FlattenOptions) -> Dict[str, Any]:
    if row.new is not None:
        base: Dict[str, Any] = dict(row.new)
    elif row.old is not None:
        base = dict(row.old)
    else:
        base = {}

    record: Dict[str, Any] = {}
    if opts.key_column:
        record[opts.key_column] = row.key
    record[opts.change_type_key] = _change_label(row)
    record.update(base)
    return record


def flatten_diff(
    result: DiffResult,
    opts: Optional[FlattenOptions] = None,
) -> FlattenResult:
    if opts is None:
        opts = FlattenOptions()

    flat_rows: List[Dict[str, Any]] = []
    for row in result.rows:
        is_unchanged = row.old is not None and row.new is not None and row.old == row.new
        if is_unchanged and not opts.include_unchanged:
            continue
        flat_rows.append(_flatten_row(row, opts))

    extra_headers: List[str] = []
    if opts.key_column:
        extra_headers.append(opts.key_column)
    extra_headers.append(opts.change_type_key)
    headers = extra_headers + [h for h in result.headers if h not in extra_headers]

    return FlattenResult(rows=flat_rows, headers=headers, total=len(flat_rows))
