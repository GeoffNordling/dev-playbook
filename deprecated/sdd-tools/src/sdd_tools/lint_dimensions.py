"""Dimension section-organization lint rules (ADR-005).

Rules:
    lint.missing-dimension-header   a dsn-containing file is missing one of the
                                    four canonical dimension headers
    lint.dimension-order            dimension headers are out of canonical order
    lint.dsn-outside-dimension      a dsn item appears outside a dimension section

Files with no ``dsn`` items are exempt — the dimension organization is a
design-layer requirement, not a workspace-wide one.
"""

from __future__ import annotations

from sdd_tools.models import DIMENSION_NAMES, Finding, SpecFile


def check(spec_file: SpecFile, raw_text: str) -> list[Finding]:  # noqa: ARG001
    if not _has_dsn_items(spec_file):
        return []

    findings: list[Finding] = []
    findings.extend(_check_headers_present_and_ordered(spec_file))
    findings.extend(_check_dsn_placement(spec_file))
    return findings


def _has_dsn_items(spec_file: SpecFile) -> bool:
    return any(it.doctype == "dsn" for it in spec_file.all_items())


def _check_headers_present_and_ordered(spec_file: SpecFile) -> list[Finding]:
    """Verify all four dimension headers appear in canonical order."""
    dimension_sections = [s for s in spec_file.sections if s.is_dimension]
    present = [s.header for s in dimension_sections]

    findings: list[Finding] = []
    missing = [d for d in DIMENSION_NAMES if d not in present]
    for name in missing:
        findings.append(
            Finding(
                rule="lint.missing-dimension-header",
                file=spec_file.path,
                line=1,
                message=f"missing dimension header '## {name}'",
                fix=(
                    "every dsn spec file needs all four headers in order: "
                    + ", ".join(f"## {d}" for d in DIMENSION_NAMES)
                ),
            )
        )

    # Order check: among the dimensions that ARE present, confirm canonical order.
    canonical_rank = {d: i for i, d in enumerate(DIMENSION_NAMES)}
    present_ranks = [canonical_rank[d] for d in present if d in canonical_rank]
    if present_ranks != sorted(present_ranks):
        first_out_of_order = next(
            s
            for s, rank in zip(dimension_sections, present_ranks, strict=False)
            if present_ranks.index(rank) != sorted(present_ranks).index(rank)
        )
        findings.append(
            Finding(
                rule="lint.dimension-order",
                file=spec_file.path,
                line=first_out_of_order.header_line or 1,
                message=(
                    f"dimension header '## {first_out_of_order.header}' out of canonical order"
                ),
                fix=(
                    "arrange headers as: "
                    + " then ".join(f"## {d}" for d in DIMENSION_NAMES)
                ),
            )
        )
    return findings


def _check_dsn_placement(spec_file: SpecFile) -> list[Finding]:
    """Every dsn item must appear under a dimension section."""
    findings: list[Finding] = []
    for section in spec_file.sections:
        if section.is_dimension:
            continue
        for item in section.items:
            if item.doctype != "dsn":
                continue
            findings.append(
                Finding(
                    rule="lint.dsn-outside-dimension",
                    file=spec_file.path,
                    line=item.source_line,
                    line_kind="item header",
                    spec_id=item.id,
                    message=(
                        "dsn item is not under a dimension header "
                        "(Data, API Shape, Algorithms, Composition)"
                    ),
                    fix="move the item under exactly one ## dimension header",
                )
            )
    return findings
