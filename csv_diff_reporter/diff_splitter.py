"""Split a DiffResult into multiple chunks by change type or row count."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from csv_diff_reporter.differ import DiffResult, RowDiff


@dataclass
class SplitOptions:
    chunk_size: Optional[int] = None  # max rows per chunk; None = no limit
    by_type: bool = False             # split into separate buckets per change type


@dataclass
class SplitResult:
    chunks: List[DiffResult] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)  # human-readable label per chunk

    @property
    def count(self) -> int:
        return len(self.chunks)


def _make_diff(rows: List[RowDiff], source: DiffResult) -> DiffResult:
    """Build a new DiffResult with a subset of rows, preserving headers."""
    return DiffResult(
        headers=source.headers,
        rows=rows,
    )


def _chunk_rows(rows: List[RowDiff], size: int) -> List[List[RowDiff]]:
    """Partition *rows* into consecutive sublists of at most *size* items."""
    if size <= 0:
        raise ValueError("chunk_size must be a positive integer")
    return [rows[i : i + size] for i in range(0, max(len(rows), 1), size)] if rows else [[]]


def split_diff(result: DiffResult, options: Optional[SplitOptions] = None) -> SplitResult:
    """Split *result* according to *options* and return a SplitResult."""
    if options is None:
        options = SplitOptions()

    if options.by_type:
        buckets = {
            "added": [r for r in result.rows if r.change_type == "added"],
            "removed": [r for r in result.rows if r.change_type == "removed"],
            "modified": [r for r in result.rows if r.change_type == "modified"],
        }
        split = SplitResult()
        for label, rows in buckets.items():
            if options.chunk_size:
                for idx, chunk in enumerate(_chunk_rows(rows, options.chunk_size), 1):
                    split.chunks.append(_make_diff(chunk, result))
                    split.labels.append(f"{label} (part {idx})")
            else:
                split.chunks.append(_make_diff(rows, result))
                split.labels.append(label)
        return split

    if options.chunk_size:
        split = SplitResult()
        for idx, chunk in enumerate(_chunk_rows(result.rows, options.chunk_size), 1):
            split.chunks.append(_make_diff(chunk, result))
            split.labels.append(f"part {idx}")
        return split

    # No splitting at all — return the whole result as a single chunk.
    return SplitResult(chunks=[result], labels=["all"])
