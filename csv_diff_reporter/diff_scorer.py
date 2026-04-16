"""Scores a DiffResult to indicate overall severity of changes."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
from csv_diff_reporter.differ import DiffResult

SeverityLevel = Literal["none", "low", "medium", "high"]


@dataclass
class DiffScore:
    total_rows: int
    changed_rows: int
    change_rate: float  # 0.0 – 1.0
    severity: SeverityLevel
    score: int  # 0-100

    def as_dict(self) -> dict:
        return {
            "total_rows": self.total_rows,
            "changed_rows": self.changed_rows,
            "change_rate": round(self.change_rate, 4),
            "severity": self.severity,
            "score": self.score,
        }


def _severity(rate: float) -> SeverityLevel:
    if rate == 0.0:
        return "none"
    if rate < 0.1:
        return "low"
    if rate < 0.4:
        return "medium"
    return "high"


def score_diff(result: DiffResult) -> DiffScore:
    """Compute a numeric score (0-100) and severity label for *result*."""
    total = len(result.rows) if result.rows else 0
    changed = sum(
        1 for r in (result.rows or [])
        if r.change_type in ("added", "removed", "modified")
    )
    rate = changed / total if total > 0 else 0.0
    score = min(100, round(rate * 100))
    return DiffScore(
        total_rows=total,
        changed_rows=changed,
        change_rate=rate,
        severity=_severity(rate),
        score=score,
    )
