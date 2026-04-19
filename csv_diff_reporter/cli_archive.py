"""CLI integration for diff archiving."""
from __future__ import annotations

import argparse

from csv_diff_reporter.diff_archiver import ArchiveEntry, ArchiveOptions, archive_diff
from csv_diff_reporter.differ import DiffResult


def add_archive_args(parser: argparse.ArgumentParser) -> None:
    grp = parser.add_argument_group("archive")
    grp.add_argument("--archive-dir", default="", metavar="DIR",
                     help="Base directory for archives. Enables archiving when set.")
    grp.add_argument("--archive-label", default="", metavar="LABEL",
                     help="Optional label appended to archive folder name.")
    grp.add_argument("--archive-formats", nargs="+",
                     choices=["text", "json", "markdown"],
                     default=["text"],
                     help="Formats to write into the archive (default: text).")


def build_archive_options(args: argparse.Namespace) -> ArchiveOptions | None:
    if not getattr(args, "archive_dir", ""):
        return None
    return ArchiveOptions(
        base_dir=args.archive_dir,
        label=getattr(args, "archive_label", ""),
        formats=getattr(args, "archive_formats", ["text"]),
    )


def apply_archive(result: DiffResult, args: argparse.Namespace) -> ArchiveEntry | None:
    options = build_archive_options(args)
    if options is None:
        return None
    return archive_diff(result, options)


def render_archive_notice(entry: ArchiveEntry | None) -> str:
    if entry is None:
        return ""
    fmts = ", ".join(entry.formats)
    return f"Archived diff to: {entry.path} (formats: {fmts})"
