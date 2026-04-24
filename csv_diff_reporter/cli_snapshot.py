"""CLI helpers for the snapshot feature."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from csv_diff_reporter.diff_snapshot import (
    SnapshotError,
    SnapshotOptions,
    load_snapshot,
    save_snapshot,
    snapshot_label,
)
from csv_diff_reporter.differ import DiffResult


def add_snapshot_args(parser: argparse.ArgumentParser) -> None:
    """Register snapshot-related flags on *parser*."""
    grp = parser.add_argument_group("snapshot")
    grp.add_argument(
        "--save-snapshot",
        metavar="FILE",
        default=None,
        help="Save the diff result as a JSON snapshot to FILE.",
    )
    grp.add_argument(
        "--load-snapshot",
        metavar="FILE",
        default=None,
        help="Load a previously saved snapshot and use it as the diff result.",
    )
    grp.add_argument(
        "--snapshot-label",
        metavar="LABEL",
        default="",
        help="Human-readable label stored inside the snapshot file.",
    )


def apply_save_snapshot(
    result: DiffResult, args: argparse.Namespace
) -> Optional[Path]:
    """If --save-snapshot is set, persist *result* and return the path."""
    raw: Optional[str] = getattr(args, "save_snapshot", None)
    if not raw:
        return None
    label: str = getattr(args, "snapshot_label", "") or ""
    opts = SnapshotOptions(path=Path(raw), label=label)
    try:
        return save_snapshot(result, opts)
    except SnapshotError as exc:
        raise SystemExit(f"[snapshot] {exc}") from exc


def apply_load_snapshot(
    result: DiffResult, args: argparse.Namespace
) -> DiffResult:
    """If --load-snapshot is set, return the loaded DiffResult; otherwise *result*."""
    raw: Optional[str] = getattr(args, "load_snapshot", None)
    if not raw:
        return result
    path = Path(raw)
    try:
        loaded = load_snapshot(path)
    except SnapshotError as exc:
        raise SystemExit(f"[snapshot] {exc}") from exc
    return loaded


def render_snapshot_notice(path: Optional[Path]) -> str:
    """Return a human-readable notice for a saved snapshot."""
    if path is None:
        return ""
    label = snapshot_label(path)
    label_part = f" ({label})" if label else ""
    return f"Snapshot saved: {path}{label_part}"
