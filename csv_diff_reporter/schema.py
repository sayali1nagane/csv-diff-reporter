"""Schema validation for CSV diff columns."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csv_diff_reporter.differ import DiffResult


@dataclass
class SchemaError:
    column: str
    message: str

    def __str__(self) -> str:
        return f"[{self.column}] {self.message}"


@dataclass
class SchemaValidationResult:
    errors: List[SchemaError] = field(default_factory=list)
    warnings: List[SchemaError] = field(default_factory=list)

    def __bool__(self) -> bool:
        return len(self.errors) == 0

    def is_valid(self) -> bool:
        return bool(self)

    def has_warnings(self) -> bool:
        return len(self.warnings) > 0


@dataclass
class ColumnSchema:
    required: bool = False
    expected_type: Optional[str] = None  # "int", "float", "str"
    max_length: Optional[int] = None
    allowed_values: Optional[List[str]] = None


SchemaSpec = Dict[str, ColumnSchema]


def _check_type(value: str, expected: str) -> bool:
    """Return True if value can be coerced to expected type."""
    try:
        if expected == "int":
            int(value)
        elif expected == "float":
            float(value)
        return True
    except (ValueError, TypeError):
        return False


def validate_headers(
    headers: List[str], spec: SchemaSpec
) -> SchemaValidationResult:
    """Validate that required columns are present in headers."""
    result = SchemaValidationResult()
    for col, schema in spec.items():
        if schema.required and col not in headers:
            result.errors.append(
                SchemaError(col, "required column is missing from CSV headers")
            )
        elif col not in headers:
            result.warnings.append(
                SchemaError(col, "expected column not found in CSV headers")
            )
    return result


def validate_diff_values(
    diff: DiffResult, spec: SchemaSpec
) -> SchemaValidationResult:
    """Validate cell values in diff rows against the schema spec."""
    result = SchemaValidationResult()
    all_rows = list(diff.added) + list(diff.removed) + list(diff.modified)

    for row_diff in all_rows:
        row_data = row_diff.new_row or row_diff.old_row or {}
        for col, schema in spec.items():
            if col not in row_data:
                continue
            value = row_data[col]
            if schema.expected_type and not _check_type(value, schema.expected_type):
                result.errors.append(
                    SchemaError(
                        col,
                        f"value {value!r} cannot be coerced to {schema.expected_type}",
                    )
                )
            if schema.max_length is not None and len(value) > schema.max_length:
                result.errors.append(
                    SchemaError(
                        col,
                        f"value {value!r} exceeds max length {schema.max_length}",
                    )
                )
            if schema.allowed_values is not None and value not in schema.allowed_values:
                result.errors.append(
                    SchemaError(
                        col,
                        f"value {value!r} not in allowed values {schema.allowed_values}",
                    )
                )
    return result
