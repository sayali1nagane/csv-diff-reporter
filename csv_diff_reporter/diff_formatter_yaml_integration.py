"""Integration helpers: register YAML export into the main CLI pipeline."""
from __future__ import annotations

import argparse
import sys
from typing import IO

from csv_diff_reporter.differ import DiffResult
from csv_diff_reporter.cli_yaml import add_yaml_args, apply_yaml_export


def integrate_yaml_export(
    parser: argparse.ArgumentParser,
) -> None:
    """Add YAML export arguments to an existing *parser*.

    Call this once during CLI setup, before :func:`argparse.ArgumentParser.parse_args`.
    """
    add_yaml_args(parser)


def run_yaml_export(
    args: argparse.Namespace,
    result: DiffResult,
    stdout: IO[str] | None = None,
) -> None:
    """Execute YAML export side-effects based on parsed *args*.

    Writes to file when ``--yaml PATH`` is supplied.
    Prints to *stdout* (defaults to ``sys.stdout``) when ``--yaml-stdout`` is set.
    """
    if stdout is None:
        stdout = sys.stdout

    yaml_output = apply_yaml_export(args, result)
    if yaml_output is not None:
        stdout.write(yaml_output)


__all__ = ["integrate_yaml_export", "run_yaml_export"]
