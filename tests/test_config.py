"""Tests for csv_diff_reporter.config."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from csv_diff_reporter.config import (
    AppConfig,
    config_from_env,
    effective_config,
    load_config,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MINIMAL_TOML = b"""
[csv_diff_reporter]
output_format = "json"
key_column = "id"
ignore_columns = ["updated_at", "checksum"]
show_unchanged = true
"""

FLAT_TOML = b"""
output_format = "markdown"
"""


# ---------------------------------------------------------------------------
# load_config
# ---------------------------------------------------------------------------


def test_load_config_returns_defaults_when_file_missing(tmp_path):
    cfg = load_config(tmp_path / "nonexistent.toml")
    assert isinstance(cfg, AppConfig)
    assert cfg.output_format == "text"
    assert cfg.key_column is None
    assert cfg.ignore_columns == []
    assert cfg.show_unchanged is False


def test_load_config_reads_toml_section(tmp_path):
    toml_file = tmp_path / "cfg.toml"
    toml_file.write_bytes(MINIMAL_TOML)

    cfg = load_config(toml_file)

    assert cfg.output_format == "json"
    assert cfg.key_column == "id"
    assert cfg.ignore_columns == ["updated_at", "checksum"]
    assert cfg.show_unchanged is True


def test_load_config_reads_flat_toml(tmp_path):
    toml_file = tmp_path / "flat.toml"
    toml_file.write_bytes(FLAT_TOML)

    cfg = load_config(toml_file)
    assert cfg.output_format == "markdown"


def test_load_config_accepts_path_string(tmp_path):
    toml_file = tmp_path / "cfg.toml"
    toml_file.write_bytes(MINIMAL_TOML)

    cfg = load_config(str(toml_file))
    assert cfg.key_column == "id"


# ---------------------------------------------------------------------------
# config_from_env
# ---------------------------------------------------------------------------


def test_config_from_env_empty(monkeypatch):
    for var in (
        "CSV_DIFF_KEY_COLUMN",
        "CSV_DIFF_OUTPUT_FORMAT",
        "CSV_DIFF_OUTPUT_FILE",
        "CSV_DIFF_IGNORE_COLUMNS",
        "CSV_DIFF_SHOW_UNCHANGED",
    ):
        monkeypatch.delenv(var, raising=False)

    assert config_from_env() == {}


def test_config_from_env_reads_variables(monkeypatch):
    monkeypatch.setenv("CSV_DIFF_KEY_COLUMN", "uuid")
    monkeypatch.setenv("CSV_DIFF_OUTPUT_FORMAT", "markdown")
    monkeypatch.setenv("CSV_DIFF_IGNORE_COLUMNS", "col_a, col_b")
    monkeypatch.setenv("CSV_DIFF_SHOW_UNCHANGED", "true")

    result = config_from_env()

    assert result["key_column"] == "uuid"
    assert result["output_format"] == "markdown"
    assert result["ignore_columns"] == ["col_a", "col_b"]
    assert result["show_unchanged"] is True


# ---------------------------------------------------------------------------
# effective_config
# ---------------------------------------------------------------------------


def test_effective_config_env_overrides_file(tmp_path, monkeypatch):
    toml_file = tmp_path / "cfg.toml"
    toml_file.write_bytes(MINIMAL_TOML)  # output_format = "json"

    monkeypatch.setenv("CSV_DIFF_OUTPUT_FORMAT", "markdown")

    cfg = effective_config(toml_file)
    assert cfg.output_format == "markdown"  # env wins
    assert cfg.key_column == "id"  # still from file


def test_effective_config_no_file_no_env(tmp_path, monkeypatch):
    for var in (
        "CSV_DIFF_KEY_COLUMN",
        "CSV_DIFF_OUTPUT_FORMAT",
        "CSV_DIFF_OUTPUT_FILE",
        "CSV_DIFF_IGNORE_COLUMNS",
        "CSV_DIFF_SHOW_UNCHANGED",
    ):
        monkeypatch.delenv(var, raising=False)

    cfg = effective_config(tmp_path / "missing.toml")
    assert cfg == AppConfig()
