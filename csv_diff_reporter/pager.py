"""Pagination utilities for large diff results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from csv_diff_reporter.differ import DiffResult, RowDiff


@dataclass
class PageResult:
    """A single page of diff rows."""

    rows: List[RowDiff]
    page: int
    page_size: int
    total_rows: int

    @property
    def total_pages(self) -> int:
        if self.page_size <= 0:
            return 1
        return max(1, (self.total_rows + self.page_size - 1) // self.page_size)

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1


def paginate_diff(result: DiffResult, page: int = 1, page_size: int = 50) -> PageResult:
    """Return a PageResult containing the requested slice of diff rows.

    Args:
        result: The full DiffResult to paginate.
        page: 1-based page number.
        page_size: Number of rows per page.  Use 0 to return all rows.

    Returns:
        PageResult with the appropriate slice of rows.

    Raises:
        ValueError: If *page* is less than 1 or *page_size* is negative.
    """
    if page < 1:
        raise ValueError(f"page must be >= 1, got {page}")
    if page_size < 0:
        raise ValueError(f"page_size must be >= 0, got {page_size}")

    all_rows: List[RowDiff] = list(result.added) + list(result.removed) + list(result.modified)
    total = len(all_rows)

    if page_size == 0:
        return PageResult(rows=all_rows, page=1, page_size=total or 1, total_rows=total)

    start = (page - 1) * page_size
    end = start + page_size
    sliced = all_rows[start:end]

    return PageResult(rows=sliced, page=page, page_size=page_size, total_rows=total)
