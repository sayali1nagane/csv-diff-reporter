"""Load a ColumnSchema spec from a TOML or dict configuration."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from csv_diff_reporter.schema import ColumnSchema, SchemaSpec

try:
    import tomllib  # Python 3.11+
except ImportError:  # pragma: no cover
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:  # pragma: no cover
        tomllib = None  # type: ignore


class SchemaLoadError(Exception):
    """Raised when a schema file cannot be loaded or parsed."""


def _parse_column(data: Dict[str, Any]) -> ColumnSchema:
    return ColumnSchema(
        required=bool(data.get("required", False)),
        expected_type=data.get("type"),
        max_length=data.get("max_length"),
        allowed_values=data.get("allowed_values"),
    )


def schema_from_dict(raw: Dict[str, Any]) -> SchemaSpec:
    """Build a SchemaSpec from a plain dict (e.g. parsed TOML)."""
    columns_section: Dict[str, Any] = raw.get("columns", raw)
    return {
        col_name: _parse_column(col_def)
        for col_name, col_def in columns_section.items()
        if isinstance(col_def, dict)
    }


def load_schema(path: Optional[str | Path]) -> SchemaSpec:
    """Load a SchemaSpec from a TOML file.  Returns empty spec if path is None."""
    if path is None:
        return {}
    path = Path(path)
    if not path.exists():
        raise SchemaLoadError(f"Schema file not found: {path}")
    if tomllib is None:  # pragma: no cover
        raise SchemaLoadError(
            "TOML support requires Python 3.11+ or 'tomli' package."
        )
    try:
        with path.open("rb") as fh:
            raw = tomllib.load(fh)
    except Exception as exc:  # pragma: no cover
        raise SchemaLoadError(f"Failed to parse schema file {path}: {exc}") from exc
    return schema_from_dict(raw)
