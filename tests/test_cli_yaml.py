"""Tests for csv_diff_reporter.cli_yaml."""
from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.cli_yaml import add_yaml_args, apply_yaml_export


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    add_yaml_args(p)
    return p


def _make_result() -> DiffResult:
    return DiffResult(headers=["id", "name"], rows=[])


# ---------------------------------------------------------------------------
# add_yaml_args
# ---------------------------------------------------------------------------

def test_add_yaml_args_registers_yaml_output():
    p = _parser()
    args = p.parse_args(["--yaml", "/tmp/out.yaml"])
    assert args.yaml_output == "/tmp/out.yaml"


def test_add_yaml_args_default_yaml_output_is_none():
    p = _parser()
    args = p.parse_args([])
    assert args.yaml_output is None


def test_add_yaml_args_registers_yaml_stdout():
    p = _parser()
    args = p.parse_args(["--yaml-stdout"])
    assert args.yaml_stdout is True


def test_add_yaml_args_default_yaml_stdout_is_false():
    p = _parser()
    args = p.parse_args([])
    assert args.yaml_stdout is False


# ---------------------------------------------------------------------------
# apply_yaml_export
# ---------------------------------------------------------------------------

def test_apply_yaml_export_returns_none_when_no_flags():
    p = _parser()
    args = p.parse_args([])
    result = apply_yaml_export(args, _make_result())
    assert result is None


def test_apply_yaml_export_returns_yaml_string_when_stdout_flag(tmp_path):
    p = _parser()
    args = p.parse_args(["--yaml-stdout"])
    output = apply_yaml_export(args, _make_result())
    assert output is not None
    assert "diff_report:" in output


def test_apply_yaml_export_writes_file(tmp_path):
    out_file = tmp_path / "report.yaml"
    p = _parser()
    args = p.parse_args(["--yaml", str(out_file)])
    apply_yaml_export(args, _make_result())
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "diff_report:" in content


def test_apply_yaml_export_creates_parent_dirs(tmp_path):
    out_file = tmp_path / "nested" / "deep" / "report.yaml"
    p = _parser()
    args = p.parse_args(["--yaml", str(out_file)])
    apply_yaml_export(args, _make_result())
    assert out_file.exists()


def test_apply_yaml_export_file_and_stdout_both_work(tmp_path):
    out_file = tmp_path / "report.yaml"
    p = _parser()
    args = p.parse_args(["--yaml", str(out_file), "--yaml-stdout"])
    output = apply_yaml_export(args, _make_result())
    assert output is not None
    assert out_file.exists()
