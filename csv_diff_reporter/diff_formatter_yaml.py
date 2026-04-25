"""Format a DiffResult as YAML output."""
from __future__ import annotations

from typing import Any

from csv_diff_reporter.differ import DiffResult, RowDiff


def _escape_str(value: str) -> str:
    """Wrap value in quotes if it contains special YAML characters."""
    specials = (':', '{', '}', '[', ']', ',', '#', '&', '*', '?', '|', '-', '<', '>', '=', '!')
    if any(c in value for c in specials) or value == '' or value.lower() in ('true', 'false', 'null', 'yes', 'no'):
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'
    return value


def _fields_to_yaml(fields: dict[str, str], indent: int) -> list[str]:
    pad = ' ' * indent
    lines = []
    for key, val in fields.items():
        lines.append(f"{pad}{_escape_str(key)}: {_escape_str(val)}")
    return lines


def _row_to_yaml(row: RowDiff, indent: int = 4) -> list[str]:
    pad = ' ' * indent
    lines = [f"{pad}- key: {_escape_str(row.key)}"]
    lines.append(f"{pad}  change_type: {row.change_type}")
    if row.old_fields:
        lines.append(f"{pad}  old_fields:")
        lines.extend(_fields_to_yaml(row.old_fields, indent + 4))
    if row.new_fields:
        lines.append(f"{pad}  new_fields:")
        lines.extend(_fields_to_yaml(row.new_fields, indent + 4))
    return lines


def format_diff_as_yaml(result: DiffResult) -> str:
    """Render *result* as a YAML document string."""
    lines: list[str] = []
    lines.append("diff_report:")
    lines.append(f"  added: {len([r for r in result.rows if r.change_type == 'added'])}")
    lines.append(f"  removed: {len([r for r in result.rows if r.change_type == 'removed'])}")
    lines.append(f"  modified: {len([r for r in result.rows if r.change_type == 'modified'])}")
    lines.append(f"  headers: [{', '.join(_escape_str(h) for h in result.headers)}]")
    lines.append("  rows:")
    if not result.rows:
        lines.append("    []")
    else:
        for row in result.rows:
            lines.extend(_row_to_yaml(row, indent=4))
    return '\n'.join(lines) + '\n'
