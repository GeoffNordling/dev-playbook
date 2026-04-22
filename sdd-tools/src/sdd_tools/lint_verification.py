"""Verification-field lint rules (ADR-005).

Rules:
    lint.missing-verification   a dsn item has none of Needs:, Interface:,
                                or AgentReview:
    lint.bad-agent-review       an AgentReview: field is empty, or appears on
                                a non-dsn item (dsn-only field)
"""

from __future__ import annotations

from sdd_tools.models import Finding, SpecFile


def check(spec_file: SpecFile, raw_text: str) -> list[Finding]:  # noqa: ARG001
    findings: list[Finding] = []
    findings.extend(_check_missing_verification(spec_file))
    findings.extend(_check_agent_review_well_formed(spec_file))
    return findings


def _check_missing_verification(spec_file: SpecFile) -> list[Finding]:
    findings: list[Finding] = []
    for item in spec_file.all_items():
        if item.doctype != "dsn":
            continue
        if item.needs or item.interfaces or item.agent_reviews:
            continue
        findings.append(
            Finding(
                rule="lint.missing-verification",
                file=spec_file.path,
                line=item.source_line,
                line_kind="item header",
                spec_id=item.id,
                message=(
                    "dsn has no verification field "
                    "(Needs:, Interface:, or AgentReview:)"
                ),
                fix=(
                    "add at least one of Needs:, Interface:, or AgentReview: "
                    "so the commitment is checked"
                ),
            )
        )
    return findings


def _check_agent_review_well_formed(spec_file: SpecFile) -> list[Finding]:
    """AgentReview: is dsn-only. The parser discards empty values already, so
    misuse on a non-dsn item is the main failure mode detected here."""
    findings: list[Finding] = []
    for item in spec_file.all_items():
        if item.agent_reviews and item.doctype != "dsn":
            findings.append(
                Finding(
                    rule="lint.bad-agent-review",
                    file=spec_file.path,
                    line=item.source_line,
                    line_kind="item header",
                    spec_id=item.id,
                    message=(
                        f"AgentReview: is dsn-only, found on {item.doctype}"
                    ),
                    fix=(
                        "remove AgentReview: or restructure as a dsn "
                        "that covers this item"
                    ),
                )
            )
    return findings
