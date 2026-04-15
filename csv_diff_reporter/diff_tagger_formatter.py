"""Format a TaggedResult as plain text or JSON."""
from __future__ import annotations

import json
from typing import List

from csv_diff_reporter.diff_tagger import TaggedResult, TaggedRow


def _row_to_dict(tagged: TaggedRow) -> dict:
    return {
        "key": tagged.row.key,
        "change_type": tagged.row.change_type,
        "tags": tagged.tags,
        "old": tagged.row.old_fields,
        "new": tagged.row.new_fields,
    }


def _as_text(result: TaggedResult) -> str:
    if not result.rows:
        return "No tagged rows."

    lines: List[str] = []
    for tagged in result.rows:
        tag_str = ", ".join(tagged.tags) if tagged.tags else "(none)"
        lines.append(
            f"[{tagged.row.change_type.upper()}] key={tagged.row.key}  tags=[{tag_str}]"
        )
    return "\n".join(lines)


def _as_json(result: TaggedResult) -> str:
    payload = {
        "headers": result.headers,
        "all_tags": result.all_tags(),
        "rows": [_row_to_dict(r) for r in result.rows],
    }
    return json.dumps(payload, indent=2)


def format_tagged(result: TaggedResult, fmt: str = "text") -> str:
    """Render *result* as *fmt* (``'text'`` or ``'json'``)."""
    if fmt == "json":
        return _as_json(result)
    return _as_text(result)
