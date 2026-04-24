"""CLI helpers for the key-rename feature."""
from __future__ import annotations

import argparse
from typing import List, Optional

from csv_diff_reporter.diff_renamer import KeyRenameOptions, format_rename_notice, rename_keys
from csv_diff_reporter.differ import DiffResult


def add_rename_key_args(parser: argparse.ArgumentParser) -> None:
    """Register --rename-key and --rename-key-strict flags on *parser*."""
    parser.add_argument(
        "--rename-key",
        metavar="OLD=NEW",
        dest="rename_keys",
        action="append",
        default=[],
        help="Rename a row key: OLD=NEW.  May be repeated.",
    )
    parser.add_argument(
        "--rename-key-strict",
        dest="rename_key_strict",
        action="store_true",
        default=False,
        help="Raise an error if a key is not present in the rename mapping.",
    )


def _parse_rename_key_args(pairs: List[str]) -> dict:
    mapping: dict = {}
    for pair in pairs:
        if "=" not in pair:
            raise argparse.ArgumentTypeError(
                f"--rename-key value must be in OLD=NEW format, got: {pair!r}"
            )
        old, new = pair.split("=", 1)
        mapping[old.strip()] = new.strip()
    return mapping


def build_rename_key_options(args: argparse.Namespace) -> Optional[KeyRenameOptions]:
    """Build a KeyRenameOptions from parsed CLI *args*, or None if not configured."""
    pairs: List[str] = getattr(args, "rename_keys", []) or []
    if not pairs:
        return None
    mapping = _parse_rename_key_args(pairs)
    strict: bool = getattr(args, "rename_key_strict", False)
    return KeyRenameOptions(mapping=mapping, passthrough=not strict)


def apply_rename_keys(result: DiffResult, args: argparse.Namespace) -> DiffResult:
    """Apply key renaming to *result* based on CLI *args*."""
    options = build_rename_key_options(args)
    if options is None:
        return result
    return rename_keys(result, options)


def render_rename_notice(args: argparse.Namespace) -> str:
    """Return the rename notice string, or empty string if no renames configured."""
    options = build_rename_key_options(args)
    if options is None:
        return ""
    return format_rename_notice(options)
