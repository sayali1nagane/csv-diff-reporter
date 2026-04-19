"""CLI integration for rule-based diff annotation."""
from __future__ import annotations
import argparse
from csv_diff_reporter.diff_annotator_rules import RuleOptions, apply_rules, RuleResult
from csv_diff_reporter.diff_annotator_rules_formatter import format_rule_result
from csv_diff_reporter.differ import DiffResult


def add_rule_args(parser: argparse.ArgumentParser) -> None:
    grp = parser.add_argument_group("rule annotations")
    grp.add_argument("--rule-empty-fields", action="store_true", default=False,
                     help="Flag rows with empty field values")
    grp.add_argument("--rule-required-columns", nargs="*", metavar="COL", default=[],
                     help="Columns that must be present in every changed row")
    grp.add_argument("--rule-forbidden-columns", nargs="*", metavar="COL", default=[],
                     help="Columns that must not appear in changed rows")
    grp.add_argument("--rule-output-format", choices=["text", "json"], default="text",
                     help="Output format for rule violations")


def build_rule_options(args: argparse.Namespace) -> RuleOptions:
    return RuleOptions(
        flag_empty_fields=getattr(args, "rule_empty_fields", False),
        required_columns=getattr(args, "rule_required_columns", []) or [],
        forbidden_columns=getattr(args, "rule_forbidden_columns", []) or [],
    )


def apply_rules_from_args(result: DiffResult, args: argparse.Namespace) -> RuleResult:
    options = build_rule_options(args)
    return apply_rules(result, options)


def render_rule_result(rule_result: RuleResult, args: argparse.Namespace) -> str:
    fmt = getattr(args, "rule_output_format", "text")
    return format_rule_result(rule_result, fmt=fmt)
