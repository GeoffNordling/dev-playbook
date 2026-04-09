"""Structural lint checks for OFT specification items.

Each function returns a list of human-readable error strings. An empty list
means the check passed. Checks are pure functions with no side effects.

Checks:
    check_bare_obligations  -- obligation keywords not wrapped in backticks
    check_mixed_obligations -- multiple distinct obligation levels in one item
    check_status            -- Status field missing or not in allowed set
    check_covers_syntax     -- Covers: references that aren't valid OFT IDs
    check_needs_values      -- Needs: values that aren't known artifact types
    check_id_format         -- near-miss IDs in backticks with malformed syntax
"""

from pathlib import Path

from pytest_sdd.models import (
    BACKTICK_SPAN_RE,
    KNOWN_ARTIFACT_TYPES,
    NEAR_MISS_ID_RE,
    OBLIGATION_BACKTICK_RE,
    OBLIGATION_BARE_RE,
    SPEC_ID_BARE_RE,
    VALID_STATUSES,
    SpecItem,
)


def check_bare_obligations(path: Path, text: str) -> list[str]:
    """Find obligation keywords that appear outside backtick spans.

    Scans the entire file (not just item bodies) so that misuse in prose
    sections and preambles is caught too. Each line is scanned after stripping
    all backtick-wrapped spans.
    """
    errors: list[str] = []
    for line_num, line in enumerate(text.splitlines(), start=1):
        stripped = BACKTICK_SPAN_RE.sub("", line)
        for match in OBLIGATION_BARE_RE.finditer(stripped):
            errors.append(
                f"{path.name}:{line_num}: bare obligation keyword "
                f"'{match.group()}' must be wrapped in backticks"
            )
    return errors


_OBLIGATION_LEVEL = {
    "SHALL": "mandatory",
    "SHALL NOT": "mandatory",
    "SHOULD": "preferred",
    "SHOULD NOT": "preferred",
    "MAY": "optional",
}


def check_mixed_obligations(items: list[SpecItem]) -> list[str]:
    """Flag spec items that use more than one distinct obligation level.

    Obligation levels: mandatory (SHALL/SHALL NOT), preferred (SHOULD/SHOULD NOT),
    optional (MAY). Mixing SHALL with SHALL NOT is allowed (both mandatory). Mixing
    mandatory with preferred or optional is not.
    """
    errors: list[str] = []
    for item in items:
        keywords = {m.group(1) for m in OBLIGATION_BACKTICK_RE.finditer(item.body)}
        levels = {_OBLIGATION_LEVEL[kw] for kw in keywords}
        if len(levels) > 1:
            found = ", ".join(sorted(keywords))
            errors.append(f"{item.id}: mixed obligation levels ({found})")
    return errors


def check_status(items: list[SpecItem]) -> list[str]:
    """Verify each spec item has a valid Status field."""
    errors: list[str] = []
    for item in items:
        if not item.status:
            errors.append(
                f"{item.id}: missing Status field "
                f"(expected one of: {', '.join(sorted(VALID_STATUSES))})"
            )
        elif item.status not in VALID_STATUSES:
            errors.append(
                f"{item.id}: invalid Status '{item.status}' "
                f"(expected one of: {', '.join(sorted(VALID_STATUSES))})"
            )
    return errors


def check_covers_syntax(items: list[SpecItem]) -> list[str]:
    """Verify each Covers: reference is a valid OFT spec item ID."""
    errors: list[str] = []
    for item in items:
        for ref in item.covers:
            if not SPEC_ID_BARE_RE.fullmatch(ref):
                errors.append(
                    f"{item.id}: malformed Covers reference '{ref}' "
                    "(expected type~name~revision)"
                )
    return errors


def check_needs_values(items: list[SpecItem]) -> list[str]:
    """Verify each Needs: value is a known OFT artifact type."""
    errors: list[str] = []
    for item in items:
        for need in item.needs:
            if need not in KNOWN_ARTIFACT_TYPES:
                errors.append(
                    f"{item.id}: unknown artifact type '{need}' in Needs:"
                )
    return errors


def check_id_format(path: Path, text: str, valid_items: list[SpecItem]) -> list[str]:
    """Find backtick-wrapped content that looks like a spec ID but is malformed.

    Scans for any backtick token containing tildes that doesn't match the
    valid ID pattern (excluding already-parsed valid IDs).
    """
    valid_ids = {f"`{item.id}`" for item in valid_items}
    errors: list[str] = []
    for match in NEAR_MISS_ID_RE.finditer(text):
        token = match.group()
        if token in valid_ids:
            continue
        # Strip backticks and check if the bare content is a valid ID
        bare = token[1:-1]
        if not SPEC_ID_BARE_RE.fullmatch(bare):
            errors.append(
                f"{path.name}: malformed spec ID {token} "
                "(expected `type~name~revision`)"
            )
    return errors


def run_all(path: Path, text: str, items: list[SpecItem]) -> list[str]:
    """Run all lint checks and return combined error list."""
    errors: list[str] = []
    errors.extend(check_bare_obligations(path, text))
    errors.extend(check_mixed_obligations(items))
    errors.extend(check_status(items))
    errors.extend(check_covers_syntax(items))
    errors.extend(check_needs_values(items))
    errors.extend(check_id_format(path, text, items))
    return errors
