"""Command-line interface for csv-diff-reporter."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from csv_diff_reporter.differ import diff_csv
from csv_diff_reporter.formatter import OutputFormat, format_output
from csv_diff_reporter.parser import CSVParseError, load_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csv-diff-reporter",
        description="Compare two CSV files and generate a human-readable diff report.",
    )
    parser.add_argument("old_file", type=Path, help="Path to the original CSV file.")
    parser.add_argument("new_file", type=Path, help="Path to the updated CSV file.")
    parser.add_argument(
        "--key",
        metavar="COLUMN",
        default=None,
        help="Column name to use as the row identifier (default: row index).",
    )
    parser.add_argument(
        "--format",
        dest="output_format",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        type=Path,
        default=None,
        help="Write report to FILE instead of stdout.",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 when differences are found.",
    )
    return parser


def _load_csv_files(
    old_file: Path, new_file: Path, key: str | None
) -> tuple[list, list]:
    """Load both CSV files, raising SystemExit with a helpful message on failure.

    Returns a tuple of (old_rows, new_rows).
    """
    old_rows = load_csv(old_file, key_column=key)
    new_rows = load_csv(new_file, key_column=key)
    return old_rows, new_rows


def _write_report(report: str, output: Path) -> int:
    """Write *report* to *output*, returning an exit code.

    Returns 0 on success, or 2 if the file cannot be written, printing an
    error message to stderr in that case.
    """
    try:
        output.write_text(report, encoding="utf-8")
    except OSError as exc:
        print(f"error: could not write output file: {exc}", file=sys.stderr)
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:  # noqa: D401
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        old_rows, new_rows = _load_csv_files(args.old_file, args.new_file, args.key)
    except (CSVParseError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = diff_csv(old_rows, new_rows)
    report = format_output(result, fmt=args.output_format)  # type: OutputFormat

    if args.output:
        rc = _write_report(report, args.output)
        if rc != 0:
            return rc
    else:
        print(report)

    if args.exit_code and result.total_changes > 0:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
