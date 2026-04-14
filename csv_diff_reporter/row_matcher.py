"""Fuzzy row matching: find the closest row in the other file for unmatched rows."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from csv_diff_reporter.differ import RowDiff


@dataclass
class MatchScore:
    key: str
    score: float  # 0.0 – 1.0, higher is more similar
    fields: Dict[str, Tuple[str, str]] = field(default_factory=dict)


@dataclass
class MatchResult:
    row_diff: RowDiff
    best_match: Optional[MatchScore] = None

    @property
    def has_match(self) -> bool:
        return self.best_match is not None


def _field_similarity(a: str, b: str) -> float:
    """Simple character-level Jaccard similarity between two strings."""
    if a == b:
        return 1.0
    set_a = set(a.lower())
    set_b = set(b.lower())
    if not set_a and not set_b:
        return 1.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


def _row_similarity(
    row_a: Dict[str, str],
    row_b: Dict[str, str],
) -> Tuple[float, Dict[str, Tuple[str, str]]]:
    """Return (mean similarity score, per-field comparison dict)."""
    common_keys = set(row_a) & set(row_b)
    if not common_keys:
        return 0.0, {}
    fields: Dict[str, Tuple[str, str]] = {}
    total = 0.0
    for k in common_keys:
        sim = _field_similarity(row_a[k], row_b[k])
        total += sim
        fields[k] = (row_a[k], row_b[k])
    return total / len(common_keys), fields


def find_best_match(
    target_row: Dict[str, str],
    candidates: List[Tuple[str, Dict[str, str]]],
    threshold: float = 0.6,
) -> Optional[MatchScore]:
    """Return the best-matching candidate above *threshold*, or None."""
    best: Optional[MatchScore] = None
    for key, row in candidates:
        score, fields = _row_similarity(target_row, row)
        if score >= threshold and (best is None or score > best.score):
            best = MatchScore(key=key, score=score, fields=fields)
    return best


def match_unmatched_rows(
    diffs: List[RowDiff],
    all_rows: Dict[str, Dict[str, str]],
    threshold: float = 0.6,
) -> List[MatchResult]:
    """For every added/removed row in *diffs*, attempt to find a fuzzy match."""
    candidates = list(all_rows.items())
    results: List[MatchResult] = []
    for diff in diffs:
        if diff.change_type not in ("added", "removed"):
            continue
        row_data = diff.new_row if diff.change_type == "added" else diff.old_row
        if row_data is None:
            results.append(MatchResult(row_diff=diff))
            continue
        match = find_best_match(row_data, candidates, threshold=threshold)
        results.append(MatchResult(row_diff=diff, best_match=match))
    return results
