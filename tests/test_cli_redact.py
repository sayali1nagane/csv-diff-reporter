"""Tests for csv_diff_reporter.cli_redact."""
import argparse
import pytest
from csv_diff_reporter.cli_redact import add_redact_args, build_redact_options, apply_redact
from csv_diff_reporter.differ import DiffResult, RowDiff


def _parser():
    p = argparse.ArgumentParser()
    add_redact_args(p)
    return p


def _result():
    row = RowDiff(key="1", change_type="added", old_fields=None,
                 new_fields={"id": "1", "email": "x@y.com"})
    return DiffResult(headers=["id", "email"], rows=[row])


def test_add_redact_args_registers_columns_flag():
    p = _parser()
    args = p.parse_args(["--redact-columns", "email"])
    assert args.redact_columns == ["email"]


def test_add_redact_args_registers_mask_flag():
    p = _parser()
    args = p.parse_args(["--redact-columns", "email", "--redact-mask", "HIDDEN"])
    assert args.redact_mask == "HIDDEN"


def test_add_redact_args_defaults():
    p = _parser()
    args = p.parse_args([])
    assert args.redact_columns == []
    assert args.redact_mask == "***"


def test_build_redact_options_returns_none_when_no_columns():
    p = _parser()
    args = p.parse_args([])
    assert build_redact_options(args) is None


def test_build_redact_options_returns_options_with_columns():
    p = _parser()
    args = p.parse_args(["--redact-columns", "email", "name"])
    opts = build_redact_options(args)
    assert opts is not None
    assert "email" in opts.columns
    assert "name" in opts.columns


def test_apply_redact_masks_column():
    p = _parser()
    args = p.parse_args(["--redact-columns", "email"])
    r = _result()
    out = apply_redact(r, args)
    assert out.rows[0].new_fields["email"] == "***"


def test_apply_redact_no_columns_returns_same():
    p = _parser()
    args = p.parse_args([])
    r = _result()
    assert apply_redact(r, args) is r
