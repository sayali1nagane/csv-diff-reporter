"""Normalize field values in a DiffResult for consistent comparison.

Supports stripping whitespace, lowercasing, and custom value mappings.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from csv_diff_reporter.differ import DiffResult, RowDiff


@dataclass
class NormalizeOptions:
    strip_whitespace: bool = True
    lowercase: bool = False
    value_map: Dict[str, str] = field(default_factory=dict)


def _normalize_value(value: str, opts: NormalizeOptions) -> str:
    """Apply normalization rules to a single string value."""
    if opts.strip_whitespace:
        value = value.strip()
    if opts.lowercase:
        value = value.lower()
    if opts.value_map and value in opts.value_map:
        value = opts.value_map[value]
    return value


def _normalize_fields(
    fields: Optional[Dict[str, str]], opts: NormalizeOptions
) -> Optional[Dict[str, str]]:
    if fields is None:
        return None
    return {k: _normalize_value(v, opts) for k, v in fields.items()}


def _normalize_row_diff(row: RowDiff, opts: NormalizeOptions) -> RowDiff:
    """Return a new RowDiff with normalized field values."""
    return RowDiff(
        key=row.key,
        change_type=row.change_type,
        old_fields=_normalize_fields(row.old_fields, opts),
        new_fields=_normalize_fields(row.new_fields, opts),
    )


def normalize_diff(result: DiffResult, opts: Optional[NormalizeOptions] = None) -> DiffResult:
    """Return a new DiffResult with all field values normalized.

    If *opts* is None a default NormalizeOptions() is used (strip whitespace only).
    """
    if opts is None:
        opts = NormalizeOptions()

    normalized_rows = [_normalize_row_diff(row, opts) for row in result.rows]
    return DiffResult(
        headers=result.headers,
        rows=normalized_rows,
    )
