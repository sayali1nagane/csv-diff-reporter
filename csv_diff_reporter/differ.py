"""Core diffing logic for comparing two CSV datasets."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RowDiff:
    """Represents a single row-level change between two CSV files."""

    key: str
    change_type: str  # 'added', 'removed', 'modified'
    old_row: dict[str, Any] | None = None
    new_row: dict[str, Any] | None = None
    changed_fields: dict[str, tuple[Any, Any]] = field(default_factory=dict)


@dataclass
class DiffResult:
    """Aggregated result of comparing two CSV datasets."""

    added: list[RowDiff] = field(default_factory=list)
    removed: list[RowDiff] = field(default_factory=list)
    modified: list[RowDiff] = field(default_factory=list)

    @property
    def total_changes(self) -> int:
        return len(self.added) + len(self.removed) + len(self.modified)

    @property
    def is_empty(self) -> bool:
        return self.total_changes == 0

    def summary(self) -> str:
        """Return a human-readable summary of the diff result."""
        return (
            f"{len(self.added)} added, "
            f"{len(self.removed)} removed, "
            f"{len(self.modified)} modified "
            f"({self.total_changes} total)"
        )


def diff_csv(
    old_data: dict[str, dict[str, Any]],
    new_data: dict[str, dict[str, Any]],
) -> DiffResult:
    """Compare two CSV datasets (keyed dicts) and return a DiffResult.

    Args:
        old_data: Mapping of row key -> row dict from the original CSV.
        new_data: Mapping of row key -> row dict from the updated CSV.

    Returns:
        A DiffResult containing added, removed, and modified rows.
    """
    result = DiffResult()

    old_keys = set(old_data)
    new_keys = set(new_data)

    for key in sorted(new_keys - old_keys):
        result.added.append(
            RowDiff(key=key, change_type="added", new_row=new_data[key])
        )

    for key in sorted(old_keys - new_keys):
        result.removed.append(
            RowDiff(key=key, change_type="removed", old_row=old_data[key])
        )

    for key in sorted(old_keys & new_keys):
        old_row = old_data[key]
        new_row = new_data[key]
        all_fields = set(old_row) | set(new_row)
        changed: dict[str, tuple[Any, Any]] = {
            f: (old_row.get(f), new_row.get(f))
            for f in all_fields
            if old_row.get(f) != new_row.get(f)
        }
        if changed:
            result.modified.append(
                RowDiff(
                    key=key,
                    change_type="modified",
                    old_row=old_row,
                    new_row=new_row,
                    changed_fields=changed,
                )
            )

    return result
