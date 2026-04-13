"""CSV file parsing utilities for csv-diff-reporter."""

import csv
from pathlib import Path
from typing import Optional


class CSVParseError(Exception):
    """Raised when a CSV file cannot be parsed."""
    pass


def load_csv(filepath: str, key_column: Optional[str] = None) -> dict:
    """
    Load a CSV file and return its contents as a dict keyed by row index
    or a specified key column.

    Args:
        filepath: Path to the CSV file.
        key_column: Optional column name to use as the row key.

    Returns:
        A dict mapping row keys to row dicts.

    Raises:
        CSVParseError: If the file cannot be read or parsed.
    """
    path = Path(filepath)
    if not path.exists():
        raise CSVParseError(f"File not found: {filepath}")
    if not path.is_file():
        raise CSVParseError(f"Path is not a file: {filepath}")

    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise CSVParseError(f"CSV file is empty or has no headers: {filepath}")

            rows = {}
            for idx, row in enumerate(reader):
                if key_column:
                    if key_column not in row:
                        raise CSVParseError(
                            f"Key column '{key_column}' not found in {filepath}. "
                            f"Available columns: {list(row.keys())}"
                        )
                    key = row[key_column]
                    if key in rows:
                        raise CSVParseError(
                            f"Duplicate key '{key}' in column '{key_column}' at row {idx + 2}"
                        )
                else:
                    key = str(idx)
                rows[key] = dict(row)

        return rows

    except (OSError, csv.Error) as exc:
        raise CSVParseError(f"Failed to parse {filepath}: {exc}") from exc


def get_headers(filepath: str) -> list:
    """
    Return the list of column headers from a CSV file.

    Args:
        filepath: Path to the CSV file.

    Returns:
        List of column header strings.

    Raises:
        CSVParseError: If the file cannot be read.
    """
    path = Path(filepath)
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise CSVParseError(f"CSV file is empty or has no headers: {filepath}")
            return list(reader.fieldnames)
    except (OSError, csv.Error) as exc:
        raise CSVParseError(f"Failed to read headers from {filepath}: {exc}") from exc
