"""Tests for csv_diff_reporter.diff_exporter_csv."""
import csv
import io

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_exporter_csv import CsvExportOptions, export_diff_to_csv


def _result(rows, headers=("id", "name")):
    return DiffResult(headers=list(headers), rows=rows)


def _row(change_type, old=None, new=None, key="1"):
    return RowDiff(key=key, change_type=change_type, old_row=old, new_row=new)


def _parse(csv_text):
    return list(csv.DictReader(io.StringIO(csv_text)))


def test_export_empty_result_returns_header_row():
    result = _result([])
    out = export_diff_to_csv(result)
    rows = _parse(out)
    assert rows == []
    assert "_change_type" in out
    assert "id" in out


def test_export_added_row():
    row = _row("added", new={"id": "1", "name": "Alice"})
    out = export_diff_to_csv(_result([row]))
    rows = _parse(out)
    assert len(rows) == 1
    assert rows[0]["_change_type"] == "added"
    assert rows[0]["name"] == "Alice"


def test_export_removed_row():
    row = _row("removed", old={"id": "2", "name": "Bob"})
    out = export_diff_to_csv(_result([row]))
    rows = _parse(out)
    assert rows[0]["_change_type"] == "removed"
    assert rows[0]["name"] == "Bob"


def test_export_modified_row_uses_new_values():
    row = _row("modified", old={"id": "3", "name": "Old"}, new={"id": "3", "name": "New"})
    out = export_diff_to_csv(_result([row]))
    rows = _parse(out)
    assert rows[0]["name"] == "New"
    assert rows[0]["_change_type"] == "modified"


def test_export_without_change_type_column():
    opts = CsvExportOptions(include_change_type=False)
    row = _row("added", new={"id": "1", "name": "Alice"})
    out = export_diff_to_csv(_result([row]), options=opts)
    assert "_change_type" not in out
    rows = _parse(out)
    assert rows[0]["name"] == "Alice"


def test_export_custom_change_type_column_name():
    opts = CsvExportOptions(change_type_column="change")
    row = _row("added", new={"id": "1", "name": "Alice"})
    out = export_diff_to_csv(_result([row]), options=opts)
    rows = _parse(out)
    assert "change" in rows[0]
    assert rows[0]["change"] == "added"


def test_export_custom_delimiter():
    opts = CsvExportOptions(delimiter=";")
    row = _row("added", new={"id": "1", "name": "Alice"})
    out = export_diff_to_csv(_result([row]), options=opts)
    assert ";" in out
    rows = list(csv.DictReader(io.StringIO(out), delimiter=";"))
    assert rows[0]["name"] == "Alice"


def test_export_multiple_rows():
    rows = [
        _row("added", new={"id": "1", "name": "A"}, key="1"),
        _row("removed", old={"id": "2", "name": "B"}, key="2"),
        _row("modified", old={"id": "3", "name": "C"}, new={"id": "3", "name": "D"}, key="3"),
    ]
    out = export_diff_to_csv(_result(rows))
    parsed = _parse(out)
    assert len(parsed) == 3
    types = [r["_change_type"] for r in parsed]
    assert types == ["added", "removed", "modified"]
