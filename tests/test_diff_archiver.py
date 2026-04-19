"""Tests for diff_archiver module."""
import json
from pathlib import Path

import pytest

from csv_diff_reporter.diff_archiver import (
    ArchiveError,
    ArchiveOptions,
    archive_diff,
)
from csv_diff_reporter.differ import DiffResult, RowDiff


def _empty_result() -> DiffResult:
    return DiffResult(headers=["id", "name"], rows=[])


def _row(key="1", change="added"):
    return RowDiff(key=key, change_type=change,
                   old_fields={}, new_fields={"id": "1", "name": "Alice"})


def test_archive_creates_directory(tmp_path):
    opts = ArchiveOptions(base_dir=str(tmp_path / "arch"), formats=["text"])
    entry = archive_diff(_empty_result(), opts)
    assert Path(entry.path).is_dir()


def test_archive_writes_text_file(tmp_path):
    opts = ArchiveOptions(base_dir=str(tmp_path), formats=["text"])
    entry = archive_diff(_empty_result(), opts)
    txt = list(Path(entry.path).glob("*.txt"))
    assert len(txt) == 1


def test_archive_writes_json_file(tmp_path):
    opts = ArchiveOptions(base_dir=str(tmp_path), formats=["json"])
    entry = archive_diff(_empty_result(), opts)
    files = list(Path(entry.path).glob("*.json"))
    # meta.json + diff.json
    assert any(f.name == "diff.json" for f in files)


def test_archive_writes_meta_json(tmp_path):
    opts = ArchiveOptions(base_dir=str(tmp_path), label="run1", formats=["text"])
    entry = archive_diff(_empty_result(), opts)
    meta = json.loads((Path(entry.path) / "meta.json").read_text())
    assert meta["label"] == "run1"
    assert "text" in meta["formats"]
    assert "timestamp" in meta


def test_archive_entry_as_dict(tmp_path):
    opts = ArchiveOptions(base_dir=str(tmp_path), label="x", formats=["text"])
    entry = archive_diff(_empty_result(), opts)
    d = entry.as_dict()
    assert d["label"] == "x"
    assert isinstance(d["formats"], list)


def test_archive_label_in_path(tmp_path):
    opts = ArchiveOptions(base_dir=str(tmp_path), label="mylabel", formats=["text"])
    entry = archive_diff(_empty_result(), opts)
    assert "mylabel" in entry.path


def test_archive_multiple_formats(tmp_path):
    opts = ArchiveOptions(base_dir=str(tmp_path), formats=["text", "json", "markdown"])
    entry = archive_diff(_empty_result(), opts)
    assert set(entry.formats) == {"text", "json", "markdown"}
    files = {f.name for f in Path(entry.path).iterdir()}
    assert "diff.txt" in files
    assert "diff.json" in files
    assert "diff.md" in files


def test_archive_raises_on_unwritable_dir(tmp_path):
    bad = tmp_path / "locked"
    bad.mkdir()
    bad.chmod(0o444)
    opts = ArchiveOptions(base_dir=str(bad / "sub"), formats=["text"])
    try:
        with pytest.raises(ArchiveError):
            archive_diff(_empty_result(), opts)
    finally:
        bad.chmod(0o755)
