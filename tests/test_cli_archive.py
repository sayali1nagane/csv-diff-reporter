"""Tests for cli_archive module."""
import argparse
from pathlib import Path

import pytest

from csv_diff_reporter.cli_archive import (
    add_archive_args,
    apply_archive,
    build_archive_options,
    render_archive_notice,
)
from csv_diff_reporter.diff_archiver import ArchiveEntry
from csv_diff_reporter.differ import DiffResult


def _parser():
    p = argparse.ArgumentParser()
    add_archive_args(p)
    return p


def _empty_result():
    return DiffResult(headers=["id"], rows=[])


def test_add_archive_args_registers_dir():
    p = _parser()
    args = p.parse_args([])
    assert hasattr(args, "archive_dir")


def test_add_archive_args_registers_label():
    p = _parser()
    args = p.parse_args(["--archive-label", "test"])
    assert args.archive_label == "test"


def test_add_archive_args_default_formats():
    p = _parser()
    args = p.parse_args([])
    assert args.archive_formats == ["text"]


def test_build_archive_options_none_when_no_dir():
    p = _parser()
    args = p.parse_args([])
    assert build_archive_options(args) is None


def test_build_archive_options_returns_options_when_dir_set():
    p = _parser()
    args = p.parse_args(["--archive-dir", "/tmp/arch"])
    opts = build_archive_options(args)
    assert opts is not None
    assert opts.base_dir == "/tmp/arch"


def test_apply_archive_returns_none_without_dir():
    p = _parser()
    args = p.parse_args([])
    assert apply_archive(_empty_result(), args) is None


def test_apply_archive_creates_entry(tmp_path):
    p = _parser()
    args = p.parse_args(["--archive-dir", str(tmp_path)])
    entry = apply_archive(_empty_result(), args)
    assert entry is not None
    assert Path(entry.path).is_dir()


def test_render_archive_notice_empty_on_none():
    assert render_archive_notice(None) == ""


def test_render_archive_notice_contains_path(tmp_path):
    entry = ArchiveEntry(path=str(tmp_path), timestamp="20240101T000000Z",
                         label="", formats=["text"])
    notice = render_archive_notice(entry)
    assert str(tmp_path) in notice
    assert "text" in notice
