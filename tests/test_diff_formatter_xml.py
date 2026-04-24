"""Tests for csv_diff_reporter.diff_formatter_xml."""
from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_formatter_xml import format_diff_as_xml


def _row(key: str, old=None, new=None) -> RowDiff:
    return RowDiff(key=key, old=old, new=new)


def _make_result(*rows: RowDiff, headers=None) -> DiffResult:
    return DiffResult(rows=list(rows), headers=headers or ["id", "name", "value"])


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _parse(xml_str: str) -> ET.Element:
    return ET.fromstring(xml_str)


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

def test_format_xml_empty_result_root_attributes():
    result = _make_result()
    root = _parse(format_diff_as_xml(result, pretty=False))
    assert root.attrib["added"] == "0"
    assert root.attrib["removed"] == "0"
    assert root.attrib["modified"] == "0"


def test_format_xml_empty_result_has_no_row_elements():
    result = _make_result()
    root = _parse(format_diff_as_xml(result, pretty=False))
    assert root.find("rows") is not None
    assert list(root.find("rows")) == []  # type: ignore[arg-type]


def test_format_xml_headers_element_present():
    result = _make_result(headers=["id", "name"])
    root = _parse(format_diff_as_xml(result, pretty=False))
    headers = root.find("headers")
    assert headers is not None
    texts = [h.text for h in headers]
    assert texts == ["id", "name"]


def test_format_xml_added_row_type_attribute():
    row = _row("1", old=None, new={"id": "1", "name": "Alice", "value": "10"})
    result = _make_result(row)
    root = _parse(format_diff_as_xml(result, pretty=False))
    row_el = root.find("./rows/row")
    assert row_el is not None
    assert row_el.attrib["type"] == "added"
    assert row_el.attrib["key"] == "1"


def test_format_xml_removed_row_type_attribute():
    row = _row("2", old={"id": "2", "name": "Bob", "value": "20"}, new=None)
    result = _make_result(row)
    root = _parse(format_diff_as_xml(result, pretty=False))
    row_el = root.find("./rows/row")
    assert row_el is not None
    assert row_el.attrib["type"] == "removed"


def test_format_xml_modified_row_has_old_and_new_children():
    row = _row(
        "3",
        old={"id": "3", "name": "Carol", "value": "30"},
        new={"id": "3", "name": "Carol", "value": "99"},
    )
    result = _make_result(row)
    root = _parse(format_diff_as_xml(result, pretty=False))
    row_el = root.find("./rows/row")
    assert row_el is not None
    assert row_el.attrib["type"] == "modified"
    assert row_el.find("old") is not None
    assert row_el.find("new") is not None


def test_format_xml_counts_reflect_row_types():
    rows = [
        _row("1", new={"id": "1"}),
        _row("2", old={"id": "2"}),
        _row("3", old={"id": "3", "v": "a"}, new={"id": "3", "v": "b"}),
        _row("4", old={"id": "4", "v": "x"}, new={"id": "4", "v": "y"}),
    ]
    result = _make_result(*rows)
    root = _parse(format_diff_as_xml(result, pretty=False))
    assert root.attrib["added"] == "1"
    assert root.attrib["removed"] == "1"
    assert root.attrib["modified"] == "2"


def test_format_xml_pretty_output_is_indented():
    result = _make_result(_row("1", new={"id": "1"}))
    xml_str = format_diff_as_xml(result, pretty=True)
    assert "\n" in xml_str


def test_format_xml_custom_title():
    result = _make_result()
    root = _parse(format_diff_as_xml(result, title="my-report", pretty=False))
    assert root.attrib["title"] == "my-report"
