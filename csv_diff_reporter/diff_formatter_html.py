"""HTML formatter for diff results."""
from __future__ import annotations

import html
from typing import List

from csv_diff_reporter.differ import DiffResult, RowDiff

_CHANGE_CLASS = {
    "added": "diff-added",
    "removed": "diff-removed",
    "modified": "diff-modified",
}

_STYLE = """
<style>
  table { border-collapse: collapse; font-family: monospace; font-size: 13px; }
  th, td { border: 1px solid #ccc; padding: 4px 8px; }
  .diff-added { background: #e6ffed; }
  .diff-removed { background: #ffeef0; }
  .diff-modified { background: #fff8c5; }
  .summary { margin-bottom: 12px; font-family: sans-serif; }
</style>
"""


def _escape(value: str) -> str:
    return html.escape(str(value))


def _row_to_html(row: RowDiff, headers: List[str]) -> str:
    css = _CHANGE_CLASS.get(row.change_type, "")
    cells = "".join(
        f"<td>{_escape(row.new_fields.get(h, row.old_fields.get(h, '')) )}</td>"
        for h in headers
    )
    return f'<tr class="{css}"><td>{_escape(row.change_type)}</td><td>{_escape(row.key)}</td>{cells}</tr>'


def format_diff_as_html(result: DiffResult, title: str = "CSV Diff Report") -> str:
    headers = result.headers
    rows = result.rows

    added = sum(1 for r in rows if r.change_type == "added")
    removed = sum(1 for r in rows if r.change_type == "removed")
    modified = sum(1 for r in rows if r.change_type == "modified")

    summary_html = (
        f'<div class="summary">'
        f"<strong>{_escape(title)}</strong> &mdash; "
        f"Added: {added}, Removed: {removed}, Modified: {modified}"
        f"</div>"
    )

    if not rows:
        return f"<!DOCTYPE html><html><head>{_STYLE}</head><body>{summary_html}<p>No differences found.</p></body></html>"

    header_cells = "".join(f"<th>{_escape(h)}</th>" for h in headers)
    header_row = f"<tr><th>change</th><th>key</th>{header_cells}</tr>"
    body_rows = "\n".join(_row_to_html(r, headers) for r in rows)

    table = f"<table>{header_row}\n{body_rows}</table>"
    return f"<!DOCTYPE html><html><head>{_STYLE}</head><body>{summary_html}{table}</body></html>"
