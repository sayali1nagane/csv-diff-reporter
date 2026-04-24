"""Tests for csv_diff_reporter.diff_snapshot."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_snapshot import (
    SnapshotError,
    SnapshotOptions,
    load_snapshot,
    save_snapshot,
    snapshot_label,
)


def _row(key="1", change_type="added") -> RowDiff:
    return RowDiff(
        key=key,
        change_type=change_type,
        old_fields={},
        new_fields={"name": "Alice"},
    )


def _result(*rows: RowDiff) -> DiffResult:
    return DiffResult(headers=["id", "name"], rows=list(rows))


def test_save_snapshot_creates_file(tmp_path):
    path = tmp_path / "snap.json"
    opts = SnapshotOptions(path=path, label="v1")
    returned = save_snapshot(_result(_row()), opts)
    assert returned == path
    assert path.exists()


def test_save_snapshot_content_is_valid_json(tmp_path):
    path = tmp_path / "snap.json"
    opts = SnapshotOptions(path=path)
    save_snapshot(_result(_row(key="2", change_type="removed")), opts)
    payload = json.loads(path.read_text())
    assert payload["headers"] == ["id", "name"]
    assert len(payload["rows"]) == 1
    assert payload["rows"][0]["change_type"] == "removed"


def test_save_snapshot_stores_label(tmp_path):
    path = tmp_path / "snap.json"
    opts = SnapshotOptions(path=path, label="release-42")
    save_snapshot(_result(), opts)
    payload = json.loads(path.read_text())
    assert payload["label"] == "release-42"


def test_save_snapshot_creates_parent_dirs(tmp_path):
    path = tmp_path / "nested" / "deep" / "snap.json"
    opts = SnapshotOptions(path=path)
    save_snapshot(_result(), opts)
    assert path.exists()


def test_save_snapshot_raises_on_unwritable(tmp_path):
    path = tmp_path / "snap.json"
    path.parent.chmod(0o444)
    opts = SnapshotOptions(path=path / "sub" / "snap.json")
    with pytest.raises(SnapshotError):
        save_snapshot(_result(), opts)
    path.parent.chmod(0o755)


def test_load_snapshot_round_trips(tmp_path):
    path = tmp_path / "snap.json"
    original = _result(_row("1", "added"), _row("2", "modified"))
    save_snapshot(original, SnapshotOptions(path=path))
    loaded = load_snapshot(path)
    assert loaded.headers == original.headers
    assert len(loaded.rows) == 2
    assert loaded.rows[0].key == "1"
    assert loaded.rows[1].change_type == "modified"


def test_load_snapshot_raises_when_missing(tmp_path):
    with pytest.raises(SnapshotError, match="not found"):
        load_snapshot(tmp_path / "ghost.json")


def test_load_snapshot_raises_on_corrupt_json(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("not json", encoding="utf-8")
    with pytest.raises(SnapshotError, match="Cannot read"):
        load_snapshot(path)


def test_snapshot_label_returns_label(tmp_path):
    path = tmp_path / "snap.json"
    save_snapshot(_result(), SnapshotOptions(path=path, label="my-label"))
    assert snapshot_label(path) == "my-label"


def test_snapshot_label_returns_none_for_empty_label(tmp_path):
    path = tmp_path / "snap.json"
    save_snapshot(_result(), SnapshotOptions(path=path, label=""))
    assert snapshot_label(path) is None


def test_snapshot_label_returns_none_for_missing_file(tmp_path):
    assert snapshot_label(tmp_path / "missing.json") is None
