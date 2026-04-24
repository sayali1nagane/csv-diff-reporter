"""Format an AuditLog for display."""
from __future__ import annotations

import json

from csv_diff_reporter.diff_auditor import AuditLog


def _as_text(log: AuditLog) -> str:
    if not log.entries:
        return "Audit log: no operations recorded."
    lines = ["Audit log:"]
    for i, entry in enumerate(log.all(), start=1):
        detail_part = f" — {entry.detail}" if entry.detail else ""
        lines.append(f"  {i:>3}. [{entry.timestamp}] {entry.operation}{detail_part}")
    return "\n".join(lines)


def _as_json(log: AuditLog) -> str:
    return json.dumps(log.as_dict(), indent=2)


def format_audit(log: AuditLog, fmt: str = "text") -> str:
    """Return formatted audit log.  *fmt* is ``'text'`` or ``'json'``."""
    if fmt == "json":
        return _as_json(log)
    return _as_text(log)
