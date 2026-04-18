"""Random and deterministic sampling of diff results."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

from csv_diff_reporter.differ import DiffResult, RowDiff


@dataclass
class SampleOptions:
    n: Optional[int] = None
    fraction: Optional[float] = None
    seed: Optional[int] = None
    change_types: Optional[list[str]] = None  # e.g. ["added", "removed", "modified"]


@dataclass
class SampleResult:
    diff: DiffResult
    original_count: int
    sampled_count: int

    @property
    def dropped(self) -> int:
        return self.original_count - self.sampled_count


def _change_type(row: RowDiff) -> str:
    if row.old is None:
        return "added"
    if row.new is None:
        return "removed"
    return "modified"


def sample_diff(result: DiffResult, options: SampleOptions) -> SampleResult:
    """Return a SampleResult containing a subset of rows from *result*."""
    rows = list(result.rows)

    if options.change_types:
        allowed = set(options.change_types)
        rows = [r for r in rows if _change_type(r) in allowed]

    original_count = len(rows)

    rng = random.Random(options.seed)

    if options.n is not None:
        k = min(options.n, len(rows))
        rows = rng.sample(rows, k)
    elif options.fraction is not None:
        k = max(0, int(len(rows) * options.fraction))
        rows = rng.sample(rows, k)

    sampled = DiffResult(headers=result.headers, rows=rows)
    return SampleResult(
        diff=sampled,
        original_count=original_count,
        sampled_count=len(rows),
    )


def format_sample_notice(result: SampleResult) -> str:
    if result.dropped == 0:
        return "Sample: all rows retained (no sampling applied)."
    return (
        f"Sample: {result.sampled_count} of {result.original_count} rows retained "
        f"({result.dropped} dropped)."
    )
