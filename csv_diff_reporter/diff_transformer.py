"""Apply field-level transformations to a DiffResult before reporting."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from csv_diff_reporter.differ import DiffResult, RowDiff


TransformFn = Callable[[str], str]


@dataclass
class TransformOptions:
    """Column-to-transform-function mapping plus an optional catch-all."""
    column_transforms: Dict[str, TransformFn] = field(default_factory=dict)
    default_transform: Optional[TransformFn] = None


@dataclass
class TransformResult:
    result: DiffResult
    columns_affected: List[str]


def _apply(value: str, fn: Optional[TransformFn]) -> str:
    if fn is None:
        return value
    try:
        return fn(value)
    except Exception:
        return value


def _transform_fields(
    fields: Dict[str, str],
    opts: TransformOptions,
) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for col, val in fields.items():
        fn = opts.column_transforms.get(col, opts.default_transform)
        out[col] = _apply(val, fn)
    return out


def _transform_row(row: RowDiff, opts: TransformOptions) -> RowDiff:
    return RowDiff(
        change_type=row.change_type,
        key=row.key,
        old_fields=_transform_fields(row.old_fields, opts) if row.old_fields else row.old_fields,
        new_fields=_transform_fields(row.new_fields, opts) if row.new_fields else row.new_fields,
    )


def transform_diff(result: DiffResult, opts: Optional[TransformOptions] = None) -> TransformResult:
    """Return a new DiffResult with field values transformed according to *opts*."""
    if opts is None or (not opts.column_transforms and opts.default_transform is None):
        return TransformResult(result=result, columns_affected=[])

    transformed_rows = [_transform_row(r, opts) for r in result.rows]
    new_result = DiffResult(
        headers=result.headers,
        rows=transformed_rows,
    )

    affected = list(opts.column_transforms.keys())
    if opts.default_transform is not None and "*" not in affected:
        affected.append("*")

    return TransformResult(result=new_result, columns_affected=affected)
