"""Tests for csv_diff_reporter.cli_schema helpers."""
from __future__ import annotations

import argparse
import sys
from unittest.mock import patch

import pytest

from csv_diff_reporter.cli_schema import add_schema_args, apply_schema_validation
from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.schema import SchemaValidationResult


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _empty_diff() -> DiffResult:
    return DiffResult(added=[], removed=[], modified=[], unchanged=[])


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"schema": None, "schema_strict": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# ---------------------------------------------------------------------------
# add_schema_args
# ---------------------------------------------------------------------------

def test_add_schema_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_schema_args(parser)
    args = parser.parse_args([])
    assert args.schema is None
    assert args.schema_strict is False


def test_add_schema_args_schema_flag():
    parser = argparse.ArgumentParser()
    add_schema_args(parser)
    args = parser.parse_args(["--schema", "schema.toml"])
    assert args.schema == "schema.toml"


def test_add_schema_args_strict_flag():
    parser = argparse.ArgumentParser()
    add_schema_args(parser)
    args = parser.parse_args(["--schema-strict"])
    assert args.schema_strict is True


# ---------------------------------------------------------------------------
# apply_schema_validation — no schema
# ---------------------------------------------------------------------------

def test_apply_schema_no_schema_returns_valid():
    args = _make_args()
    result = apply_schema_validation(args, ["id", "name"], _empty_diff())
    assert result.is_valid()


# ---------------------------------------------------------------------------
# apply_schema_validation — with schema file
# ---------------------------------------------------------------------------

def test_apply_schema_valid_spec(tmp_path):
    schema_file = tmp_path / "schema.toml"
    schema_file.write_text('[columns.id]\nrequired = true\ntype = "int"\n')
    args = _make_args(schema=str(schema_file))
    diff = DiffResult(
        added=[RowDiff(key="1", old_row=None, new_row={"id": "42"})],
        removed=[], modified=[], unchanged=[],
    )
    result = apply_schema_validation(args, ["id"], diff)
    assert result.is_valid()


def test_apply_schema_strict_exits_on_error(tmp_path):
    schema_file = tmp_path / "schema.toml"
    schema_file.write_text('[columns.id]\nrequired = true\ntype = "int"\n')
    args = _make_args(schema=str(schema_file), schema_strict=True)
    diff = DiffResult(
        added=[RowDiff(key="x", old_row=None, new_row={"id": "not-int"})],
        removed=[], modified=[], unchanged=[],
    )
    with pytest.raises(SystemExit) as exc_info:
        apply_schema_validation(args, ["id"], diff)
    assert exc_info.value.code == 2


def test_apply_schema_missing_file_exits(tmp_path):
    args = _make_args(schema=str(tmp_path / "missing.toml"))
    with pytest.raises(SystemExit) as exc_info:
        apply_schema_validation(args, [], _empty_diff())
    assert exc_info.value.code == 1
