"""Tests for csv_diff_reporter.cli_row_limit."""
import argparse
import sys

import pytest

from csv_diff_reporter.cli_row_limit import add_row_limit_args, apply_row_limit_from_args


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    add_row_limit_args(p)
    return p


def _data(n: int):
    return {str(i): [{"id": str(i)}] for i in range(n)}


# ---------------------------------------------------------------------------
# add_row_limit_args
# ---------------------------------------------------------------------------

def test_add_row_limit_args_registers_max_rows():
    p = _parser()
    args = p.parse_args([])
    assert args.max_rows is None


def test_add_row_limit_args_parses_value():
    p = _parser()
    args = p.parse_args(["--max-rows", "50"])
    assert args.max_rows == 50


def test_add_row_limit_args_no_warning_flag_default_false():
    p = _parser()
    args = p.parse_args([])
    assert args.no_row_limit_warning is False


def test_add_row_limit_args_no_warning_flag_set():
    p = _parser()
    args = p.parse_args(["--no-row-limit-warning"])
    assert args.no_row_limit_warning is True


# ---------------------------------------------------------------------------
# apply_row_limit_from_args
# ---------------------------------------------------------------------------

def test_apply_no_limit_returns_all(capsys):
    p = _parser()
    args = p.parse_args([])
    data = _data(5)
    result = apply_row_limit_from_args(args, data)
    assert len(result) == 5
    captured = capsys.readouterr()
    assert captured.err == ""


def test_apply_limit_truncates(capsys):
    p = _parser()
    args = p.parse_args(["--max-rows", "3"])
    data = _data(8)
    result = apply_row_limit_from_args(args, data)
    assert len(result) == 3


def test_apply_limit_prints_warning_to_stderr(capsys):
    p = _parser()
    args = p.parse_args(["--max-rows", "2"])
    data = _data(5)
    apply_row_limit_from_args(args, data)
    captured = capsys.readouterr()
    assert "Warning" in captured.err


def test_apply_limit_suppresses_warning(capsys):
    p = _parser()
    args = p.parse_args(["--max-rows", "2", "--no-row-limit-warning"])
    data = _data(5)
    apply_row_limit_from_args(args, data)
    captured = capsys.readouterr()
    assert captured.err == ""
