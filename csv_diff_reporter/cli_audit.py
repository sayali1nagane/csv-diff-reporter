"""CLI helpers for the audit-trail feature."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from csv_diff_reporter.diff_auditor import AuditLog
from csv_diff_reporter.diff_auditor_formatter import format_audit


def add_audit_args(parser: argparse.ArgumentParser) -> None:
    """Register audit-related flags onto *parser*."""
    group = parser.add_argument_group("audit")
    group.add_argument(
        "--audit",
        action="store_true",
        default=False,
        help="Print the audit trail after processing.",
    )
    group.add_argument(
        "--audit-format",
        choices=["text", "json"],
        default="text",
        dest="audit_format",
        help="Output format for the audit trail (default: text).",
    )
    group.add_argument(
        "--audit-output",
        default=None,
        dest="audit_output",
        metavar="PATH",
        help="Write audit trail to this file instead of stdout.",
    )


def render_audit(
    log: AuditLog,
    fmt: str = "text",
    output_path: Optional[str] = None,
) -> str:
    """Format *log* and optionally write it to *output_path*.

    Returns the formatted string regardless of whether it was written to a file.
    """
    content = format_audit(log, fmt=fmt)
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return content
