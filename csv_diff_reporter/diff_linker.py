"""diff_linker.py — Cross-reference rows between two DiffResult objects by a shared key.

Provides `link_diffs`, which pairs rows from two separate diff results that
share the same row key, enabling side-by-side comparison across multiple
diff runs (e.g. comparing Monday's diff with Tuesday's diff).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from csv_diff_reporter.differ import DiffResult, RowDiff


@dataclass(frozen=True)
class LinkedRow:
    """A pair of RowDiff entries that share the same row key."""

    key: str
    left: Optional[RowDiff]   # row from the first (left) diff, or None
    right: Optional[RowDiff]  # row from the second (right) diff, or None

    @property
    def in_both(self) -> bool:
        """True when the key appears in both diffs."""
        return self.left is not None and self.right is not None

    @property
    def left_only(self) -> bool:
        """True when the key appears only in the left diff."""
        return self.left is not None and self.right is None

    @property
    def right_only(self) -> bool:
        """True when the key appears only in the right diff."""
        return self.left is None and self.right is not None

    def as_dict(self) -> dict:
        """Serialise to a plain dictionary."""
        return {
            "key": self.key,
            "in_both": self.in_both,
            "left_only": self.left_only,
            "right_only": self.right_only,
            "left_change_type": self.left.change_type if self.left else None,
            "right_change_type": self.right.change_type if self.right else None,
        }


@dataclass
class LinkResult:
    """Outcome of linking two DiffResult objects."""

    rows: List[LinkedRow] = field(default_factory=list)
    left_headers: List[str] = field(default_factory=list)
    right_headers: List[str] = field(default_factory=list)

    # ------------------------------------------------------------------ counts

    @property
    def total(self) -> int:
        return len(self.rows)

    @property
    def shared_count(self) -> int:
        return sum(1 for r in self.rows if r.in_both)

    @property
    def left_only_count(self) -> int:
        return sum(1 for r in self.rows if r.left_only)

    @property
    def right_only_count(self) -> int:
        return sum(1 for r in self.rows if r.right_only)

    def get(self, key: str) -> Optional[LinkedRow]:
        """Return the LinkedRow for *key*, or None if not present."""
        for row in self.rows:
            if row.key == key:
                return row
        return None

    def as_dict(self) -> dict:
        return {
            "total": self.total,
            "shared": self.shared_count,
            "left_only": self.left_only_count,
            "right_only": self.right_only_count,
            "rows": [r.as_dict() for r in self.rows],
        }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _index_rows(diff: DiffResult) -> Dict[str, RowDiff]:
    """Build a mapping from row key → RowDiff for every changed row."""
    index: Dict[str, RowDiff] = {}
    for row in diff.rows:
        # Use the first value in old_fields or new_fields as the key when the
        # RowDiff does not carry an explicit key attribute.  The key column is
        # stored as the first field in new_fields (added/modified) or
        # old_fields (removed).
        fields = row.new_fields if row.new_fields else row.old_fields
        row_key = row.key if hasattr(row, "key") and row.key else next(iter(fields.values()), "")
        index[str(row_key)] = row
    return index


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def link_diffs(left: DiffResult, right: DiffResult) -> LinkResult:
    """Cross-reference *left* and *right* DiffResult objects by row key.

    Rows that appear in both diffs are paired; rows that appear in only one
    diff are included with ``None`` on the absent side.

    Args:
        left:  The first DiffResult (e.g. from an earlier comparison run).
        right: The second DiffResult (e.g. from a later comparison run).

    Returns:
        A :class:`LinkResult` containing all :class:`LinkedRow` pairs.
    """
    left_index = _index_rows(left)
    right_index = _index_rows(right)

    all_keys: List[str] = list(left_index.keys())
    for k in right_index:
        if k not in left_index:
            all_keys.append(k)

    linked: List[LinkedRow] = [
        LinkedRow(
            key=k,
            left=left_index.get(k),
            right=right_index.get(k),
        )
        for k in all_keys
    ]

    return LinkResult(
        rows=linked,
        left_headers=list(left.headers),
        right_headers=list(right.headers),
    )
