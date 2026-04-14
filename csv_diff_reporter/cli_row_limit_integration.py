"""Integration helper: wire row-limit into the main pipeline.

This module provides ``integrate_row_limit`` which applies the row-limit
step to both sides of a CSV diff (old and new) before diffing.
"""
from __future__ import annotations

import argparse
import sys
from typing import Dict, List, Tuple

from csv_diff_reporter.row_limit import RowLimitOptions, apply_row_limit, format_row_limit_warning


def integrate_row_limit(
    args: argparse.Namespace,
    old_data: Dict[str, List[dict]],
    new_data: Dict[str, List[dict]],
) -> Tuple[Dict[str, List[dict]], Dict[str, List[dict]]]:
    """Apply the row-limit to both *old_data* and *new_data*.

    Warnings are emitted to *stderr* separately for each side when
    truncation occurs (and ``--no-row-limit-warning`` is not set).

    Parameters
    ----------
    args:
        Parsed CLI namespace; expected attributes: ``max_rows``,
        ``no_row_limit_warning``.
    old_data:
        Keyed rows from the 'old' CSV file.
    new_data:
        Keyed rows from the 'new' CSV file.

    Returns
    -------
    Tuple of (limited_old_data, limited_new_data).
    """
    max_rows: int | None = getattr(args, "max_rows", None)
    suppress_warning: bool = getattr(args, "no_row_limit_warning", False)

    options = RowLimitOptions(
        max_rows=max_rows,
        warn_on_truncation=not suppress_warning,
    )

    old_result = apply_row_limit(old_data, options)
    new_result = apply_row_limit(new_data, options)

    for label, result in (("old", old_result), ("new", new_result)):
        if result.was_limited and options.warn_on_truncation:
            warning = format_row_limit_warning(result)
            print(f"[{label}] {warning}", file=sys.stderr)

    return old_result.data, new_result.data
