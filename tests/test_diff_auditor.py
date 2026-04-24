"""Tests for diff_auditor, diff_auditor_formatter, and cli_audit."""
from __future__ import annotations

import json

import pytest

from csv_diff_reporter.diff_auditor import AuditEntry, AuditLog, build_audit_log
from csv_diff_reporter.diff_auditor_formatter import format_audit
from csv_diff_reporter.cli_audit import add_audit_args, render_audit


# ---------------------------------------------------------------------------
# AuditLog
# ---------------------------------------------------------------------------

def test_audit_log_starts_empty():
    log = AuditLog()
    assert len(log) == 0
    assert log.all() == []


def test_audit_log_records_entry():
    log = AuditLog()
    log.record("filter", "exclude_added=True")
    assert len(log) == 1
    entry = log.all()[0]
    assert entry.operation == "filter"
    assert entry.detail == "exclude_added=True"


def test_audit_log_all_returns_copy():
    log = AuditLog()
    log.record("sort", "key asc")
    copy = log.all()
    copy.clear()
    assert len(log) == 1


def test_audit_log_clear_resets():
    log = AuditLog()
    log.record("redact", "columns=[email]")
    log.clear()
    assert len(log) == 0


def test_audit_log_as_dict_has_entries_key():
    log = AuditLog()
    log.record("normalize", "strip_whitespace=True")
    d = log.as_dict()
    assert "entries" in d
    assert len(d["entries"]) == 1


def test_build_audit_log_empty():
    log = build_audit_log()
    assert len(log) == 0


def test_build_audit_log_prepopulates():
    log = build_audit_log([("filter", "x"), ("sort", "y")])
    assert len(log) == 2
    assert log.all()[0].operation == "filter"
    assert log.all()[1].operation == "sort"


def test_audit_entry_as_dict_has_expected_keys():
    entry = AuditEntry(operation="truncate", detail="limit=100")
    d = entry.as_dict()
    assert set(d.keys()) == {"operation", "detail", "timestamp"}


# ---------------------------------------------------------------------------
# Formatter
# ---------------------------------------------------------------------------

def test_format_text_empty_log():
    log = AuditLog()
    out = format_audit(log, fmt="text")
    assert "no operations" in out


def test_format_text_contains_operation():
    log = AuditLog()
    log.record("filter", "exclude_removed=True")
    out = format_audit(log, fmt="text")
    assert "filter" in out
    assert "exclude_removed=True" in out


def test_format_json_is_valid_json():
    log = AuditLog()
    log.record("sort", "type desc")
    out = format_audit(log, fmt="json")
    parsed = json.loads(out)
    assert "entries" in parsed
    assert parsed["entries"][0]["operation"] == "sort"


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def test_add_audit_args_registers_flags():
    import argparse
    parser = argparse.ArgumentParser()
    add_audit_args(parser)
    args = parser.parse_args([])
    assert args.audit is False
    assert args.audit_format == "text"
    assert args.audit_output is None


def test_render_audit_returns_string():
    log = AuditLog()
    log.record("paginate", "page=1 size=10")
    out = render_audit(log, fmt="text")
    assert isinstance(out, str)
    assert "paginate" in out


def test_render_audit_writes_file(tmp_path):
    log = AuditLog()
    log.record("export", "format=csv")
    dest = tmp_path / "audit.txt"
    render_audit(log, fmt="text", output_path=str(dest))
    assert dest.exists()
    assert "export" in dest.read_text()
