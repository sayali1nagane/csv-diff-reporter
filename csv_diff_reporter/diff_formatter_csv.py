"""Format a DiffResult as a CSV string for export or piping."""
from __future__ import annotations

import csv
import io
from typing import List

from csv_diff_reporter.differ import DiffResult, RowDiff


_CHANGE_TYPE_HEADER = "_change_type"
_KEY_HEADER = "_key"


def _collect_field_headers(result: DiffResult) -> List[str]:
    """Return sorted field names seen across all row diffs."""
    seen: set[str] = set()
    for row in result.rows:
        if row.new_fields:
            seen.update(row.new_fields.keys())
        if row.old_fields:
            seen.update(row.old_fields.keys())
    return sorted(seen)


def _row_to_record(row: RowDiff, field_headers: List[str]) -> dict:
    """Convert a RowDiff to a flat dict suitable for csv.DictWriter."""
    fields = row.new_fields or row.old_fields or {}
    record: dict = {
        _CHANGE_TYPE_HEADER: row.change_type,
        _KEY_HEADER: row.key,
    }
    for header in field_headers:
        record[header] = fields.get(header, "")
    return record


def format_diff_as_csv(result: DiffResult, include_unchanged: bool = False) -> str:
    """Serialise *result* to a CSV string.

    Parameters
    ----------
    result:
        The diff result to format.
    include_unchanged:
        When *True*, rows with change_type ``"unchanged"`` are included.
        Defaults to *False* to keep output concise.
    """
    rows = [
        r
        for r in result.rows
        if include_unchanged or r.change_type != "unchanged"
    ]

    field_headers = _collect_field_headers(result)
    column_names = [_CHANGE_TYPE_HEADER, _KEY_HEADER] + field_headers

    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=column_names,
        lineterminator="\n",
        extrasaction="ignore",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(_row_to_record(row, field_headers))

    return buf.getvalue()
