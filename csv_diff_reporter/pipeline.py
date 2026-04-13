"""High-level pipeline that wires parser, differ, summary, and formatter."""
from dataclasses import dataclass
from typing import Optional

from csv_diff_reporter.parser import load_csv, get_row_count, CSVParseError
from csv_diff_reporter.differ import diff_csv, DiffResult
from csv_diff_reporter.summary import DiffSummary, compute_summary
from csv_diff_reporter.formatter import format_output
from csv_diff_reporter.validator import validate_inputs, ValidationError


@dataclass
class PipelineResult:
    """Container for all artefacts produced by the pipeline."""
    diff: DiffResult
    summary: DiffSummary
    output: str


def run_pipeline(
    file_a: str,
    file_b: str,
    key_column: Optional[str] = None,
    output_format: str = "text",
) -> PipelineResult:
    """Execute the full diff pipeline and return structured results.

    Args:
        file_a: Path to the original CSV file.
        file_b: Path to the new CSV file.
        key_column: Column name to use as row identifier. If None, row index
                    is used.
        output_format: One of 'text', 'json', or 'markdown'.

    Returns:
        A PipelineResult containing the diff, summary, and formatted output.

    Raises:
        ValidationError: If either file path fails validation.
        CSVParseError: If a file cannot be parsed.
        ValueError: If output_format is not recognised.
    """
    validation = validate_inputs(file_a, file_b)
    if not validation:
        raise ValidationError(str(validation))

    rows_a = load_csv(file_a, key_column=key_column)
    rows_b = load_csv(file_b, key_column=key_column)

    count_a = get_row_count(file_a)
    count_b = get_row_count(file_b)

    diff = diff_csv(rows_a, rows_b)
    summary = compute_summary(diff, total_rows_old=count_a, total_rows_new=count_b)
    output = format_output(diff, fmt=output_format)

    return PipelineResult(diff=diff, summary=summary, output=output)
