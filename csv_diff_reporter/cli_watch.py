"""CLI helpers for the --watch flag."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from csv_diff_reporter.diff_watcher import WatchOptions, watch
from csv_diff_reporter.pipeline import PipelineResult, run_pipeline


def add_watch_args(parser: argparse.ArgumentParser) -> None:
    """Register watch-related CLI flags on *parser*."""
    group = parser.add_argument_group("watch")
    group.add_argument(
        "--watch",
        action="store_true",
        default=False,
        help="Re-run the diff whenever either input file changes.",
    )
    group.add_argument(
        "--watch-interval",
        type=float,
        default=2.0,
        metavar="SECONDS",
        help="Polling interval in seconds (default: 2.0).",
    )


def _make_on_change(args: argparse.Namespace) -> None:
    """Build a callback that re-runs the pipeline and prints output."""

    def _callback(path_a: Path, path_b: Path) -> None:
        print(f"[watch] change detected — re-running diff ...", file=sys.stderr)
        result: PipelineResult = run_pipeline(
            path_a=path_a,
            path_b=path_b,
            key_column=getattr(args, "key", None),
        )
        if result.report:
            print(result.report)
        else:
            print("(no differences)", file=sys.stderr)

    return _callback


def apply_watch(args: argparse.Namespace, remaining_argv: List[str]) -> bool:
    """If --watch is set, start the watch loop and return True.

    Returns False when the flag is absent so the caller can proceed normally.
    """
    if not getattr(args, "watch", False):
        return False

    path_a = Path(args.file_a)
    path_b = Path(args.file_b)
    options = WatchOptions(
        interval=getattr(args, "watch_interval", 2.0),
        on_change=_make_on_change(args),
    )
    print(
        f"[watch] watching {path_a} and {path_b} "
        f"(interval={options.interval}s) — press Ctrl-C to stop",
        file=sys.stderr,
    )
    try:
        watch(path_a, path_b, options)
    except KeyboardInterrupt:
        print("\n[watch] stopped.", file=sys.stderr)
    return True
