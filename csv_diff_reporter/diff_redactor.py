"""Redact sensitive column values from a DiffResult."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, Optional

from csv_diff_reporter.differ import DiffResult, RowDiff


_MASK = "***"


@dataclass(frozen=True)
class RedactOptions:
    columns: FrozenSet[str] = field(default_factory=frozenset)
    mask: str = _MASK


def _redact_fields(
    fields: dict[str, str],
    columns: FrozenSet[str],
    mask: str,
) -> dict[str, str]:
    return {k: (mask if k in columns else v) for k, v in fields.items()}


def _redact_row(row: RowDiff, opts: RedactOptions) -> RowDiff:
    if not opts.columns:
        return row
    old = (
        _redact_fields(row.old_fields, opts.columns, opts.mask)
        if row.old_fields is not None
        else None
    )
    new = (
        _redact_fields(row.new_fields, opts.columns, opts.mask)
        if row.new_fields is not None
        else None
    )
    return RowDiff(key=row.key, change_type=row.change_type, old_fields=old, new_fields=new)


def redact_diff(result: DiffResult, opts: Optional[RedactOptions] = None) -> DiffResult:
    """Return a new DiffResult with sensitive columns masked."""
    if opts is None or not opts.columns:
        return result
    redacted_rows = [_redact_row(r, opts) for r in result.rows]
    return DiffResult(headers=result.headers, rows=redacted_rows)
