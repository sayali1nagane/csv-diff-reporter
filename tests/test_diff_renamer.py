"""Tests for csv_diff_reporter.diff_renamer and cli_rename_keys."""
from __future__ import annotations

import argparse

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_renamer import (
    KeyRenameOptions,
    format_rename_notice,
    rename_keys,
)
from csv_diff_reporter.cli_rename_keys import (
    add_rename_key_args,
    apply_rename_keys,
    build_rename_key_options,
    render_rename_notice,
)


def _row(key: str, change_type: str = "added") -> RowDiff:
    return RowDiff(
        key=key,
        change_type=change_type,
        old_fields={},
        new_fields={"col": "val"},
    )


def _result(*keys: str) -> DiffResult:
    return DiffResult(
        headers=["col"],
        rows=[_row(k) for k in keys],
    )


# ---------------------------------------------------------------------------
# rename_keys
# ---------------------------------------------------------------------------

def test_rename_keys_no_options_returns_same_object():
    result = _result("a", "b")
    assert rename_keys(result) is result


def test_rename_keys_empty_mapping_returns_same_object():
    result = _result("a", "b")
    assert rename_keys(result, KeyRenameOptions(mapping={})) is result


def test_rename_keys_renames_matching_key():
    result = _result("old_key", "other")
    opts = KeyRenameOptions(mapping={"old_key": "new_key"})
    renamed = rename_keys(result, opts)
    keys = [r.key for r in renamed.rows]
    assert "new_key" in keys
    assert "old_key" not in keys


def test_rename_keys_passthrough_leaves_unmapped_keys():
    result = _result("a", "b")
    opts = KeyRenameOptions(mapping={"a": "alpha"}, passthrough=True)
    renamed = rename_keys(result, opts)
    keys = [r.key for r in renamed.rows]
    assert "alpha" in keys
    assert "b" in keys


def test_rename_keys_strict_raises_for_unmapped_key():
    result = _result("a", "b")
    opts = KeyRenameOptions(mapping={"a": "alpha"}, passthrough=False)
    with pytest.raises(ValueError, match="passthrough is disabled"):
        rename_keys(result, opts)


def test_rename_keys_preserves_headers_and_change_type():
    result = _result("x")
    result.rows[0] = RowDiff(key="x", change_type="removed", old_fields={"col": "v"}, new_fields={})
    opts = KeyRenameOptions(mapping={"x": "y"})
    renamed = rename_keys(result, opts)
    assert renamed.headers == ["col"]
    assert renamed.rows[0].change_type == "removed"


# ---------------------------------------------------------------------------
# format_rename_notice
# ---------------------------------------------------------------------------

def test_format_rename_notice_empty_mapping():
    opts = KeyRenameOptions(mapping={})
    assert format_rename_notice(opts) == "No key renames applied."


def test_format_rename_notice_lists_renames():
    opts = KeyRenameOptions(mapping={"a": "alpha", "b": "beta"})
    notice = format_rename_notice(opts)
    assert "'a' -> 'alpha'" in notice
    assert "'b' -> 'beta'" in notice


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    add_rename_key_args(p)
    return p


def test_add_rename_key_args_registers_rename_key():
    p = _parser()
    args = p.parse_args(["--rename-key", "old=new"])
    assert args.rename_keys == ["old=new"]


def test_add_rename_key_args_strict_default_false():
    p = _parser()
    args = p.parse_args([])
    assert args.rename_key_strict is False


def test_build_rename_key_options_returns_none_when_no_keys():
    p = _parser()
    args = p.parse_args([])
    assert build_rename_key_options(args) is None


def test_build_rename_key_options_parses_mapping():
    p = _parser()
    args = p.parse_args(["--rename-key", "foo=bar"])
    opts = build_rename_key_options(args)
    assert opts is not None
    assert opts.mapping == {"foo": "bar"}


def test_apply_rename_keys_no_args_returns_same_object():
    p = _parser()
    args = p.parse_args([])
    result = _result("x")
    assert apply_rename_keys(result, args) is result


def test_render_rename_notice_empty_when_no_renames():
    p = _parser()
    args = p.parse_args([])
    assert render_rename_notice(args) == ""


def test_render_rename_notice_contains_mapping():
    p = _parser()
    args = p.parse_args(["--rename-key", "old=new"])
    notice = render_rename_notice(args)
    assert "old" in notice
    assert "new" in notice
