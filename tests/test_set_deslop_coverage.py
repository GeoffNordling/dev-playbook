"""The deslop audit assignments stay in lockstep with the standards they slice.

The working-doc-set-deslopper agent divides two standards among three
auditors by citing section anchors. Two drifts can silently break that
division:

  - a section added to a standard that no auditor is assigned — the new
    rule is never audited;
  - an assignment citing a section that was renamed or removed — the
    auditor is sent to a rule that no longer exists (ref-lint also fails
    this at the commit gate; asserted here so the whole contract lives in
    one test).

A rule heading is a *leaf* ATX heading below H1 — one with no subheadings
under it — matching one-rule-one-place: structural group headings carry no
rule of their own. Headings deliberately outside the division are named in
EXEMPT with the reason; a stale exemption fails too.
"""

import re
from pathlib import Path

from dev_playbook.md import content_lines, github_slug

REPO_ROOT = Path(__file__).resolve().parents[1]

DESLOPPER = REPO_ROOT / "dotfiles/dot-claude/agents/working-doc-set-deslopper.md"

# The sliced standards, each with the leaf headings the division deliberately
# leaves out: covered by a written exemption or by a deterministic linter.
EXEMPT: dict[Path, frozenset[str]] = {
    REPO_ROOT
    / "standards/knowledge-organization/working-documentation-sets.md": frozenset(),
    REPO_ROOT / "standards/prose/conventions.md": frozenset(
        {
            # Working sets are exempt by the speculative-voice section.
            "declarative-present-tense",
            # A working-set member is always a declarative document, never
            # harness-loaded, so this voice rule never binds it.
            "imperative-and-second-person",
            # prose-lint enforces these deterministically.
            "spelling",
            "terminology-the-person-is-the-user",
        }
    ),
}

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")


def leaf_slugs(standard: Path) -> frozenset[str]:
    """Slugs of the standard's leaf headings below H1."""
    headings = [
        (len(m.group(1)), github_slug(m.group(2)))
        for _, line in content_lines(standard)
        if (m := HEADING.match(line))
    ]
    return frozenset(
        slug
        for i, (level, slug) in enumerate(headings)
        if level > 1
        and not any(deeper > level for deeper, _ in headings[i + 1 : i + 2])
    )


def assigned_slugs(standard: Path) -> frozenset[str]:
    """Slugs the deslopper's assignments cite for one standard."""
    citation = re.compile(
        r"~/workspace/dev-playbook/"
        + re.escape(str(standard.relative_to(REPO_ROOT)))
        + r"#([a-z0-9-]+)"
    )
    return frozenset(
        slug for _, line in content_lines(DESLOPPER) for slug in citation.findall(line)
    )


def test_every_rule_heading_is_assigned_or_exempt() -> None:
    for standard, exempt in EXEMPT.items():
        uncovered = leaf_slugs(standard) - assigned_slugs(standard) - exempt
        assert not uncovered, (
            f"{standard.name} headings no auditor is assigned: {sorted(uncovered)} — "
            f"assign them in {DESLOPPER.name} or add them to EXEMPT with a reason"
        )


def test_every_assignment_resolves_to_a_heading() -> None:
    for standard in EXEMPT:
        dead = assigned_slugs(standard) - leaf_slugs(standard)
        assert not dead, (
            f"{DESLOPPER.name} assigns {standard.name} sections that are not leaf "
            f"headings there: {sorted(dead)}"
        )


def test_exemptions_name_real_headings() -> None:
    for standard, exempt in EXEMPT.items():
        stale = exempt - leaf_slugs(standard)
        assert not stale, (
            f"EXEMPT names headings gone from {standard.name}: {sorted(stale)}"
        )
