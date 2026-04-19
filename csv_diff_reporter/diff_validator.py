"""Validate diff results against user-defined row count and change rate thresholds."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from csv_diff_reporter.differ import DiffResult


@dataclass
class ThresholdOptions:
    max_added: Optional[int] = None
    max_removed: Optional[int] = None
    max_modified: Optional[int] = None
    max_change_rate: Optional[float] = None  # 0.0 – 1.0


@dataclass
class ThresholdViolation:
    rule: str
    limit: float
    actual: float

    def as_dict(self) -> dict:
        return {"rule": self.rule, "limit": self.limit, "actual": self.actual}


@dataclass
class ThresholdResult:
    violations: List[ThresholdViolation] = field(default_factory=list)

    def __bool__(self) -> bool:
        return len(self.violations) == 0

    def is_valid(self) -> bool:
        return bool(self)


def validate_thresholds(result: DiffResult, opts: ThresholdOptions) -> ThresholdResult:
    violations: List[ThresholdViolation] = []

    added = sum(1 for r in result.rows if r.change_type == "added")
    removed = sum(1 for r in result.rows if r.change_type == "removed")
    modified = sum(1 for r in result.rows if r.change_type == "modified")
    total = len(result.rows)

    if opts.max_added is not None and added > opts.max_added:
        violations.append(ThresholdViolation("max_added", opts.max_added, added))
    if opts.max_removed is not None and removed > opts.max_removed:
        violations.append(ThresholdViolation("max_removed", opts.max_removed, removed))
    if opts.max_modified is not None and modified > opts.max_modified:
        violations.append(ThresholdViolation("max_modified", opts.max_modified, modified))
    if opts.max_change_rate is not None and total > 0:
        changed = added + removed + modified
        rate = changed / total
        if rate > opts.max_change_rate:
            violations.append(ThresholdViolation("max_change_rate", opts.max_change_rate, round(rate, 4)))

    return ThresholdResult(violations=violations)
