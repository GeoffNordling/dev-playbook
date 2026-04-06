"""Verify traceability between requirements, design specs, and tests.

Traceability follows a linear pipeline:

  Functional spec  →  (mandatory only)  →  Design  →  Tests

1. Parse functional requirements and partition into mandatory
   (`SHALL`/`SHALL NOT`) and non-mandatory (`SHOULD`, `SHOULD NOT`, `MAY`).
   Non-mandatory requirements are counted but not tracked further.
2. Every mandatory requirement must appear in the design spec.
3. Every requirement referenced in the design spec must have at least one test.
4. Every test marker must map to a real requirement (no orphans).
5. Every design reference must map to a real requirement (no orphans).

When no design spec exists, the tool falls back to requiring that every
mandatory requirement is tested directly (steps 2–3 collapse into one check).

Spec validation (well-formed IDs, obligation keywords) runs as a gate before
traceability analysis and exits with code 2 on failure.

Conventions:
  Requirement IDs    REQ-<AREA>-<NNN> where AREA is 3–6 uppercase letters
                     and NNN is a 3-digit number (e.g. REQ-TRANS-001).
  Definition sites   **REQ-XXX-NNN**: ... `SHALL` ... (bold ID + colon,
                     backtick-wrapped obligation keyword).
  Test markers       @pytest.mark.req("REQ-XXX-NNN") or list form
                     @pytest.mark.req(["REQ-XXX-001", "REQ-XXX-002"]).
  Spec layout        specs/functional_requirements.md (single file) or
                     specs/functional_requirements/ (split; must contain index.md).
                     specs/design.md or specs/design/ — optional, same conventions.

Output:
  By default, prints a verdict-first compact summary:
    PASS/FAIL  <gap counts>
    Areas: <area code counts>
  On FAIL, blocking gaps are listed below with specific requirement IDs.

  Use --detail <AREA> [<AREA> ...] to expand specific area codes into full
  traceability matrix rows grouped by area.

Exit codes:
  0  All checks pass.
  1  Gaps found (mandatory missing from design, design items untested,
     orphaned markers, or orphaned design refs).
  2  Configuration error (missing directories, no requirements, malformed IDs,
     or missing/mixed obligation keywords).
"""

import argparse
import sys
from pathlib import Path

from sdd_trace.models import find_md_files
from sdd_trace.parser import (
    parse_design_refs,
    parse_functional_reqs,
    parse_test_markers,
)
from sdd_trace.report import print_compact, print_detail
from sdd_trace.validation import validate_obligations, validate_req_ids


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--specs",
        type=Path,
        default=None,
        help="Path to specs directory (default: auto-detect specs/ from cwd)",
    )
    parser.add_argument(
        "--tests",
        type=Path,
        default=None,
        help="Path to tests directory (default: auto-detect tests/ or test/ from cwd)",
    )
    parser.add_argument(
        "--detail",
        nargs="*",
        default=None,
        help="Show full matrix for specific area codes (e.g., --detail ERR AQD). "
        "Omit to show compact summary only.",
    )
    args = parser.parse_args()

    root = Path.cwd()

    # Auto-detect directories
    specs_dir = args.specs or (root / "specs" if (root / "specs").is_dir() else None)
    tests_dir = args.tests
    if tests_dir is None:
        for candidate in ("tests", "test"):
            if (root / candidate).is_dir():
                tests_dir = root / candidate
                break

    if specs_dir is None:
        print(
            "Error: No specs directory found. Use --specs to specify.", file=sys.stderr
        )
        sys.exit(2)
    if tests_dir is None:
        print(
            "Error: No tests directory found. Use --tests to specify.", file=sys.stderr
        )
        sys.exit(2)
    if not specs_dir.is_dir():
        print(f"Error: {specs_dir} is not a directory.", file=sys.stderr)
        sys.exit(2)
    if not tests_dir.is_dir():
        print(f"Error: {tests_dir} is not a directory.", file=sys.stderr)
        sys.exit(2)

    # 1. Locate functional requirements
    spec_files = find_md_files(specs_dir, "functional_requirements")
    if not spec_files:
        print(
            "Error: No functional_requirements.md or functional_requirements/ "
            f"directory found in {specs_dir}.",
            file=sys.stderr,
        )
        sys.exit(2)

    # 2. Validate requirement IDs (operates on raw files)
    validation_errors = validate_req_ids(spec_files)
    if validation_errors:
        print("Error: Malformed requirement IDs found:", file=sys.stderr)
        for err in validation_errors:
            print(f"  {err}", file=sys.stderr)
        sys.exit(2)

    # 3. Parse functional requirements
    func_reqs = parse_functional_reqs(spec_files)
    if not func_reqs:
        print(
            "Error: No requirement definitions (**REQ-XXX-NNN**: ...) found "
            "in spec files.",
            file=sys.stderr,
        )
        sys.exit(2)

    # 4. Validate obligation keywords (operates on parsed result)
    obligation_errors = validate_obligations(func_reqs)
    if obligation_errors:
        print("Error: Obligation keyword problems found:", file=sys.stderr)
        for err in obligation_errors:
            print(f"  {err}", file=sys.stderr)
        sys.exit(2)

    # 5. Design coverage (optional)
    design_files = find_md_files(specs_dir, "design")
    if design_files:
        design_errors = validate_req_ids(design_files)
        if design_errors:
            print("Error: Malformed requirement IDs in design spec:", file=sys.stderr)
            for err in design_errors:
                print(f"  {err}", file=sys.stderr)
            sys.exit(2)
    design_refs = parse_design_refs(design_files) if design_files else None

    # 6. Test coverage
    test_markers = parse_test_markers(tests_dir)

    # 7. Report
    exit_code = print_compact(func_reqs, test_markers, design_refs)

    detail_areas = args.detail or []
    if detail_areas:
        areas = [a.upper() for a in detail_areas]
        print_detail(func_reqs, test_markers, design_refs, areas=areas)

    sys.exit(exit_code)
