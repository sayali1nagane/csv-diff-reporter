"""Tests for csv_diff_reporter.cli_split."""
from __future__ import annotations

import argparse

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.cli_split import (
    add_split_args,
    apply_split,
    build_split_options,
    render_split_notice,
)


HEADERS = ["id", "val"]


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    add_split_args(p)
    return p


def _row(key: str, ct: str) -> RowDiff:
    return RowDiff(key=key, change_type=ct, old_row={}, new_row={"id": key, "val": "x"})


def _result(n: int = 3) -> DiffResult:
    return DiffResult(headers=HEADERS, rows=[_row(str(i), "added") for i in range(n)])


# ---------------------------------------------------------------------------
# add_split_args
# ---------------------------------------------------------------------------

def test_add_split_args_registers_split_size():
    args = _parser().parse_args([])
    assert hasattr(args, "split_size")
    assert args.split_size is None


def test_add_split_args_registers_split_by_type():
    args = _parser().parse_args([])
    assert hasattr(args, "split_by_type")
    assert args.split_by_type is False


def test_add_split_args_parses_size():
    args = _parser().parse_args(["--split-size", "10"])
    assert args.split_size == 10


def test_add_split_args_parses_by_type():
    args = _parser().parse_args(["--split-by-type"])
    assert args.split_by_type is True


# ---------------------------------------------------------------------------
# build_split_options
# ---------------------------------------------------------------------------

def test_build_split_options_none_when_no_flags():
    args = _parser().parse_args([])
    assert build_split_options(args) is None


def test_build_split_options_with_size():
    args = _parser().parse_args(["--split-size", "5"])
    opts = build_split_options(args)
    assert opts is not None
    assert opts.chunk_size == 5
    assert opts.by_type is False


def test_build_split_options_with_by_type():
    args = _parser().parse_args(["--split-by-type"])
    opts = build_split_options(args)
    assert opts is not None
    assert opts.by_type is True


# ---------------------------------------------------------------------------
# apply_split
# ---------------------------------------------------------------------------

def test_apply_split_no_flags_single_chunk():
    args = _parser().parse_args([])
    split = apply_split(_result(4), args)
    assert split.count == 1


def test_apply_split_with_size_produces_chunks():
    args = _parser().parse_args(["--split-size", "2"])
    split = apply_split(_result(4), args)
    assert split.count == 2


# ---------------------------------------------------------------------------
# render_split_notice
# ---------------------------------------------------------------------------

def test_render_split_notice_empty_when_single_chunk():
    args = _parser().parse_args([])
    split = apply_split(_result(3), args)
    assert render_split_notice(split) == ""


def test_render_split_notice_contains_chunk_count():
    args = _parser().parse_args(["--split-size", "1"])
    split = apply_split(_result(3), args)
    notice = render_split_notice(split)
    assert "3 chunks" in notice
