"""Spec-linting functions for requirement documents.

Validates structural correctness of requirement definitions without any
knowledge of design specs or tests.  These checks run before traceability
analysis and gate on exit code 2 (configuration error).
"""

from pathlib import Path

from sdd_trace.models import (
    _MALFORMED_LONG_AREA,
    _MALFORMED_NO_PREFIX,
    _MALFORMED_SHORT_AREA,
    FunctionalReq,
)


def validate_req_ids(files: list[Path]) -> list[str]:
    """Scan for malformed requirement IDs. Returns list of error messages.

    Catches IDs that look like requirements but don't match the
    REQ-[A-Z]{3,6}-\\d{3} pattern: wrong-length area codes and missing REQ- prefix.
    """
    errors: list[str] = []
    for f in files:
        text = f.read_text()
        name = Path(f).name
        for match in _MALFORMED_LONG_AREA.finditer(text):
            mid = match.group().split("-")[1]
            errors.append(
                f"{match.group()} in {name}: area code '{mid}' has "
                f"{len(mid)} letters, expected 3–6"
            )
        for match in _MALFORMED_SHORT_AREA.finditer(text):
            mid = match.group().split("-")[1]
            errors.append(
                f"{match.group()} in {name}: area code '{mid}' has "
                f"{len(mid)} letter{'s' if len(mid) > 1 else ''}, expected 3–6"
            )
        for match in _MALFORMED_NO_PREFIX.finditer(text):
            errors.append(f"{match.group()} in {name}: missing REQ- prefix")
    return errors


def validate_obligations(func_reqs: dict[str, FunctionalReq]) -> list[str]:
    """Validate that every parsed requirement has exactly one obligation level.

    Operates on the parsed result of ``parse_functional_reqs`` rather than
    re-scanning files, using the ``all_obligations`` field on each requirement.

    Returns a list of error messages.  Empty list means all requirements are valid.
    Checks:
    - Definition site with no backtick-wrapped obligation keyword.
    - Definition site where backtick-wrapped keywords are not all the same
      (violates one-obligation-level-per-requirement rule).
    """
    errors: list[str] = []
    for req_id, req in sorted(func_reqs.items()):
        source_name = Path(req.sources[0]).name if req.sources else "unknown"
        if not req.all_obligations:
            errors.append(
                f"{req_id} in {source_name}: "
                "no backtick-wrapped obligation keyword found"
            )
        elif len(req.all_obligations) > 1:
            found = ", ".join(sorted(req.all_obligations))
            errors.append(
                f"{req_id} in {source_name}: mixed obligation levels ({found})"
            )
    return errors


# Keep these in the public namespace so validate_obligations can be tested
# independently, but they are intentionally not re-exported from __init__.
__all__ = ["validate_req_ids", "validate_obligations"]
