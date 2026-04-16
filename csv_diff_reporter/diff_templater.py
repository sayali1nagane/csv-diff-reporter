"""Render diff results using a Jinja2-style simple template engine."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from csv_diff_reporter.differ import DiffResult
from csv_diff_reporter.summary import compute_summary


@dataclass
class TemplateOptions:
    template: str
    missing: str = ""


_VARIABLE_RE = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def _build_context(result: DiffResult) -> dict:
    summary = compute_summary(result)
    return {
        "added": str(summary.added),
        "removed": str(summary.removed),
        "modified": str(summary.modified),
        "unchanged": str(summary.unchanged),
        "total_changes": str(summary.added + summary.removed + summary.modified),
        "total_rows": str(summary.added + summary.removed + summary.modified + summary.unchanged),
        "change_rate": f"{summary.change_rate:.2f}",
        "headers": ", ".join(result.headers),
    }


def render_template(result: DiffResult, options: TemplateOptions) -> str:
    """Render a template string with diff summary variables."""
    context = _build_context(result)

    def replace(match: re.Match) -> str:
        key = match.group(1)
        return context.get(key, options.missing)

    return _VARIABLE_RE.sub(replace, options.template)


def list_variables() -> list[str]:
    """Return the available template variable names."""
    return ["added", "removed", "modified", "unchanged",
            "total_changes", "total_rows", "change_rate", "headers"]
