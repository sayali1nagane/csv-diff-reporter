"""Format a DiffResult as a LaTeX longtable document."""
from __future__ import annotations

from typing import Dict

from .differ import DiffResult, RowDiff

_CHANGE_COLOR: Dict[str, str] = {
    "added": "diffadded",
    "removed": "diffremoved",
    "modified": "diffmodified",
}

_LATEX_SPECIAL = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "\\": r"\textbackslash{}",
}


def _escape(value: str) -> str:
    """Escape special LaTeX characters in a string value."""
    result = []
    for ch in value:
        result.append(_LATEX_SPECIAL.get(ch, ch))
    return "".join(result)


def _row_to_latex(row: RowDiff, headers: list[str]) -> str:
    """Render a single RowDiff as a colored LaTeX table row."""
    color = _CHANGE_COLOR.get(row.change_type, "")
    fields = row.new_fields if row.change_type != "removed" else row.old_fields
    cells = [_escape(str(fields.get(h, ""))) for h in headers]
    row_content = " & ".join(cells) + r" \\"
    if color:
        return r"\rowcolor{" + color + "}" + "\n" + row_content
    return row_content


def format_diff_as_latex(result: DiffResult, title: str = "CSV Diff Report") -> str:
    """Return a complete LaTeX document string for the given DiffResult."""
    headers = result.headers
    col_spec = "|".join(["l"] * (len(headers) + 1))  # +1 for change_type column
    header_cells = "Change & " + " & ".join(_escape(h) for h in headers) + r" \\ \hline"

    rows_latex: list[str] = []
    for row in result.rows:
        fields = row.new_fields if row.change_type != "removed" else row.old_fields
        color = _CHANGE_COLOR.get(row.change_type, "")
        cells = [_escape(str(fields.get(h, ""))) for h in headers]
        row_line = _escape(row.change_type) + " & " + " & ".join(cells) + r" \\"
        if color:
            rows_latex.append(r"\rowcolor{" + color + "}")
        rows_latex.append(row_line)

    rows_block = "\n    ".join(rows_latex) if rows_latex else r"\multicolumn{" + str(len(headers) + 1) + r"}{c}{No differences found.} \\"

    return (
        r"\documentclass{article}" + "\n"
        r"\usepackage{longtable,xcolor}" + "\n"
        r"\definecolor{diffadded}{RGB}{198,239,206}" + "\n"
        r"\definecolor{diffremoved}{RGB}{255,199,206}" + "\n"
        r"\definecolor{diffmodified}{RGB}{255,235,156}" + "\n"
        r"\begin{document}" + "\n"
        r"\section*{" + _escape(title) + "}\n"
        r"\begin{longtable}{|" + col_spec + r"|}" + "\n"
        r"\hline" + "\n"
        "    " + header_cells + "\n"
        r"\endfirsthead" + "\n"
        "    " + rows_block + "\n"
        r"\hline" + "\n"
        r"\end{longtable}" + "\n"
        r"\end{document}" + "\n"
    )
