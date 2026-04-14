"""Annotate each row diff with a human-readable change label and severity."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from csv_diff_reporter.differ import DiffResult, RowDiff


@dataclass
class AnnotatedRow:
    """A RowDiff enriched with a label and severity level."""

    row: RowDiff
    label: str
    severity: str  # "info" | "warning" | "critical"
    note: Optional[str] = None


@dataclass
class AnnotatedResult:
    rows: List[AnnotatedRow] = field(default_factory=list)
    source: Optional[DiffResult] = None


_SEVERITY_MAP = {
    "added": "info",
    "removed": "warning",
    "modified": "critical",
}

_LABEL_MAP = {
    "added": "Row Added",
    "removed": "Row Removed",
    "modified": "Row Modified",
}


def _severity(change_type: str) -> str:
    return _SEVERITY_MAP.get(change_type, "info")


def _label(change_type: str) -> str:
    return _LABEL_MAP.get(change_type, change_type.title())


def _note(row: RowDiff) -> Optional[str]:
    """Generate a short note describing what changed in a modified row."""
    if row.change_type != "modified" or not row.diff:
        return None
    changed = [k for k, v in row.diff.items() if v[0] != v[1]]
    if not changed:
        return None
    cols = ", ".join(changed[:3])
    extra = f" (+{len(changed) - 3} more)" if len(changed) > 3 else ""
    return f"Changed columns: {cols}{extra}"


def annotate_diff(result: DiffResult) -> AnnotatedResult:
    """Annotate every RowDiff in *result* and return an AnnotatedResult."""
    annotated: List[AnnotatedRow] = []
    for row in result.rows:
        annotated.append(
            AnnotatedRow(
                row=row,
                label=_label(row.change_type),
                severity=_severity(row.change_type),
                note=_note(row),
            )
        )
    return AnnotatedResult(rows=annotated, source=result)
