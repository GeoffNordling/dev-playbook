"""The deslop audit assignments stay in lockstep with the standards they slice.

The doc-set-deslopper agent divides two standards among six auditors
by citing section anchors; the third, Working Documentation Sets, the
auditor reads whole when the set's directory holds ROOT.md, filing each
section under the slice of the general rule it cites. Two drifts can
silently break the division:

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

DESLOPPER = REPO_ROOT / "dotfiles/dot-claude/agents/doc-set-deslopper.md"
AUDITOR = REPO_ROOT / "dotfiles/dot-claude/agents/doc-set-auditor.md"
WORKING_SETS = (
    REPO_ROOT
    / "standards/knowledge-organization/documentation-sets/working-documentation-sets.md"
)

# The sliced standards, each with the leaf headings the division deliberately
# leaves out: covered by a written exemption or by a deterministic linter.
EXEMPT: dict[Path, frozenset[str]] = {
    REPO_ROOT
    / "standards/knowledge-organization/documentation-sets/documentation-sets.md": frozenset(),
    REPO_ROOT / "standards/prose/conventions.md": frozenset(
        {
            # A set member is always a declarative document, never
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


def test_working_set_rules_are_read_whole() -> None:
    """The auditor reads Working Documentation Sets whole, so nothing is sliced
    there; the one thing that can drift is the link itself."""
    link = "~/workspace/dev-playbook/" + str(WORKING_SETS.relative_to(REPO_ROOT))
    assert any(link in line for _, line in content_lines(AUDITOR)), (
        f"{AUDITOR.name} no longer reads {WORKING_SETS.name}; a working set's "
        "further rules reach no auditor"
    )


def leaf_sections(standard: Path) -> dict[str, list[str]]:
    """Each leaf heading's slug mapped to the lines of its section."""
    leaves = leaf_slugs(standard)
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for _, line in content_lines(standard):
        if m := HEADING.match(line):
            slug = github_slug(m.group(2))
            current = slug if slug in leaves else None
        elif current is not None:
            sections[current].append(line)
        if current is not None and current not in sections:
            sections[current] = []
    return sections


def test_every_working_set_section_qualifies_an_assigned_rule() -> None:
    """The auditor routes a working-set section to the slice that owns the
    general rule it qualifies, so every section must cite one such rule by
    anchor, and that anchor must be one the deslopper assigns."""
    assigned = {
        "/" + str(standard.relative_to(REPO_ROOT)): assigned_slugs(standard)
        for standard in EXEMPT
    }
    citation = re.compile(r"\((/standards/[^)#]+\.md)#([a-z0-9-]+)\)")
    for slug, lines in leaf_sections(WORKING_SETS).items():
        cited = {
            (path, anchor)
            for line in lines
            for path, anchor in citation.findall(line)
            if anchor in assigned.get(path, frozenset())
        }
        assert cited, (
            f"{WORKING_SETS.name}#{slug} cites no rule the deslopper assigns; "
            "an auditor has no slice to file it under"
        )
