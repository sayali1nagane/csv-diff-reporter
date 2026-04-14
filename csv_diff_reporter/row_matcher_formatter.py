"""Format fuzzy match results for human-readable output."""
from __future__ import annotations

import json
from typing import List

from csv_diff_reporter.row_matcher import MatchResult


def _score_bar(score: float, width: int = 10) -> str:
    filled = round(score * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def _format_match_text(result: MatchResult) -> str:
    diff = result.row_diff
    change = diff.change_type.upper()
    key = diff.key
    lines = [f"  {change} row (key={key!r})"]
    if result.best_match is None:
        lines.append("    No close match found in opposite file.")
    else:
        m = result.best_match
        bar = _score_bar(m.score)
        lines.append(f"    Best match: key={m.key!r}  score={m.score:.2f} {bar}")
        for col, (old, new) in list(m.fields.items())[:5]:
            lines.append(f"      {col}: {old!r} -> {new!r}")
        if len(m.fields) > 5:
            lines.append(f"      ... and {len(m.fields) - 5} more field(s)")
    return "\n".join(lines)


def format_match_results(results: List[MatchResult], fmt: str = "text") -> str:
    """Return a formatted string for all match results.

    Parameters
    ----------
    results:
        Output of :func:`~csv_diff_reporter.row_matcher.match_unmatched_rows`.
    fmt:
        ``"text"`` (default) or ``"json"``.
    """
    if not results:
        if fmt == "json":
            return json.dumps([], indent=2)
        return "No unmatched rows to analyse.\n"

    if fmt == "json":
        payload = []
        for r in results:
            entry: dict = {
                "key": r.row_diff.key,
                "change_type": r.row_diff.change_type,
                "best_match": None,
            }
            if r.best_match:
                entry["best_match"] = {
                    "key": r.best_match.key,
                    "score": round(r.best_match.score, 4),
                    "fields": {
                        col: {"old": old, "new": new}
                        for col, (old, new) in r.best_match.fields.items()
                    },
                }
            payload.append(entry)
        return json.dumps(payload, indent=2)

    header = "=== Fuzzy Row Match Analysis ==="
    body = "\n".join(_format_match_text(r) for r in results)
    return f"{header}\n{body}\n"
