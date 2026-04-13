"""Tests for csv_diff_reporter.pager."""

from __future__ import annotations

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.pager import PageResult, paginate_diff


def _row(key: str, change: str) -> RowDiff:
    return RowDiff(key=key, change_type=change, old_row={}, new_row={})


def _result(n_added: int = 0, n_removed: int = 0, n_modified: int = 0) -> DiffResult:
    added = [_row(f"a{i}", "added") for i in range(n_added)]
    removed = [_row(f"r{i}", "removed") for i in range(n_removed)]
    modified = [_row(f"m{i}", "modified") for i in range(n_modified)]
    return DiffResult(added=added, removed=removed, modified=modified)


def test_paginate_empty_result():
    result = _result()
    page = paginate_diff(result, page=1, page_size=10)
    assert page.rows == []
    assert page.total_rows == 0
    assert page.total_pages == 1
    assert not page.has_next
    assert not page.has_prev


def test_paginate_first_page():
    result = _result(n_added=5, n_removed=5)
    page = paginate_diff(result, page=1, page_size=4)
    assert len(page.rows) == 4
    assert page.page == 1
    assert page.total_rows == 10
    assert page.total_pages == 3
    assert page.has_next
    assert not page.has_prev


def test_paginate_last_page_partial():
    result = _result(n_added=7)
    page = paginate_diff(result, page=2, page_size=5)
    assert len(page.rows) == 2
    assert page.page == 2
    assert page.total_pages == 2
    assert not page.has_next
    assert page.has_prev


def test_paginate_beyond_last_page_returns_empty():
    result = _result(n_added=3)
    page = paginate_diff(result, page=5, page_size=3)
    assert page.rows == []
    assert page.total_rows == 3


def test_paginate_page_size_zero_returns_all():
    result = _result(n_added=3, n_removed=2)
    page = paginate_diff(result, page=1, page_size=0)
    assert len(page.rows) == 5
    assert page.total_pages == 1
    assert not page.has_next


def test_paginate_invalid_page_raises():
    result = _result(n_added=1)
    with pytest.raises(ValueError, match="page must be"):
        paginate_diff(result, page=0)


def test_paginate_negative_page_size_raises():
    result = _result(n_added=1)
    with pytest.raises(ValueError, match="page_size must be"):
        paginate_diff(result, page=1, page_size=-1)


def test_row_order_added_removed_modified():
    result = _result(n_added=1, n_removed=1, n_modified=1)
    page = paginate_diff(result, page=1, page_size=10)
    types = [r.change_type for r in page.rows]
    assert types == ["added", "removed", "modified"]
