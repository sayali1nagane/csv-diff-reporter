"""Classify diff rows into named categories based on field patterns."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csv_diff_reporter.differ import DiffResult, RowDiff


@dataclass
class ClassifyOptions:
    """Options controlling how rows are classified."""
    categories: Dict[str, List[str]] = field(default_factory=dict)
    # e.g. {"price_change": ["price", "cost"], "name_change": ["name"]}
    default_category: str = "other"


@dataclass
class ClassifiedRow:
    row: RowDiff
    category: str

    def as_dict(self) -> dict:
        return {
            "key": self.row.key,
            "change_type": (
                "added" if self.row.old_fields is None
                else "removed" if self.row.new_fields is None
                else "modified"
            ),
            "category": self.category,
        }


@dataclass
class ClassifyResult:
    headers: List[str]
    rows: List[ClassifiedRow] = field(default_factory=list)
    options: Optional[ClassifyOptions] = None

    def for_category(self, category: str) -> List[ClassifiedRow]:
        return [r for r in self.rows if r.category == category]

    def category_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for r in self.rows:
            counts[r.category] = counts.get(r.category, 0) + 1
        return counts


def _detect_category(row: RowDiff, options: ClassifyOptions) -> str:
    """Return the first matching category whose fields appear in changed fields."""
    changed: set[str] = set()
    if row.old_fields is not None and row.new_fields is not None:
        for k in row.new_fields:
            if row.old_fields.get(k) != row.new_fields.get(k):
                changed.add(k)
    elif row.new_fields is not None:
        changed = set(row.new_fields.keys())
    elif row.old_fields is not None:
        changed = set(row.old_fields.keys())

    for category, trigger_fields in options.categories.items():
        if changed.intersection(trigger_fields):
            return category
    return options.default_category


def classify_diff(
    result: DiffResult,
    options: Optional[ClassifyOptions] = None,
) -> ClassifyResult:
    """Classify every row in *result* according to *options*."""
    if options is None or not options.categories:
        opts = ClassifyOptions()
    else:
        opts = options

    classified = [
        ClassifiedRow(row=row, category=_detect_category(row, opts))
        for row in result.rows
    ]
    return ClassifyResult(headers=list(result.headers), rows=classified, options=opts)
