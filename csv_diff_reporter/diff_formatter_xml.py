"""Format a DiffResult as an XML document."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Optional

from csv_diff_reporter.differ import DiffResult, RowDiff


def _row_to_xml(parent: ET.Element, row: RowDiff) -> None:
    """Append a <row> element to *parent* for the given RowDiff."""
    if row.old is None and row.new is not None:
        change_type = "added"
        fields = row.new
    elif row.old is not None and row.new is None:
        change_type = "removed"
        fields = row.old
    else:
        change_type = "modified"
        fields = row.new or {}

    row_el = ET.SubElement(parent, "row", attrib={"type": change_type, "key": str(row.key)})

    if change_type == "modified" and row.old:
        old_el = ET.SubElement(row_el, "old")
        for col, val in (row.old or {}).items():
            ET.SubElement(old_el, "field", attrib={"name": col}).text = str(val)
        new_el = ET.SubElement(row_el, "new")
        for col, val in fields.items():
            ET.SubElement(new_el, "field", attrib={"name": col}).text = str(val)
    else:
        for col, val in fields.items():
            ET.SubElement(row_el, "field", attrib={"name": col}).text = str(val)


def format_diff_as_xml(
    result: DiffResult,
    title: str = "csv-diff-report",
    pretty: bool = True,
) -> str:
    """Return an XML string representing *result*.

    Parameters
    ----------
    result:
        The diff result to serialise.
    title:
        Value of the ``title`` attribute on the root ``<report>`` element.
    pretty:
        When *True* the output is indented for human readability.
    """
    added = [r for r in result.rows if r.old is None]
    removed = [r for r in result.rows if r.new is None]
    modified = [r for r in result.rows if r.old is not None and r.new is not None]

    root = ET.Element(
        "report",
        attrib={
            "title": title,
            "added": str(len(added)),
            "removed": str(len(removed)),
            "modified": str(len(modified)),
        },
    )

    if result.headers:
        headers_el = ET.SubElement(root, "headers")
        for h in result.headers:
            ET.SubElement(headers_el, "header").text = h

    rows_el = ET.SubElement(root, "rows")
    for row in result.rows:
        _row_to_xml(rows_el, row)

    raw = ET.tostring(root, encoding="unicode", xml_declaration=False)
    if not pretty:
        return raw
    return minidom.parseString(raw).toprettyxml(indent="  ", encoding=None)  # type: ignore[return-value]
