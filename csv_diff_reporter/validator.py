"""Validation utilities for CSV diff reporter inputs."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional


class ValidationError(Exception):
    """Raised when input validation fails."""


@dataclass
class ValidationResult:
    """Holds the outcome of a validation check."""

    valid: bool
    errors: List[str]

    def __bool__(self) -> bool:  # noqa: D105
        return self.valid


def validate_file_path(path: str) -> Optional[str]:
    """Return an error message if *path* is not a readable file, else None."""
    if not path:
        return "File path must not be empty."
    if not os.path.exists(path):
        return f"File not found: '{path}'."
    if not os.path.isfile(path):
        return f"Path is not a file: '{path}'."
    if not os.access(path, os.R_OK):
        return f"File is not readable: '{path}'."
    return None


def validate_csv_extension(path: str) -> Optional[str]:
    """Return an error message if *path* does not end with '.csv', else None."""
    if not path.lower().endswith(".csv"):
        return f"File does not have a .csv extension: '{path}'."
    return None


def validate_inputs(
    old_path: str,
    new_path: str,
    *,
    require_csv_extension: bool = True,
) -> ValidationResult:
    """Validate both CSV file paths and return a :class:`ValidationResult`.

    Parameters
    ----------
    old_path:
        Path to the original CSV file.
    new_path:
        Path to the updated CSV file.
    require_csv_extension:
        When *True* (default) both paths must end with ``.csv``.
    """
    errors: List[str] = []

    for label, path in (("old", old_path), ("new", new_path)):
        err = validate_file_path(path)
        if err:
            errors.append(f"[{label}] {err}")
            # Skip extension check when the file doesn't exist at all.
            continue
        if require_csv_extension:
            ext_err = validate_csv_extension(path)
            if ext_err:
                errors.append(f"[{label}] {ext_err}")

    return ValidationResult(valid=len(errors) == 0, errors=errors)
