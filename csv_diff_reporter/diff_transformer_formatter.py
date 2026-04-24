"""Format the TransformResult for CLI output."""
from __future__ import annotations

import json
from typing import Literal

from csv_diff_reporter.diff_transformer import TransformResult


def _as_text(tr: TransformResult) -> str:
    if not tr.columns_affected:
        return "No transformations applied."
    cols = ", ".join(tr.columns_affected)
    return f"Transformations applied to column(s): {cols}"


def _as_json(tr: TransformResult) -> str:
    return json.dumps(
        {
            "columns_affected": tr.columns_affected,
            "transformed": bool(tr.columns_affected),
        },
        indent=2,
    )


def format_transform_notice(
    tr: TransformResult,
    fmt: Literal["text", "json"] = "text",
) -> str:
    if fmt == "json":
        return _as_json(tr)
    return _as_text(tr)
