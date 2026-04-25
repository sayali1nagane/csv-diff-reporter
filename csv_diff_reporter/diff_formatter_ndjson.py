"""Format a DiffResult as newline-delimited JSON (NDJSON / JSON Lines)."""
from __future__ import annotations

import json
from typing import Any, Dict

from csv_diff_reporter.differ import DiffResult, RowDiff


def _row_to_record(row: RowDiff) -> Dict[str, Any]:
    """Convert a single RowDiff to a plain dict suitable for JSON serialisation."""
    change_type: str
    if row.added:
        change_type = "added"
        fields = row.new_fields
    elif row.removed:
        change_type = "removed"
        fields = row.old_fields
    else:
        change_type = "modified"
        fields = row.new_fields

    record: Dict[str, Any] = {
        "key": row.key,
        "change_type": change_type,
        "fields": fields,
    }

    if not row.added and not row.removed and row.old_fields is not None:
        record["old_fields"] = row.old_fields

    return record


def format_diff_as_ndjson(result: DiffResult) -> str:
    """Return the diff rows serialised as NDJSON (one JSON object per line).

    An empty diff produces an empty string (no trailing newline).
    """
    if not result.rows:
        return ""

    lines = [json.dumps(_row_to_record(row), ensure_ascii=False) for row in result.rows]
    return "\n".join(lines)
