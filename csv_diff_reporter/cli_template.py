"""CLI helpers for diff template rendering."""
from __future__ import annotations

import argparse
from typing import Optional

from csv_diff_reporter.diff_templater import TemplateOptions, render_template, list_variables
from csv_diff_reporter.differ import DiffResult


def add_template_args(parser: argparse.ArgumentParser) -> None:
    """Register --template and --template-missing flags on *parser*."""
    group = parser.add_argument_group("template")
    group.add_argument(
        "--template",
        metavar="TEXT",
        default=None,
        help="Template string with {{ variable }} placeholders for the diff summary.",
    )
    group.add_argument(
        "--template-missing",
        metavar="TEXT",
        default="",
        dest="template_missing",
        help="Value to use when a template variable is unknown (default: empty string).",
    )
    group.add_argument(
        "--template-list-vars",
        action="store_true",
        default=False,
        dest="template_list_vars",
        help="Print available template variables and exit.",
    )


def apply_template(
    result: DiffResult,
    args: argparse.Namespace,
) -> Optional[str]:
    """Return rendered template string or None if --template was not supplied."""
    if getattr(args, "template_list_vars", False):
        return "Available variables: " + ", ".join(list_variables())
    template: Optional[str] = getattr(args, "template", None)
    if not template:
        return None
    options = TemplateOptions(
        template=template,
        missing=getattr(args, "template_missing", ""),
    )
    return render_template(result, options)
