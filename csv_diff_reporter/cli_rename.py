"""CLI helpers for the column-renaming feature."""

import argparse
from typing import List, Optional

from csv_diff_reporter.column_renamer import RenameOptions, rename_columns
from csv_diff_reporter.differ import DiffResult


def add_rename_args(parser: argparse.ArgumentParser) -> None:
    """Register ``--rename`` flag on *parser*.

    The flag can be supplied multiple times::

        --rename old_name:new_name --rename another:better
    """
    parser.add_argument(
        "--rename",
        metavar="OLD:NEW",
        action="append",
        default=[],
        dest="renames",
        help="Rename a column for display: OLD_NAME:NEW_NAME (repeatable).",
    )


def _parse_renames(renames: List[str]) -> Optional[RenameOptions]:
    """Parse a list of ``'old:new'`` strings into a :class:`RenameOptions`.

    Returns ``None`` when *renames* is empty.
    Raises :class:`ValueError` for malformed entries.
    """
    if not renames:
        return None
    mapping = {}
    for entry in renames:
        if ":" not in entry:
            raise ValueError(
                f"Invalid --rename value {entry!r}: expected format OLD:NEW"
            )
        old, new = entry.split(":", 1)
        old, new = old.strip(), new.strip()
        if not old or not new:
            raise ValueError(
                f"Invalid --rename value {entry!r}: both OLD and NEW must be non-empty"
            )
        mapping[old] = new
    return RenameOptions(mapping=mapping)


def apply_rename(args: argparse.Namespace, result: DiffResult) -> DiffResult:
    """Apply column renaming described in *args* to *result*."""
    options = _parse_renames(getattr(args, "renames", []) or [])
    return rename_columns(result, options)
