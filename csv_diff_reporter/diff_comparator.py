"""Compare two DiffResult objects and produce a comparison report."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict
from csv_diff_reporter.differ import DiffResult


@dataclass
class ComparisonResult:
    added_only_in_a: int = 0
    added_only_in_b: int = 0
    removed_only_in_a: int = 0
    removed_only_in_b: int = 0
    modified_only_in_a: int = 0
    modified_only_in_b: int = 0
    common_added: int = 0
    common_removed: int = 0
    common_modified: int = 0
    labels: Dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "added_only_in_a": self.added_only_in_a,
            "added_only_in_b": self.added_only_in_b,
            "removed_only_in_a": self.removed_only_in_a,
            "removed_only_in_b": self.removed_only_in_b,
            "modified_only_in_a": self.modified_only_in_a,
            "modified_only_in_b": self.modified_only_in_b,
            "common_added": self.common_added,
            "common_removed": self.common_removed,
            "common_modified": self.common_modified,
        }


def _keys_by_type(diff: DiffResult, change_type: str):
    return {r.key for r in diff.rows if r.change_type == change_type}


def compare_diffs(
    a: DiffResult,
    b: DiffResult,
    label_a: str = "A",
    label_b: str = "B",
) -> ComparisonResult:
    result = ComparisonResult(labels={"a": label_a, "b": label_b})

    for change_type in ("added", "removed", "modified"):
        keys_a = _keys_by_type(a, change_type)
        keys_b = _keys_by_type(b, change_type)
        common = len(keys_a & keys_b)
        only_a = len(keys_a - keys_b)
        only_b = len(keys_b - keys_a)
        setattr(result, f"common_{change_type}", common)
        setattr(result, f"{change_type}_only_in_a", only_a)
        setattr(result, f"{change_type}_only_in_b", only_b)

    return result
