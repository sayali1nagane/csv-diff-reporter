import json
import pytest
from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_profiler import profile_diff, ProfileResult
from csv_diff_reporter.diff_profiler_formatter import format_profile


HEADERS = ["id", "name", "status"]


def _row(key, old, new):
    return RowDiff(key=key, old_fields=old, new_fields=new)


def _result(added=(), removed=(), modified=()):
    return DiffResult(headers=HEADERS, added=list(added), removed=list(removed), modified=list(modified))


def test_profile_empty_result():
    r = profile_diff(_result())
    assert isinstance(r, ProfileResult)
    assert r.profiles == {}
    assert r.headers == HEADERS


def test_profile_added_rows_counted():
    rows = [
        _row("1", None, {"id": "1", "name": "Alice", "status": "active"}),
        _row("2", None, {"id": "2", "name": "Bob", "status": "active"}),
    ]
    r = profile_diff(_result(added=rows))
    assert r.get("status") is not None
    assert r.get("status").total_values == 2
    assert r.get("status").unique_values == 1
    assert r.get("status").top_values[0] == ("active", 2)


def test_profile_top_n_respected():
    rows = [_row(str(i), None, {"id": str(i), "name": f"n{i}", "status": "x"}) for i in range(10)]
    r = profile_diff(_result(added=rows), top_n=3)
    assert len(r.get("name").top_values) <= 3


def test_profile_mixed_change_types():
    added = [_row("1", None, {"id": "1", "name": "A", "status": "on"})]
    removed = [_row("2", {"id": "2", "name": "B", "status": "off"}, None)]
    modified = [_row("3", {"id": "3", "name": "C", "status": "on"}, {"id": "3", "name": "C2", "status": "off"})]
    r = profile_diff(_result(added=added, removed=removed, modified=modified))
    assert r.get("status").total_values == 3


def test_as_dict_structure():
    rows = [_row("1", None, {"id": "1", "name": "Alice", "status": "active"})]
    r = profile_diff(_result(added=rows))
    d = r.as_dict()
    assert "headers" in d
    assert "profiles" in d
    assert "top_values" in d["profiles"]["id"]


def test_format_text_empty():
    r = profile_diff(_result())
    out = format_profile(r, fmt="text")
    assert "No profile data" in out


def test_format_text_with_data():
    rows = [_row("1", None, {"id": "1", "name": "Alice", "status": "active"})]
    r = profile_diff(_result(added=rows))
    out = format_profile(r, fmt="text")
    assert "Column: id" in out
    assert "Total values" in out


def test_format_json_valid():
    rows = [_row("1", None, {"id": "1", "name": "Alice", "status": "active"})]
    r = profile_diff(_result(added=rows))
    out = format_profile(r, fmt="json")
    parsed = json.loads(out)
    assert "profiles" in parsed
