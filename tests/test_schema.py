"""Tests for csv_diff_reporter.schema and csv_diff_reporter.schema_loader."""
from __future__ import annotations

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.schema import (
    ColumnSchema,
    SchemaError,
    SchemaValidationResult,
    validate_diff_values,
    validate_headers,
)
from csv_diff_reporter.schema_loader import SchemaLoadError, load_schema, schema_from_dict


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _result(**kwargs) -> DiffResult:
    defaults = dict(added=[], removed=[], modified=[], unchanged=[])
    defaults.update(kwargs)
    return DiffResult(**defaults)


def _added(row: dict) -> RowDiff:
    return RowDiff(key="k", old_row=None, new_row=row)


def _modified(old: dict, new: dict) -> RowDiff:
    return RowDiff(key="k", old_row=old, new_row=new)


# ---------------------------------------------------------------------------
# SchemaValidationResult bool
# ---------------------------------------------------------------------------

def test_schema_result_true_when_no_errors():
    r = SchemaValidationResult()
    assert bool(r) is True
    assert r.is_valid()


def test_schema_result_false_when_errors():
    r = SchemaValidationResult(errors=[SchemaError("col", "bad")])
    assert bool(r) is False


def test_schema_result_has_warnings():
    r = SchemaValidationResult(warnings=[SchemaError("col", "warn")])
    assert r.has_warnings()


# ---------------------------------------------------------------------------
# validate_headers
# ---------------------------------------------------------------------------

def test_validate_headers_all_present():
    spec = {"id": ColumnSchema(required=True), "name": ColumnSchema(required=True)}
    result = validate_headers(["id", "name", "extra"], spec)
    assert result.is_valid()
    assert not result.has_warnings()


def test_validate_headers_missing_required():
    spec = {"id": ColumnSchema(required=True)}
    result = validate_headers(["name"], spec)
    assert not result.is_valid()
    assert any(e.column == "id" for e in result.errors)


def test_validate_headers_optional_missing_produces_warning():
    spec = {"score": ColumnSchema(required=False)}
    result = validate_headers(["id"], spec)
    assert result.is_valid()
    assert result.has_warnings()


# ---------------------------------------------------------------------------
# validate_diff_values
# ---------------------------------------------------------------------------

def test_validate_values_valid_int():
    spec = {"age": ColumnSchema(expected_type="int")}
    diff = _result(added=[_added({"age": "25"})])
    result = validate_diff_values(diff, spec)
    assert result.is_valid()


def test_validate_values_invalid_int():
    spec = {"age": ColumnSchema(expected_type="int")}
    diff = _result(added=[_added({"age": "not-a-number"})])
    result = validate_diff_values(diff, spec)
    assert not result.is_valid()
    assert any(e.column == "age" for e in result.errors)


def test_validate_values_max_length_exceeded():
    spec = {"code": ColumnSchema(max_length=3)}
    diff = _result(added=[_added({"code": "TOOLONG"})])
    result = validate_diff_values(diff, spec)
    assert not result.is_valid()


def test_validate_values_allowed_values_ok():
    spec = {"status": ColumnSchema(allowed_values=["active", "inactive"])}
    diff = _result(added=[_added({"status": "active"})])
    assert validate_diff_values(diff, spec).is_valid()


def test_validate_values_disallowed_value():
    spec = {"status": ColumnSchema(allowed_values=["active", "inactive"])}
    diff = _result(added=[_added({"status": "pending"})])
    result = validate_diff_values(diff, spec)
    assert not result.is_valid()


# ---------------------------------------------------------------------------
# schema_loader
# ---------------------------------------------------------------------------

def test_schema_from_dict_builds_spec():
    raw = {"columns": {"id": {"required": True, "type": "int"}}}
    spec = schema_from_dict(raw)
    assert "id" in spec
    assert spec["id"].required is True
    assert spec["id"].expected_type == "int"


def test_schema_from_dict_flat_format():
    raw = {"name": {"max_length": 50}}
    spec = schema_from_dict(raw)
    assert spec["name"].max_length == 50


def test_load_schema_returns_empty_for_none():
    assert load_schema(None) == {}


def test_load_schema_raises_for_missing_file(tmp_path):
    with pytest.raises(SchemaLoadError, match="not found"):
        load_schema(tmp_path / "nonexistent.toml")
