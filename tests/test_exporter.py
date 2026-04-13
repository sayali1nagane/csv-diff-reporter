"""Tests for csv_diff_reporter.exporter."""

from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.exporter import (
    export,
    export_to_file,
    export_to_stdout,
    ExportError,
)


def _make_result() -> DiffResult:
    return DiffResult(added=[], removed=[], modified=[])


# ---------------------------------------------------------------------------
# export_to_file
# ---------------------------------------------------------------------------

def test_export_to_file_creates_file(tmp_path: Path) -> None:
    dest = tmp_path / "out" / "report.txt"
    export_to_file("hello", dest)
    assert dest.read_text(encoding="utf-8") == "hello"


def test_export_to_file_creates_parent_dirs(tmp_path: Path) -> None:
    dest = tmp_path / "a" / "b" / "c" / "report.json"
    export_to_file("{}", dest)
    assert dest.exists()


def test_export_to_file_raises_on_unwritable(tmp_path: Path) -> None:
    dest = tmp_path / "report.txt"
    dest.mkdir()  # make it a directory so write_text fails
    with pytest.raises(ExportError, match="Cannot write to"):
        export_to_file("data", dest)


# ---------------------------------------------------------------------------
# export_to_stdout
# ---------------------------------------------------------------------------

def test_export_to_stdout_writes_content(capsys) -> None:
    export_to_stdout("line one")
    captured = capsys.readouterr()
    assert "line one" in captured.out


def test_export_to_stdout_appends_newline_if_missing(capsys) -> None:
    export_to_stdout("no newline")
    captured = capsys.readouterr()
    assert captured.out.endswith("\n")


def test_export_to_stdout_does_not_double_newline(capsys) -> None:
    export_to_stdout("already\n")
    captured = capsys.readouterr()
    assert captured.out == "already\n"


# ---------------------------------------------------------------------------
# export (integration)
# ---------------------------------------------------------------------------

def test_export_stdout_default_fmt(capsys) -> None:
    export(_make_result())
    captured = capsys.readouterr()
    assert captured.out  # something was written


def test_export_to_path(tmp_path: Path) -> None:
    dest = tmp_path / "report.json"
    export(_make_result(), fmt="json", output_path=dest)
    assert dest.exists()
    content = dest.read_text(encoding="utf-8")
    assert content.strip()  # non-empty


def test_export_markdown_to_path(tmp_path: Path) -> None:
    dest = tmp_path / "report.md"
    export(_make_result(), fmt="markdown", output_path=dest)
    text = dest.read_text(encoding="utf-8")
    assert "#" in text or "No differences" in text
