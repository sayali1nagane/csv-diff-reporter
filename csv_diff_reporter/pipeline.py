"""High-level pipeline: load → validate → diff → export."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from csv_diff_reporter.validator import validate_inputs, ValidationError
from csv_diff_reporter.parser import load_csv, CSVParseError
from csv_diff_reporter.differ import diff_csv, DiffResult
from csv_diff_reporter.summary import compute_summary, DiffSummary
from csv_diff_reporter.exporter import export, ExportError


@dataclass
class PipelineResult:
    success: bool
    diff: Optional[DiffResult] = None
    summary: Optional[DiffSummary] = None
    error: str = ""
    warnings: list[str] = field(default_factory=list)


def run_pipeline(
    file_a: Path,
    file_b: Path,
    key_column: Optional[str] = None,
    fmt: str = "text",
    output_path: Optional[Path] = None,
) -> PipelineResult:
    """Execute the full diff pipeline and return a :class:`PipelineResult`."""
    # 1. Validate inputs
    try:
        validation = validate_inputs(file_a, file_b)
        if not validation:
            return PipelineResult(success=False, error=str(validation))
    except ValidationError as exc:
        return PipelineResult(success=False, error=str(exc))

    # 2. Parse CSV files
    try:
        rows_a = load_csv(file_a, key_column=key_column)
        rows_b = load_csv(file_b, key_column=key_column)
    except CSVParseError as exc:
        return PipelineResult(success=False, error=str(exc))

    # 3. Diff
    diff = diff_csv(rows_a, rows_b)

    # 4. Summarise
    summary = compute_summary(diff)

    # 5. Export
    try:
        export(diff, fmt=fmt, output_path=output_path)
    except ExportError as exc:
        return PipelineResult(
            success=False,
            diff=diff,
            summary=summary,
            error=str(exc),
        )

    return PipelineResult(success=True, diff=diff, summary=summary)
