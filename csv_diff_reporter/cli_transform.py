"""CLI helpers for the --transform feature."""
from __future__ import annotations

import argparse
from typing import Optional

from csv_diff_reporter.differ import DiffResult
from csv_diff_reporter.diff_transformer import (
    TransformFn,
    TransformOptions,
    TransformResult,
    transform_diff,
)
from csv_diff_reporter.diff_transformer_formatter import format_transform_notice

_BUILTIN: dict[str, TransformFn] = {
    "upper": str.upper,
    "lower": str.lower,
    "strip": str.strip,
    "title": str.title,
}


def add_transform_args(parser: argparse.ArgumentParser) -> None:
    """Register --transform and --transform-default flags on *parser*."""
    parser.add_argument(
        "--transform",
        metavar="COLUMN:FN",
        action="append",
        default=[],
        help="Apply a named transform to a column, e.g. name:upper. "
             "Repeatable. Built-ins: upper, lower, strip, title.",
    )
    parser.add_argument(
        "--transform-default",
        metavar="FN",
        default=None,
        help="Apply a named transform to all columns not explicitly mapped.",
    )


def _parse_transform_args(args: argparse.Namespace) -> Optional[TransformOptions]:
    transforms = getattr(args, "transform", []) or []
    default_name = getattr(args, "transform_default", None)

    column_transforms: dict[str, TransformFn] = {}
    for item in transforms:
        if ":" not in item:
            continue
        col, fn_name = item.split(":", 1)
        fn = _BUILTIN.get(fn_name.strip())
        if fn is not None:
            column_transforms[col.strip()] = fn

    default_fn: Optional[TransformFn] = None
    if default_name and default_name in _BUILTIN:
        default_fn = _BUILTIN[default_name]

    if not column_transforms and default_fn is None:
        return None
    return TransformOptions(column_transforms=column_transforms, default_transform=default_fn)


def apply_transform(result: DiffResult, args: argparse.Namespace) -> TransformResult:
    opts = _parse_transform_args(args)
    return transform_diff(result, opts)


def render_transform_notice(tr: TransformResult, fmt: str = "text") -> str:
    return format_transform_notice(tr, fmt=fmt)  # type: ignore[arg-type]
