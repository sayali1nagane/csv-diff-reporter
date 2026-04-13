"""Configuration loader for csv-diff-reporter.

Supports loading default options from a TOML or INI-style config file
(~/.csv_diff_reporter.toml or a path supplied at runtime).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import tomllib  # Python 3.11+
except ImportError:  # pragma: no cover
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:  # pragma: no cover
        tomllib = None  # type: ignore

DEFAULT_CONFIG_PATH = Path.home() / ".csv_diff_reporter.toml"


@dataclass
class AppConfig:
    """Resolved application configuration."""

    key_column: Optional[str] = None
    output_format: str = "text"  # text | json | markdown
    output_file: Optional[str] = None
    ignore_columns: list[str] = field(default_factory=list)
    show_unchanged: bool = False


def _parse_toml(path: Path) -> dict:
    """Read a TOML file and return its contents as a dict."""
    if tomllib is None:
        raise RuntimeError(
            "TOML support requires Python 3.11+ or 'tomli' to be installed."
        )
    with path.open("rb") as fh:
        return tomllib.load(fh)


def load_config(config_path: Optional[str | Path] = None) -> AppConfig:
    """Load configuration from *config_path* (or the default location).

    Missing files are silently ignored – defaults are returned instead.
    Unknown keys in the TOML file are also silently ignored.
    """
    resolved = Path(config_path) if config_path else DEFAULT_CONFIG_PATH

    raw: dict = {}
    if resolved.exists():
        raw = _parse_toml(resolved)

    section: dict = raw.get("csv_diff_reporter", raw)  # support [csv_diff_reporter] table

    return AppConfig(
        key_column=section.get("key_column") or None,
        output_format=section.get("output_format", "text"),
        output_file=section.get("output_file") or None,
        ignore_columns=list(section.get("ignore_columns", [])),
        show_unchanged=bool(section.get("show_unchanged", False)),
    )


def config_from_env() -> dict:
    """Return a partial config dict built from environment variables.

    Environment variables take precedence over file-based config.
    """
    mapping = {}
    if val := os.environ.get("CSV_DIFF_KEY_COLUMN"):
        mapping["key_column"] = val
    if val := os.environ.get("CSV_DIFF_OUTPUT_FORMAT"):
        mapping["output_format"] = val
    if val := os.environ.get("CSV_DIFF_OUTPUT_FILE"):
        mapping["output_file"] = val
    if val := os.environ.get("CSV_DIFF_IGNORE_COLUMNS"):
        mapping["ignore_columns"] = [c.strip() for c in val.split(",") if c.strip()]
    if val := os.environ.get("CSV_DIFF_SHOW_UNCHANGED"):
        mapping["show_unchanged"] = val.lower() in ("1", "true", "yes")
    return mapping


def effective_config(config_path: Optional[str | Path] = None) -> AppConfig:
    """Merge file-based config with environment-variable overrides."""
    cfg = load_config(config_path)
    overrides = config_from_env()
    for key, value in overrides.items():
        setattr(cfg, key, value)
    return cfg
