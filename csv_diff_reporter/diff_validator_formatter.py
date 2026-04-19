"""Format ThresholdResult for CLI output."""
from __future__ import annotations
import json
from csv_diff_reporter.diff_validator import ThresholdResult


def _as_text(result: ThresholdResult) -> str:
    if result.is_valid():
        return "Threshold validation passed."
    lines = ["Threshold validation FAILED:"] + [
        f"  [{v.rule}] limit={v.limit}, actual={v.actual}"
        for v in result.violations
    ]
    return "\n".join(lines)


def _as_json(result: ThresholdResult) -> str:
    return json.dumps(
        {
            "passed": result.is_valid(),
            "violations": [v.as_dict() for v in result.violations],
        },
        indent=2,
    )


def format_threshold_result(result: ThresholdResult, fmt: str = "text") -> str:
    if fmt == "json":
        return _as_json(result)
    return _as_text(result)
