"""Tests for csv_diff_reporter.cli_snapshot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.cli_snapshot import (
    add_snapshot_args,
    apply_load_snapshot,
    apply_save_snapshot,
    render_snapshot_notice,
)


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    add_snapshot_args(p)
    return p


def _empty_diff() -> DiffResult:
    return DiffResult(headers=["id"], rows=[])


def _row(key="1") -> RowDiff:
    return RowDiff(key=key, change_type="added", old_fields={}, new_fields={"id": key})


def test_add_snapshot_args_registers_save_flag():
    p = _parser()
    args = p.parse_args([])
    assert args.save_snapshot is None


def test_add_snapshot_args_registers_load_flag():
    p = _parser()
    args = p.parse_args([])
    assert args.load_snapshot is None


def test_add_snapshot_args_registers_label_flag():
    p = _parser()
    args = p.parse_args(["--snapshot-label", "v2"])
    assert args.snapshot_label == "v2"


def test_apply_save_snapshot_returns_none_when_not_set():
    args = _parser().parse_args([])
    result = apply_save_snapshot(_empty_diff(), args)
    assert result is None


def test_apply_save_snapshot_creates_file(tmp_path):
    snap = tmp_path / "out.json"
    args = _parser().parse_args(["--save-snapshot", str(snap)])
    returned = apply_save_snapshot(_empty_diff(), args)
    assert returned == snap
    assert snap.exists()


def test_apply_save_snapshot_stores_label(tmp_path):
    snap = tmp_path / "out.json"
    args = _parser().parse_args(
        ["--save-snapshot", str(snap), "--snapshot-label", "beta"]
    )
    apply_save_snapshot(_empty_diff(), args)
    payload = json.loads(snap.read_text())
    assert payload["label"] == "beta"


def test_apply_load_snapshot_returns_original_when_not_set():
    args = _parser().parse_args([])
    diff = _empty_diff()
    assert apply_load_snapshot(diff, args) is diff


def test_apply_load_snapshot_returns_loaded_diff(tmp_path):
    snap = tmp_path / "snap.json"
    original = DiffResult(headers=["id", "val"], rows=[_row("99")])
    save_args = _parser().parse_args(["--save-snapshot", str(snap)])
    apply_save_snapshot(original, save_args)

    load_args = _parser().parse_args(["--load-snapshot", str(snap)])
    loaded = apply_load_snapshot(_empty_diff(), load_args)
    assert loaded.headers == ["id", "val"]
    assert loaded.rows[0].key == "99"


def test_apply_load_snapshot_exits_on_missing_file(tmp_path):
    args = _parser().parse_args(
        ["--load-snapshot", str(tmp_path / "ghost.json")]
    )
    with pytest.raises(SystemExit):
        apply_load_snapshot(_empty_diff(), args)


def test_render_snapshot_notice_none_returns_empty():
    assert render_snapshot_notice(None) == ""


def test_render_snapshot_notice_contains_path(tmp_path):
    p = tmp_path / "snap.json"
    notice = render_snapshot_notice(p)
    assert str(p) in notice
