"""Row limit feature: cap the number of rows processed from each CSV file."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class RowLimitOptions:
    max_rows: Optional[int] = None  # None means no limit
    warn_on_truncation: bool = True


@dataclass
class RowLimitResult:
    data: Dict[str, List[dict]]
    original_count: int
    limited_count: int
    was_limited: bool

    @property
    def dropped(self) -> int:
        return self.original_count - self.limited_count


def apply_row_limit(
    data: Dict[str, List[dict]],
    options: RowLimitOptions,
) -> RowLimitResult:
    """Apply a row limit to a keyed CSV data dict.

    Parameters
    ----------
    data:
        Mapping of row-key -> list-of-field-dicts as returned by ``load_csv``.
    options:
        Limit configuration.

    Returns
    -------
    RowLimitResult
        Wrapper containing the (possibly truncated) data and metadata.
    """
    original_count = len(data)

    if options.max_rows is None or original_count <= options.max_rows:
        return RowLimitResult(
            data=data,
            original_count=original_count,
            limited_count=original_count,
            was_limited=False,
        )

    keys = list(data.keys())[: options.max_rows]
    limited_data = {k: data[k] for k in keys}

    return RowLimitResult(
        data=limited_data,
        original_count=original_count,
        limited_count=options.max_rows,
        was_limited=True,
    )


def format_row_limit_warning(result: RowLimitResult) -> str:
    """Return a human-readable warning string when rows were dropped."""
    if not result.was_limited:
        return ""
    return (
        f"Warning: input truncated to {result.limited_count} rows "
        f"({result.dropped} row(s) omitted)."
    )
