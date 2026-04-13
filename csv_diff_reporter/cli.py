"""Command-line entry point for csv-diff-reporter."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .differ import diff_csv
from .parser import CSVParseError, load_csv
from .reporter import generate_report


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="csv-diff-reporter",
        description="Compare two CSV files and generate a human-readable diff report.",
    )
    p.add_argument("old", type=Path, help="Path to the original CSV file.")
    p.add_argument("new", type=Path, help="Path to the updated CSV file.")
    p.add_argument(
        "-k",
        "--key-column",
        default=None,
        metavar="COLUMN",
        help="Column name to use as the row key (default: row index).",
    )
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        metavar="FILE",
        help="Write the report to FILE instead of stdout.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    """Run the CLI. Returns an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        old_rows = load_csv(args.old, key_column=args.key_column)
        new_rows = load_csv(args.new, key_column=args.key_column)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except CSVParseError as exc:
        print(f"parse error: {exc}", file=sys.stderr)
        return 2

    result = diff_csv(old_rows, new_rows)

    if args.output:
        with args.output.open("w", encoding="utf-8") as fh:
            generate_report(result, file=fh)
        print(f"Report written to {args.output}")
    else:
        print(generate_report(result), end="")

    return 1 if result.diffs else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
