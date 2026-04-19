"""Rule-based annotation engine for diff results."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from csv_diff_reporter.differ import DiffResult, RowDiff


@dataclass
class RuleMatch:
    rule_name: str
    message: str
    row_key: str
    change_type: str

    def as_dict(self) -> dict:
        return {
            "rule": self.rule_name,
            "message": self.message,
            "key": self.row_key,
            "change_type": self.change_type,
        }


@dataclass
class RuleOptions:
    flag_missing_key: bool = True
    flag_empty_fields: bool = False
    required_columns: List[str] = field(default_factory=list)
    forbidden_columns: List[str] = field(default_factory=list)


@dataclass
class RuleResult:
    matches: List[RuleMatch] = field(default_factory=list)
    total_checked: int = 0

    @property
    def has_violations(self) -> bool:
        return len(self.matches) > 0


def _check_row(row: RowDiff, options: RuleOptions) -> List[RuleMatch]:
    found: List[RuleMatch] = []
    fields = row.new_fields or row.old_fields or {}

    if options.flag_empty_fields:
        for col, val in fields.items():
            if val is None or str(val).strip() == "":
                found.append(RuleMatch(
                    rule_name="empty_field",
                    message=f"Column '{col}' is empty",
                    row_key=row.key,
                    change_type=row.change_type,
                ))

    for col in options.required_columns:
        if col not in fields:
            found.append(RuleMatch(
                rule_name="missing_required_column",
                message=f"Required column '{col}' is absent",
                row_key=row.key,
                change_type=row.change_type,
            ))

    for col in options.forbidden_columns:
        if col in fields:
            found.append(RuleMatch(
                rule_name="forbidden_column_present",
                message=f"Forbidden column '{col}' is present",
                row_key=row.key,
                change_type=row.change_type,
            ))

    return found


def apply_rules(result: DiffResult, options: Optional[RuleOptions] = None) -> RuleResult:
    if options is None:
        options = RuleOptions()
    rule_result = RuleResult()
    for row in result.rows:
        rule_result.total_checked += 1
        rule_result.matches.extend(_check_row(row, options))
    return rule_result
