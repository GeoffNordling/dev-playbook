"""Format and print traceability reports."""

from collections import Counter
from pathlib import Path

from sdd_trace.models import FunctionalReq, extract_area_code


def format_area_counts(func_reqs: dict[str, FunctionalReq]) -> str:
    """Format area code value counts, sorted alphabetically.

    Example: 'Areas: AQD:5  AUTH:10  ERR:3'
    """
    counts = Counter(extract_area_code(rid) for rid in func_reqs)
    parts = [f"{area}:{count}" for area, count in sorted(counts.items())]
    return "Areas: " + "  ".join(parts)


def print_compact(
    func_reqs: dict[str, FunctionalReq],
    test_markers: dict[str, list[str]],
    design_refs: dict[str, list[str]] | None = None,
) -> int:
    """Print verdict-first compact summary optimized for CI agents.

    Traceability pipeline: func spec → (mandatory only) → design → tests.
    Non-mandatory requirements are counted but not tracked further.

    When no design doc exists, falls back to requiring mandatory reqs are
    tested directly.

    Returns exit code 0 (pass) or 1 (gaps found).
    """
    mandatory_ids = {rid for rid, req in func_reqs.items() if req.mandatory}
    non_mandatory_count = len(func_reqs) - len(mandatory_ids)

    if design_refs is not None:
        # Pipeline: mandatory must be in design, design must be tested
        mandatory_missing_from_design = mandatory_ids - set(design_refs)
        valid_design_refs = set(design_refs) & set(func_reqs)
        untested_in_design = valid_design_refs - set(test_markers)
    else:
        # Fallback: no design doc, mandatory must be tested directly
        mandatory_missing_from_design = set()
        untested_in_design = mandatory_ids - set(test_markers)

    orphaned = set(test_markers) - set(func_reqs)
    design_orphaned = (
        set(design_refs) - set(func_reqs) if design_refs is not None else set()
    )

    has_gaps = bool(
        mandatory_missing_from_design
        or untested_in_design
        or orphaned
        or design_orphaned
    )
    verdict = "FAIL" if has_gaps else "PASS"

    # Verdict line
    if has_gaps:
        parts: list[str] = []
        if mandatory_missing_from_design:
            parts.append(
                f"{len(mandatory_missing_from_design)} mandatory missing from design"
            )
        if untested_in_design:
            parts.append(f"{len(untested_in_design)} in design but untested")
        if orphaned:
            parts.append(f"{len(orphaned)} orphaned markers")
        if design_orphaned:
            parts.append(f"{len(design_orphaned)} orphaned design refs")
        if non_mandatory_count:
            parts.append(f"{non_mandatory_count} non-mandatory (not tracked)")
        print(f"{verdict}  {', '.join(parts)}")
    else:
        parts = [f"{len(mandatory_ids)} mandatory"]
        if design_refs is not None:
            designed = len(mandatory_ids - mandatory_missing_from_design)
            parts.append(f"{designed}/{len(mandatory_ids)} in design")
            tested = len(valid_design_refs - untested_in_design)
            parts.append(f"{tested}/{len(valid_design_refs)} design tested")
        else:
            tested = len(mandatory_ids - untested_in_design)
            parts.append(f"{tested}/{len(mandatory_ids)} tested")
        if non_mandatory_count:
            parts.append(f"{non_mandatory_count} non-mandatory (not tracked)")
        print(f"{verdict}  {', '.join(parts)}")

    # Area counts
    if func_reqs:
        print(format_area_counts(func_reqs))

    # Gap detail blocks (FAIL only)
    if has_gaps:
        if mandatory_missing_from_design:
            print(
                f"\nMandatory missing from design "
                f"({len(mandatory_missing_from_design)}):"
            )
            print(f"  {'  '.join(sorted(mandatory_missing_from_design))}")
        if untested_in_design:
            print(f"\nIn design but untested ({len(untested_in_design)}):")
            print(f"  {'  '.join(sorted(untested_in_design))}")
        if orphaned:
            print(f"\nOrphaned test markers ({len(orphaned)}):")
            print(f"  {'  '.join(sorted(orphaned))}")
        if design_orphaned:
            print(f"\nOrphaned design refs ({len(design_orphaned)}):")
            print(f"  {'  '.join(sorted(design_orphaned))}")

    return 1 if has_gaps else 0


def print_detail(
    func_reqs: dict[str, FunctionalReq],
    test_markers: dict[str, list[str]],
    design_refs: dict[str, list[str]] | None = None,
    *,
    areas: list[str],
) -> None:
    """Print matrix rows for specified area codes, grouped by area."""
    all_ids = set(func_reqs) | set(test_markers) | set(design_refs or {})

    for area in areas:
        area_ids = sorted(rid for rid in all_ids if extract_area_code(rid) == area)
        if not area_ids:
            continue

        area_total = sum(1 for rid in area_ids if rid in func_reqs)
        area_mandatory = sum(
            1 for rid in area_ids if rid in func_reqs and func_reqs[rid].mandatory
        )
        area_tested = sum(
            1 for rid in area_ids if rid in test_markers and rid in func_reqs
        )
        print(
            f"\n{area} ({area_total} requirements, {area_mandatory} mandatory, "
            f"{area_tested}/{area_total} tested)"
        )

        header = f"{'Requirement':<20} {'Obligation':<14} {'In Spec':<10}"
        if design_refs is not None:
            header += f" {'In Design':<12}"
        header += f" {'Tested':<10} {'Test File(s)'}"
        print(header)
        print("-" * len(header))

        for rid in area_ids:
            in_spec = str(rid in func_reqs)
            obligation = func_reqs[rid].obligation if rid in func_reqs else "N/A"
            is_mandatory = rid in func_reqs and func_reqs[rid].mandatory
            test_files = test_markers.get(rid, [])
            tested = str(bool(test_files))
            tests_str = (
                ", ".join(Path(t).name for t in test_files) if test_files else "None"
            )

            # Non-mandatory: show "-" for design/tested columns (not tracked)
            if rid in func_reqs and not is_mandatory:
                row = f"{rid:<20} {obligation:<14} {in_spec:<10}"
                if design_refs is not None:
                    row += f" {'-':<12}"
                row += f" {'-':<10} -"
            else:
                row = f"{rid:<20} {obligation:<14} {in_spec:<10}"
                if design_refs is not None:
                    row += f" {str(rid in design_refs):<12}"
                row += f" {tested:<10} {tests_str}"
            print(row)
