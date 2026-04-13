"""Tests for csv_diff_reporter.validator."""

from __future__ import annotations

import os
import stat
import pytest

from csv_diff_reporter.validator import (
    ValidationError,
    ValidationResult,
    validate_csv_extension,
    validate_file_path,
    validate_inputs,
)


# ---------------------------------------------------------------------------
# validate_file_path
# ---------------------------------------------------------------------------


def test_validate_file_path_ok(tmp_path):
    f = tmp_path / "data.csv"
    f.write_text("a,b\n1,2\n")
    assert validate_file_path(str(f)) is None


def test_validate_file_path_empty_string():
    assert validate_file_path("") is not None


def test_validate_file_path_missing():
    assert validate_file_path("/nonexistent/path/file.csv") is not None


def test_validate_file_path_directory(tmp_path):
    assert validate_file_path(str(tmp_path)) is not None


@pytest.mark.skipif(os.getuid() == 0, reason="root bypasses permission checks")
def test_validate_file_path_not_readable(tmp_path):
    f = tmp_path / "locked.csv"
    f.write_text("a,b\n")
    f.chmod(0o000)
    try:
        assert validate_file_path(str(f)) is not None
    finally:
        f.chmod(stat.S_IRUSR | stat.S_IWUSR)


# ---------------------------------------------------------------------------
# validate_csv_extension
# ---------------------------------------------------------------------------


def test_validate_csv_extension_ok():
    assert validate_csv_extension("report.csv") is None


def test_validate_csv_extension_uppercase():
    assert validate_csv_extension("REPORT.CSV") is None


def test_validate_csv_extension_wrong():
    assert validate_csv_extension("report.txt") is not None


# ---------------------------------------------------------------------------
# validate_inputs
# ---------------------------------------------------------------------------


def test_validate_inputs_both_valid(tmp_path):
    old = tmp_path / "old.csv"
    new = tmp_path / "new.csv"
    old.write_text("a,b\n1,2\n")
    new.write_text("a,b\n3,4\n")
    result = validate_inputs(str(old), str(new))
    assert result.valid is True
    assert result.errors == []
    assert bool(result) is True


def test_validate_inputs_old_missing(tmp_path):
    new = tmp_path / "new.csv"
    new.write_text("a,b\n")
    result = validate_inputs("/no/such/old.csv", str(new))
    assert not result
    assert any("old" in e for e in result.errors)


def test_validate_inputs_both_missing():
    result = validate_inputs("/no/old.csv", "/no/new.csv")
    assert not result
    assert len(result.errors) == 2


def test_validate_inputs_wrong_extension(tmp_path):
    old = tmp_path / "old.txt"
    new = tmp_path / "new.txt"
    old.write_text("a,b\n")
    new.write_text("a,b\n")
    result = validate_inputs(str(old), str(new))
    assert not result
    assert len(result.errors) == 2


def test_validate_inputs_skip_extension_check(tmp_path):
    old = tmp_path / "old.txt"
    new = tmp_path / "new.txt"
    old.write_text("a,b\n")
    new.write_text("a,b\n")
    result = validate_inputs(str(old), str(new), require_csv_extension=False)
    assert result.valid is True
