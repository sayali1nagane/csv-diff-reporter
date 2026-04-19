"""Format a ProfileResult as text or JSON."""
from __future__ import annotations
import json
from csv_diff_reporter.diff_profiler import ProfileResult


def _as_text(result: ProfileResult) -> str:
    if not result.profiles:
        return "No profile data available.\n"
    lines = ["Field Value Profiles", "=" * 40]
    for col, profile in result.profiles.items():
        lines.append(f"\nColumn: {col}")
        lines.append(f"  Total values : {profile.total_values}")
        lines.append(f"  Unique values: {profile.unique_values}")
        if profile.top_values:
            lines.append("  Top values:")
            for val, count in profile.top_values:
                display = val if val != "" else "(empty)"
                lines.append(f"    {display!r}: {count}")
    lines.append("")
    return "\n".join(lines)


def _as_json(result: ProfileResult) -> str:
    return json.dumps(result.as_dict(), indent=2)


def format_profile(result: ProfileResult, fmt: str = "text") -> str:
    """Return formatted profile. fmt is 'text' or 'json'."""
    if fmt == "json":
        return _as_json(result)
    return _as_text(result)
