"""Tests for csv_diff_reporter.parser module."""

import pytest
from pathlib import Path

from csv_diff_reporter.parser import load_csv, get_headers, CSVParseError


SAMPLE_CSV = """id,name,age
1,Alice,30
2,Bob,25
3,Charlie,35
"""

DUPLICATE_KEY_CSV = """id,name
1,Alice
1,Bob
"""

EMPTY_CSV = ""


@pytest.fixture
def csv_file(tmp_path):
    """Create a temporary CSV file with sample data."""
    def _make(content, filename="test.csv"):
        p = tmp_path / filename
        p.write_text(content, encoding="utf-8")
        return str(p)
    return _make


def test_load_csv_by_index(csv_file):
    path = csv_file(SAMPLE_CSV)
    rows = load_csv(path)
    assert len(rows) == 3
    assert rows["0"] == {"id": "1", "name": "Alice", "age": "30"}
    assert rows["2"] == {"id": "3", "name": "Charlie", "age": "35"}


def test_load_csv_by_key_column(csv_file):
    path = csv_file(SAMPLE_CSV)
    rows = load_csv(path, key_column="id")
    assert "1" in rows
    assert rows["2"]["name"] == "Bob"


def test_load_csv_missing_key_column(csv_file):
    path = csv_file(SAMPLE_CSV)
    with pytest.raises(CSVParseError, match="Key column 'email' not found"):
        load_csv(path, key_column="email")


def test_load_csv_duplicate_key(csv_file):
    path = csv_file(DUPLICATE_KEY_CSV)
    with pytest.raises(CSVParseError, match="Duplicate key '1'"):
        load_csv(path, key_column="id")


def test_load_csv_file_not_found():
    with pytest.raises(CSVParseError, match="File not found"):
        load_csv("/nonexistent/path/file.csv")


def test_load_csv_empty_file(csv_file):
    path = csv_file(EMPTY_CSV)
    with pytest.raises(CSVParseError, match="empty or has no headers"):
        load_csv(path)


def test_get_headers(csv_file):
    path = csv_file(SAMPLE_CSV)
    headers = get_headers(path)
    assert headers == ["id", "name", "age"]


def test_get_headers_file_not_found():
    with pytest.raises(CSVParseError):
        get_headers("/no/such/file.csv")


def test_load_csv_returns_string_values(csv_file):
    path = csv_file(SAMPLE_CSV)
    rows = load_csv(path)
    for row in rows.values():
        for value in row.values():
            assert isinstance(value, str)
