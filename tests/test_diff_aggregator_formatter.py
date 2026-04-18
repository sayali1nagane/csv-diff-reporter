import json
import pytest
from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_aggregator import aggregate_diff
from csv_diff_reporter.diff_aggregator_formatter import format_aggregate


def _row(change_type, fields):
    old = fields if change_type in ("removed", "modified") else None
    new = fields if change_type in ("added", "modified") else None
    return RowDiff(key=fields.get("id", "k"), change_type=change_type, old_fields=old, new_fields=new)


def _make_result(rows):
    return DiffResult(headers=["id", "region"], rows=rows)


def test_format_text_empty():
    agg = aggregate_diff(_make_result([]), "region")
    out = format_aggregate(agg, "text")
    assert "No data" in out
    assert "region" in out


def test_format_text_contains_group_key():
    rows = [_row("added", {"id": "1", "region": "EU"})]
    agg = aggregate_diff(_make_result(rows), "region")
    out = format_aggregate(agg, "text")
    assert "EU" in out


def test_format_text_contains_header_line():
    rows = [_row("added", {"id": "1", "region": "EU"})]
    agg = aggregate_diff(_make_result(rows), "region")
    out = format_aggregate(agg, "text")
    assert "Added" in out and "Removed" in out and "Modified" in out


def test_format_json_empty():
    agg = aggregate_diff(_make_result([]), "region")
    out = format_aggregate(agg, "json")
    data = json.loads(out)
    assert data["column"] == "region"
    assert data["groups"] == []


def test_format_json_with_data():
    rows = [
        _row("added", {"id": "1", "region": "EU"}),
        _row("removed", {"id": "2", "region": "US"}),
    ]
    agg = aggregate_diff(_make_result(rows), "region")
    out = format_aggregate(agg, "json")
    data = json.loads(out)
    keys = {g["key"] for g in data["groups"]}
    assert keys == {"EU", "US"}


def test_format_default_is_text():
    agg = aggregate_diff(_make_result([]), "region")
    out = format_aggregate(agg)
    assert "No data" in out
