"""Export a DiffResult back to CSV format."""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from typing import Optional

from csv_diff_reporter.differ import DiffResult, RowDiff


@dataclass
class CsvExportOptions:
    include_change_type: bool = True
    change_type_column: str = "_change_type"
    delimiter: str = ","


def _row_to_record(row_diff: RowDiff, headers: list[str], options: CsvExportOptions) -> dict:
    fields = row_diff.new_row if row_diff.new_row is not None else row_diff.old_row
    record = {h: (fields.get(h, "") if fields else "") for h in headers}
    if options.include_change_type:
        record[options.change_type_column] = row_diff.change_type
    return record


def export_diff_to_csv(
    result: DiffResult,
    options: Optional[CsvExportOptions] = None,
) -> str:
    """Serialise a DiffResult to a CSV string.

    Returns an empty string (header-only) when there are no changed rows.
    """
    if options is None:
        options = CsvExportOptions()

    rows = result.rows
    headers = list(result.headers)

    if not rows:
        out_headers = headers + ([options.change_type_column] if options.include_change_type else [])
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=out_headers, delimiter=options.delimiter)
        writer.writeheader()
        return buf.getvalue()

    out_headers = headers + ([options.change_type_column] if options.include_change_type else [])
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=out_headers,
        delimiter=options.delimiter,
        extrasaction="ignore",
    )
    writer.writeheader()
    for row_diff in rows:
        writer.writerow(_row_to_record(row_diff, headers, options))

    return buf.getvalue()
