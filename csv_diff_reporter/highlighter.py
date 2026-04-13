"""Highlight changed fields within a modified row diff."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csv_diff_reporter.differ import RowDiff


@dataclass
class FieldHighlight:
    """Represents a single field change with before/after values."""
    column: str
    old_value: Optional[str]
    new_value: Optional[str]

    @property
    def is_changed(self) -> bool:
        return self.old_value != self.new_value


@dataclass
class HighlightedRow:
    """A row diff enriched with per-field highlight information."""
    key: str
    change_type: str
    highlights: List[FieldHighlight] = field(default_factory=list)

    @property
    def changed_columns(self) -> List[str]:
        return [h.column for h in self.highlights if h.is_changed]


def highlight_row(row_diff: RowDiff) -> HighlightedRow:
    """Produce a HighlightedRow from a RowDiff, marking changed fields."""
    highlights: List[FieldHighlight] = []

    if row_diff.change_type == "modified":
        old = row_diff.old_row or {}
        new = row_diff.new_row or {}
        all_columns = sorted(set(old) | set(new))
        for col in all_columns:
            highlights.append(
                FieldHighlight(
                    column=col,
                    old_value=old.get(col),
                    new_value=new.get(col),
                )
            )
    elif row_diff.change_type == "added":
        for col, val in (row_diff.new_row or {}).items():
            highlights.append(FieldHighlight(column=col, old_value=None, new_value=val))
    elif row_diff.change_type == "removed":
        for col, val in (row_diff.old_row or {}).items():
            highlights.append(FieldHighlight(column=col, old_value=val, new_value=None))

    return HighlightedRow(
        key=row_diff.key,
        change_type=row_diff.change_type,
        highlights=highlights,
    )


def highlight_diff(row_diffs: List[RowDiff]) -> List[HighlightedRow]:
    """Apply highlighting to a list of RowDiff objects."""
    return [highlight_row(rd) for rd in row_diffs]


def format_highlighted_row(hr: HighlightedRow) -> str:
    """Return a human-readable string for a HighlightedRow."""
    lines = [f"[{hr.change_type.upper()}] key={hr.key}"]
    for h in hr.highlights:
        if h.is_changed:
            lines.append(f"  {h.column}: {h.old_value!r} -> {h.new_value!r}")
        else:
            lines.append(f"  {h.column}: {h.new_value!r} (unchanged)")
    return "\n".join(lines)
