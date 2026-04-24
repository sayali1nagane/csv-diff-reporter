"""Snapshot module: save and load DiffResult snapshots for later comparison."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from csv_diff_reporter.differ import DiffResult, RowDiff


class SnapshotError(Exception):
    """Raised when a snapshot cannot be saved or loaded."""


@dataclass
class SnapshotOptions:
    path: Path
    label: str = ""


def _row_diff_to_dict(row: RowDiff) -> dict:
    return {
        "key": row.key,
        "change_type": row.change_type,
        "old_fields": row.old_fields,
        "new_fields": row.new_fields,
    }


def _row_diff_from_dict(d: dict) -> RowDiff:
    return RowDiff(
        key=d["key"],
        change_type=d["change_type"],
        old_fields=d.get("old_fields") or {},
        new_fields=d.get("new_fields") or {},
    )


def save_snapshot(result: DiffResult, options: SnapshotOptions) -> Path:
    """Serialise *result* to JSON at *options.path*."""
    options.path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "label": options.label,
        "headers": result.headers,
        "rows": [_row_diff_to_dict(r) for r in result.rows],
    }
    try:
        options.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except OSError as exc:
        raise SnapshotError(f"Cannot write snapshot: {exc}") from exc
    return options.path


def load_snapshot(path: Path) -> DiffResult:
    """Deserialise a DiffResult from a JSON snapshot file."""
    if not path.exists():
        raise SnapshotError(f"Snapshot file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SnapshotError(f"Cannot read snapshot: {exc}") from exc
    return DiffResult(
        headers=payload.get("headers", []),
        rows=[_row_diff_from_dict(r) for r in payload.get("rows", [])],
    )


def snapshot_label(path: Path) -> Optional[str]:
    """Return the label stored inside a snapshot file, or None on failure."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload.get("label") or None
    except (OSError, json.JSONDecodeError):
        return None
