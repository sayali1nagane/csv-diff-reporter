"""Tests for cli_html."""
import argparse
from pathlib import Path

import pytest

from csv_diff_reporter.cli_html import add_html_args, apply_html_export
from csv_diff_reporter.differ import DiffResult, RowDiff


def _parser():
    p = argparse.ArgumentParser()
    add_html_args(p)
    return p


def _make_result():
    return DiffResult(headers=["id", "val"], rows=[])


def test_add_html_args_registers_html_flag():
    p = _parser()
    args = p.parse_args([])
    assert args.html is None


def test_add_html_args_parses_html_path():
    p = _parser()
    args = p.parse_args(["--html", "out/report.html"])
    assert args.html == "out/report.html"


def test_add_html_args_default_title():
    p = _parser()
    args = p.parse_args([])
    assert args.html_title == "CSV Diff Report"


def test_add_html_args_custom_title():
    p = _parser()
    args = p.parse_args(["--html-title", "My Diff"])
    assert args.html_title == "My Diff"


def test_apply_html_export_no_flag_does_nothing(tmp_path):
    p = _parser()
    args = p.parse_args([])
    apply_html_export(args, _make_result())  # should not raise


def test_apply_html_export_writes_file(tmp_path):
    output = tmp_path / "report.html"
    p = _parser()
    args = p.parse_args(["--html", str(output)])
    apply_html_export(args, _make_result())
    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content


def test_apply_html_export_creates_parent_dirs(tmp_path):
    output = tmp_path / "nested" / "dir" / "report.html"
    p = _parser()
    args = p.parse_args(["--html", str(output)])
    apply_html_export(args, _make_result())
    assert output.exists()


def test_apply_html_export_uses_custom_title(tmp_path):
    output = tmp_path / "report.html"
    p = _parser()
    args = p.parse_args(["--html", str(output), "--html-title", "Special Title"])
    apply_html_export(args, _make_result())
    content = output.read_text(encoding="utf-8")
    assert "Special Title" in content
