"""CLI helpers for schema validation integration."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from csv_diff_reporter.differ import DiffResult
from csv_diff_reporter.schema import SchemaValidationResult, validate_diff_values, validate_headers
from csv_diff_reporter.schema_loader import SchemaLoadError, load_schema


def add_schema_args(parser: argparse.ArgumentParser) -> None:
    """Attach schema-related CLI arguments to an existing ArgumentParser."""
    parser.add_argument(
        "--schema",
        metavar="FILE",
        default=None,
        help="Path to a TOML schema file for column validation.",
    )
    parser.add_argument(
        "--schema-strict",
        action="store_true",
        default=False,
        help="Exit with error code 2 when schema validation errors are found.",
    )


def apply_schema_validation(
    args: argparse.Namespace,
    headers: List[str],
    diff: DiffResult,
    output_lines: Optional[List[str]] = None,
) -> SchemaValidationResult:
    """Load schema (if specified) and validate headers + diff values.

    Prints warnings/errors to stderr.  Returns the combined result.
    """
    if not args.schema:
        from csv_diff_reporter.schema import SchemaValidationResult as SVR
        return SVR()

    try:
        spec = load_schema(args.schema)
    except SchemaLoadError as exc:
        print(f"schema error: {exc}", file=sys.stderr)
        sys.exit(1)

    header_result = validate_headers(headers, spec)
    value_result = validate_diff_values(diff, spec)

    combined = _merge(header_result, value_result)

    for warn in combined.warnings:
        print(f"schema warning: {warn}", file=sys.stderr)
    for err in combined.errors:
        print(f"schema error: {err}", file=sys.stderr)

    if not combined and args.schema_strict:
        sys.exit(2)

    return combined


def _merge(
    a: SchemaValidationResult, b: SchemaValidationResult
) -> SchemaValidationResult:
    from csv_diff_reporter.schema import SchemaValidationResult as SVR
    return SVR(errors=a.errors + b.errors, warnings=a.warnings + b.warnings)
