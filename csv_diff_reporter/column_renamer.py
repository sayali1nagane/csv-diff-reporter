"""Rename columns in a DiffResult for display purposes."""

from dataclasses import dataclass, replace
from typing import Dict, Optional

from csv_diff_reporter.differ import DiffResult, RowDiff


@dataclass
class RenameOptions:
    """Options controlling column renaming."""
    mapping: Dict[str, str]  # old_name -> new_name


def _rename_fields(fields: Dict[str, str], mapping: Dict[str, str]) -> Dict[str, str]:
    """Return a copy of *fields* with keys replaced according to *mapping*."""
    return {mapping.get(k, k): v for k, v in fields.items()}


def _rename_row_diff(row: RowDiff, mapping: Dict[str, str]) -> RowDiff:
    """Return a new RowDiff with renamed field keys."""
    old_fields = _rename_fields(row.old_fields, mapping) if row.old_fields is not None else None
    new_fields = _rename_fields(row.new_fields, mapping) if row.new_fields is not None else None
    return RowDiff(
        key=row.key,
        change_type=row.change_type,
        old_fields=old_fields,
        new_fields=new_fields,
    )


def rename_columns(
    result: DiffResult,
    options: Optional[RenameOptions],
) -> DiffResult:
    """Return a new DiffResult with columns renamed according to *options*.

    If *options* is ``None`` or the mapping is empty the original *result*
    is returned unchanged.
    """
    if options is None or not options.mapping:
        return result

    mapping = options.mapping
    renamed_rows = [_rename_row_diff(row, mapping) for row in result.rows]
    renamed_headers = [mapping.get(h, h) for h in result.headers]
    return DiffResult(rows=renamed_rows, headers=renamed_headers)
