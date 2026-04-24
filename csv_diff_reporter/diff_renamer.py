"""Rename row keys in a DiffResult using a mapping of old key -> new key."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from csv_diff_reporter.differ import DiffResult, RowDiff


@dataclass
class KeyRenameOptions:
    """Options controlling how row keys are renamed."""

    mapping: Dict[str, str] = field(default_factory=dict)
    # When True, keys not present in *mapping* are left unchanged.
    # When False (strict), keys not in mapping raise ValueError.
    passthrough: bool = True


def _rename_key(key: str, options: KeyRenameOptions) -> str:
    if key in options.mapping:
        return options.mapping[key]
    if options.passthrough:
        return key
    raise ValueError(f"Key {key!r} not found in rename mapping and passthrough is disabled.")


def _rename_row(row: RowDiff, options: KeyRenameOptions) -> RowDiff:
    new_key = _rename_key(row.key, options)
    return RowDiff(
        key=new_key,
        change_type=row.change_type,
        old_fields=row.old_fields,
        new_fields=row.new_fields,
    )


def rename_keys(result: DiffResult, options: Optional[KeyRenameOptions] = None) -> DiffResult:
    """Return a new DiffResult with row keys renamed according to *options*.

    If *options* is None or the mapping is empty the original object is
    returned unchanged (no copy is made).
    """
    if options is None or not options.mapping:
        return result

    renamed_rows = [_rename_row(row, options) for row in result.rows]
    return DiffResult(
        headers=result.headers,
        rows=renamed_rows,
    )


def format_rename_notice(options: KeyRenameOptions) -> str:
    """Return a human-readable summary of the renames that were applied."""
    if not options.mapping:
        return "No key renames applied."
    lines = ["Key renames applied:"]
    for old, new in sorted(options.mapping.items()):
        lines.append(f"  {old!r} -> {new!r}")
    return "\n".join(lines)
