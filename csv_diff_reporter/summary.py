"""Summary statistics module for CSV diff reports."""
from dataclasses import dataclass
from typing import Dict

from csv_diff_reporter.differ import DiffResult


@dataclass
class DiffSummary:
    """Aggregated statistics for a diff result."""
    total_rows_old: int
    total_rows_new: int
    added: int
    removed: int
    modified: int
    unchanged: int
    change_rate: float  # fraction of old rows that changed

    def as_dict(self) -> Dict:
        return {
            "total_rows_old": self.total_rows_old,
            "total_rows_new": self.total_rows_new,
            "added": self.added,
            "removed": self.removed,
            "modified": self.modified,
            "unchanged": self.unchanged,
            "change_rate": round(self.change_rate, 4),
        }


def compute_summary(result: DiffResult, total_rows_old: int, total_rows_new: int) -> DiffSummary:
    """Compute a DiffSummary from a DiffResult and row counts."""
    added = len(result.added)
    removed = len(result.removed)
    modified = len(result.modified)
    unchanged = len(result.unchanged)

    denominator = total_rows_old if total_rows_old > 0 else 1
    change_rate = (added + removed + modified) / denominator

    return DiffSummary(
        total_rows_old=total_rows_old,
        total_rows_new=total_rows_new,
        added=added,
        removed=removed,
        modified=modified,
        unchanged=unchanged,
        change_rate=change_rate,
    )


def format_summary_text(summary: DiffSummary) -> str:
    """Return a human-readable summary block."""
    lines = [
        "=== Diff Summary ===",
        f"  Rows (old): {summary.total_rows_old}",
        f"  Rows (new): {summary.total_rows_new}",
        f"  Added     : {summary.added}",
        f"  Removed   : {summary.removed}",
        f"  Modified  : {summary.modified}",
        f"  Unchanged : {summary.unchanged}",
        f"  Change %  : {summary.change_rate * 100:.2f}%",
    ]
    return "\n".join(lines)
