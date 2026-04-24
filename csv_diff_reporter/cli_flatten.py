"""CLI helpers for the diff-flattener feature."""
from __future__ import annotations

import argparse
import json
from typing import Optional

from csv_diff_reporter.diff_flattener import FlattenOptions, FlattenResult, flatten_diff
from csv_diff_reporter.differ import DiffResult


def add_flatten_args(parser: argparse.ArgumentParser) -> None:
    """Register --flatten and related flags on *parser*."""
    grp = parser.add_argument_group("flatten")
    grp.add_argument(
        "--flatten",
        action="store_true",
        default=False,
        help="Emit a flat list of dicts instead of the structured diff.",
    )
    grp.add_argument(
        "--flatten-include-unchanged",
        action="store_true",
        default=False,
        dest="flatten_include_unchanged",
        help="Include unchanged rows in the flattened output.",
    )
    grp.add_argument(
        "--flatten-change-key",
        default="_change",
        dest="flatten_change_key",
        metavar="KEY",
        help="Column name used for the change-type label (default: _change).",
    )
    grp.add_argument(
        "--flatten-no-key-column",
        action="store_true",
        default=False,
        dest="flatten_no_key_column",
        help="Omit the _key column from the flattened output.",
    )


def build_flatten_options(args: argparse.Namespace) -> Optional[FlattenOptions]:
    if not getattr(args, "flatten", False):
        return None
    return FlattenOptions(
        include_unchanged=getattr(args, "flatten_include_unchanged", False),
        change_type_key=getattr(args, "flatten_change_key", "_change"),
        key_column=None if getattr(args, "flatten_no_key_column", False) else "_key",
    )


def apply_flatten(
    result: DiffResult,
    args: argparse.Namespace,
) -> Optional[FlattenResult]:
    opts = build_flatten_options(args)
    if opts is None:
        return None
    return flatten_diff(result, opts)


def render_flat_result(flat: FlattenResult, fmt: str = "json") -> str:
    if fmt == "json":
        return json.dumps(flat.as_dicts(), indent=2)
    # text: one line per row
    lines = ["\t".join(flat.headers)]
    for row in flat.rows:
        lines.append("\t".join(str(row.get(h, "")) for h in flat.headers))
    return "\n".join(lines)
