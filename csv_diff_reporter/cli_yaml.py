"""CLI helpers for YAML export of diff results."""
from __future__ import annotations

import argparse
from pathlib import Path

from csv_diff_reporter.differ import DiffResult
from csv_diff_reporter.diff_formatter_yaml import format_diff_as_yaml


def add_yaml_args(parser: argparse.ArgumentParser) -> None:
    """Register --yaml / --yaml-output flags on *parser*."""
    group = parser.add_argument_group("YAML export")
    group.add_argument(
        "--yaml",
        dest="yaml_output",
        metavar="PATH",
        default=None,
        help="Write diff result as YAML to PATH.",
    )
    group.add_argument(
        "--yaml-stdout",
        dest="yaml_stdout",
        action="store_true",
        default=False,
        help="Print YAML diff to stdout instead of (or in addition to) the default report.",
    )


def apply_yaml_export(args: argparse.Namespace, result: DiffResult) -> str | None:
    """Produce YAML output according to *args*.

    Returns the YAML string when *yaml_stdout* is True, otherwise None.
    Writes to file when *yaml_output* is set.
    """
    yaml_str = format_diff_as_yaml(result)

    if getattr(args, "yaml_output", None):
        out_path = Path(args.yaml_output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(yaml_str, encoding="utf-8")

    if getattr(args, "yaml_stdout", False):
        return yaml_str
    return None
