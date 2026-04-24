"""Enrich a DiffResult with computed metadata fields for each row."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csv_diff_reporter.differ import DiffResult, RowDiff


@dataclass
class EnrichedRowDiff:
    """A RowDiff with additional computed metadata."""

    row: RowDiff
    change_count: int          # number of fields that changed (modified rows)
    change_ratio: float        # change_count / total_fields  (0.0 for add/remove)
    changed_fields: List[str]  # names of fields that differ

    def as_dict(self) -> Dict:
        return {
            "key": self.row.key,
            "change_type": self.row.change_type,
            "change_count": self.change_count,
            "change_ratio": round(self.change_ratio, 4),
            "changed_fields": self.changed_fields,
        }


@dataclass
class EnrichOptions:
    include_ratio: bool = True
    include_changed_fields: bool = True


@dataclass
class EnrichResult:
    headers: List[str]
    rows: List[EnrichedRowDiff]
    options: EnrichOptions = field(default_factory=EnrichOptions)

    def __len__(self) -> int:
        return len(self.rows)


def _enrich_row(row: RowDiff, options: EnrichOptions) -> EnrichedRowDiff:
    """Compute enrichment metadata for a single RowDiff."""
    changed_fields: List[str] = []
    change_count = 0
    total_fields = 0

    if row.change_type == "modified" and row.old_fields and row.new_fields:
        all_keys = set(row.old_fields) | set(row.new_fields)
        total_fields = len(all_keys)
        for k in all_keys:
            old_val = row.old_fields.get(k)
            new_val = row.new_fields.get(k)
            if old_val != new_val:
                change_count += 1
                if options.include_changed_fields:
                    changed_fields.append(k)
    elif row.change_type in ("added", "removed"):
        fields = row.new_fields or row.old_fields or {}
        total_fields = len(fields)
        change_count = total_fields
        if options.include_changed_fields:
            changed_fields = list(fields.keys())

    ratio = (change_count / total_fields) if total_fields > 0 else 0.0

    return EnrichedRowDiff(
        row=row,
        change_count=change_count,
        change_ratio=ratio if options.include_ratio else 0.0,
        changed_fields=changed_fields if options.include_changed_fields else [],
    )


def enrich_diff(
    result: DiffResult,
    options: Optional[EnrichOptions] = None,
) -> EnrichResult:
    """Return an EnrichResult wrapping every row in the DiffResult."""
    opts = options or EnrichOptions()
    enriched = [_enrich_row(r, opts) for r in result.rows]
    return EnrichResult(headers=list(result.headers), rows=enriched, options=opts)
