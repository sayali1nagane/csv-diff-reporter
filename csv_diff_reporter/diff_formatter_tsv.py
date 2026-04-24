"""Export a DiffResult as TSV (tab-separated values)."""
from __future__ import annotations

from typing import List

from csv_diff_reporter.differ import DiffResult, RowDiff

_CHANGE_TYPE_LABEL = {
    "added": "added",
    "removed": "removed",
    "modified": "modified",
}


def _escape(value: str) -> str:
    """Escape tab and newline characters inside a field value."""
    return value.replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")


def _row_to_tsv_record(row: RowDiff, headers: List[str]) -> str:
    """Convert a single RowDiff to a TSV line."""
    change_type = _CHANGE_TYPE_LABEL.get(row.change_type, row.change_type)
    fields = row.new_fields if row.new_fields is not None else row.old_fields or {}
    values = [_escape(str(fields.get(h, ""))) for h in headers]
    parts = [_escape(str(row.key)), change_type] + values
    return "\t".join(parts)


def format_diff_as_tsv(result: DiffResult) -> str:
    """Render *result* as a TSV string.

    The output has the following columns:
      _key, _change_type, <header1>, <header2>, …

    For modified rows the *new* field values are used.
    """
    headers: List[str] = list(result.headers)
    header_line = "\t".join(["_key", "_change_type"] + headers)

    rows = result.added + result.removed + result.modified
    if not rows:
        return header_line + "\n"

    lines = [header_line]
    for row in rows:
        lines.append(_row_to_tsv_record(row, headers))
    return "\n".join(lines) + "\n"
