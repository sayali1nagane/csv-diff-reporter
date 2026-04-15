"""Tag diff rows with arbitrary labels for downstream filtering or reporting."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from csv_diff_reporter.differ import DiffResult, RowDiff


@dataclass
class TagOptions:
    """Configuration for the tagging pass."""
    rules: List["TagRule"] = field(default_factory=list)


@dataclass
class TagRule:
    """A single tagging rule: if *predicate* matches a row, apply *tag*."""
    tag: str
    predicate: Callable[[RowDiff], bool]


@dataclass
class TaggedRow:
    """A RowDiff decorated with a set of string tags."""
    row: RowDiff
    tags: List[str] = field(default_factory=list)

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags


@dataclass
class TaggedResult:
    """Collection of tagged rows together with the original headers."""
    headers: List[str]
    rows: List[TaggedRow] = field(default_factory=list)

    def with_tag(self, tag: str) -> List[TaggedRow]:
        """Return only rows that carry *tag*."""
        return [r for r in self.rows if r.has_tag(tag)]

    def all_tags(self) -> List[str]:
        """Sorted list of every distinct tag present in the result."""
        tags: set[str] = set()
        for r in self.rows:
            tags.update(r.tags)
        return sorted(tags)


def tag_diff(result: DiffResult, options: Optional[TagOptions] = None) -> TaggedResult:
    """Apply *options* rules to every row in *result* and return a TaggedResult."""
    if options is None:
        options = TagOptions()

    tagged_rows: List[TaggedRow] = []
    for row in result.rows:
        tags = [rule.tag for rule in options.rules if rule.predicate(row)]
        tagged_rows.append(TaggedRow(row=row, tags=tags))

    return TaggedResult(headers=list(result.headers), rows=tagged_rows)
