"""Tests for csv_diff_reporter.cli_transform."""
import argparse

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.cli_transform import (
    add_transform_args,
    apply_transform,
    render_transform_notice,
)


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    add_transform_args(p)
    return p


def _result(*rows) -> DiffResult:
    return DiffResult(headers=["id", "name"], rows=list(rows))


def _row(change_type, key, new=None, old=None) -> RowDiff:
    return RowDiff(change_type=change_type, key=key,
                   old_fields=old or {}, new_fields=new or {})


def test_add_transform_args_registers_transform_flag():
    p = _parser()
    args = p.parse_args([])
    assert hasattr(args, "transform")


def test_add_transform_args_registers_transform_default_flag():
    p = _parser()
    args = p.parse_args([])
    assert hasattr(args, "transform_default")


def test_add_transform_args_default_transform_is_none():
    p = _parser()
    args = p.parse_args([])
    assert args.transform_default is None


def test_apply_transform_no_flags_returns_same_result():
    p = _parser()
    args = p.parse_args([])
    result = _result()
    tr = apply_transform(result, args)
    assert tr.result is result


def test_apply_transform_upper_flag_transforms_column():
    p = _parser()
    args = p.parse_args(["--transform", "name:upper"])
    row = _row("added", "1", new={"id": "1", "name": "alice"})
    result = _result(row)
    tr = apply_transform(result, args)
    assert tr.result.rows[0].new_fields["name"] == "ALICE"


def test_apply_transform_unknown_fn_is_ignored():
    p = _parser()
    args = p.parse_args(["--transform", "name:nonexistent"])
    row = _row("added", "1", new={"id": "1", "name": "alice"})
    result = _result(row)
    tr = apply_transform(result, args)
    # nonexistent fn is skipped → no transform applied → same value
    assert tr.result.rows[0].new_fields["name"] == "alice"


def test_apply_transform_default_flag_applies_to_all():
    p = _parser()
    args = p.parse_args(["--transform-default", "upper"])
    row = _row("added", "2", new={"id": "2", "name": "bob"})
    result = _result(row)
    tr = apply_transform(result, args)
    assert tr.result.rows[0].new_fields["name"] == "BOB"


def test_render_transform_notice_text_no_transforms():
    p = _parser()
    args = p.parse_args([])
    result = _result()
    tr = apply_transform(result, args)
    notice = render_transform_notice(tr, fmt="text")
    assert "No transformations" in notice


def test_render_transform_notice_text_with_column():
    p = _parser()
    args = p.parse_args(["--transform", "name:lower"])
    result = _result()
    tr = apply_transform(result, args)
    notice = render_transform_notice(tr, fmt="text")
    assert "name" in notice


def test_render_transform_notice_json_format():
    import json
    p = _parser()
    args = p.parse_args(["--transform", "name:strip"])
    result = _result()
    tr = apply_transform(result, args)
    notice = render_transform_notice(tr, fmt="json")
    data = json.loads(notice)
    assert "columns_affected" in data
    assert "name" in data["columns_affected"]
