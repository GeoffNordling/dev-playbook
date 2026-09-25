"""The harness family: the rules of ``standards/harness/``.

Six rules are decided by functions over the model. Two hold every
``CLAUDE.md`` and every file under a harness root, ``.claude/`` or
``dotfiles/dot-claude/``, to the paths Claude Code reads; one holds each
skill bundle and agent to its fixed shape. Three read the global source,
``dotfiles/dot-claude/CLAUDE.md``, and run only where it is tracked.
"""

import re
from collections.abc import Iterator
from pathlib import PurePosixPath

from dev_playbook.check_registry import Finding, check
from dev_playbook.model import Heading, Repo

GLOBAL_CLAUDE = "dotfiles/dot-claude/CLAUDE.md"
HARNESS_ROOTS = (".claude/", "dotfiles/dot-claude/")
GLOBAL_SECTIONS = ("Behaviors", "Principles")
READ_THE_STANDARDS = "Read the standards"
REQUIRED_RULES = (READ_THE_STANDARDS, "Navigate docs by index")
SKILL_ENTRIES = frozenset({"references", "scripts", "agents"})
AGENT = re.compile(r"agents/[^/]+\.md")

# The member rows of the registry table, each a path below a harness root.
MEMBER_PATTERNS = tuple(
    re.compile(pattern)
    for pattern in (
        r"CLAUDE\.md",
        r"skills/[^/]+/.+",
        r"agents/[^/]+\.md",
        r"rules/[^/]+\.md",
        r"settings\.json",
        r"settings\.local\.json",
        r"hooks/.+",
        r"workflows/[^/]+\.js",
        r"statusline\.sh",
    )
)


@check("harness.no-frontmatter")
def no_frontmatter(repo: Repo) -> Iterator[Finding]:
    """The first line of every tracked ``CLAUDE.md`` is not ``---``."""
    for path in repo.files:
        if PurePosixPath(path).name != "CLAUDE.md":
            continue
        if repo.text(path).split("\n", 1)[0].rstrip("\r") == "---":
            yield Finding(path, 1, "a CLAUDE.md opens on its content, not on `---`")


@check("harness.behaviors-then-principles")
def behaviors_then_principles(repo: Repo) -> Iterator[Finding]:
    """The global source's H2 headings are exactly Behaviors then Principles."""
    if GLOBAL_CLAUDE not in repo.markdown:
        return
    sections = tuple(h.text for h in _headings(repo, 2))
    if sections != GLOBAL_SECTIONS:
        yield Finding(
            GLOBAL_CLAUDE,
            None,
            f"H2 headings must be exactly {list(GLOBAL_SECTIONS)}, got {list(sections)}",
        )


@check("harness.two-required-rules")
def two_required_rules(repo: Repo) -> Iterator[Finding]:
    """The global source has the two required ``###`` rule headings."""
    if GLOBAL_CLAUDE not in repo.markdown:
        return
    present = {h.text for h in _headings(repo, 3)}
    for rule in REQUIRED_RULES:
        if rule not in present:
            yield Finding(GLOBAL_CLAUDE, None, f"missing heading `### {rule}`")


@check("harness.read-the-standards-first")
def read_the_standards_first(repo: Repo) -> Iterator[Finding]:
    """``### Read the standards`` is the first ``###`` heading of the global source.

    Where the heading is absent, the required-rules check reports it.
    """
    if GLOBAL_CLAUDE not in repo.markdown:
        return
    rules = _headings(repo, 3)
    if READ_THE_STANDARDS not in {h.text for h in rules}:
        return
    if rules[0].text != READ_THE_STANDARDS:
        yield Finding(
            GLOBAL_CLAUDE,
            rules[0].line,
            f"the first `###` heading must be `### {READ_THE_STANDARDS}`",
        )


@check("harness.every-harness-file-matches-a-member-row")
def matches_a_member_row(repo: Repo) -> Iterator[Finding]:
    """Every tracked file under a harness root has one of the member paths."""
    for path in repo.files:
        below = _below_root(path)
        if below is None:
            continue
        if not any(p.fullmatch(below) for p in MEMBER_PATTERNS):
            yield Finding(
                path, None, "matches no member row of the Type Registry's harness kinds"
            )


@check("harness.every-runbook-at-a-fixed-path")
def runbook_at_a_fixed_path(repo: Repo) -> Iterator[Finding]:
    """Each skill has ``SKILL.md`` and three optional directories; an agent is one ``.md``.

    A skill directory holds nothing but ``SKILL.md``, ``references/``,
    ``scripts/``, and ``agents/``; an agent is a ``.md`` file directly in its
    agents root.
    """
    bundles: dict[str, list[str]] = {}
    for path in repo.files:
        below = _below_root(path)
        if below is None:
            continue
        root = path[: len(path) - len(below)]
        parts = below.split("/")
        if parts[0] == "skills" and len(parts) > 2:
            bundles.setdefault(f"{root}skills/{parts[1]}", []).append(
                "/".join(parts[2:])
            )
        elif below.startswith("agents/") and not AGENT.fullmatch(below):
            yield Finding(
                path, None, "an agent is a `.md` file directly in its agents root"
            )
    for bundle, entries in sorted(bundles.items()):
        if "SKILL.md" not in entries:
            yield Finding(bundle, None, "a skill directory has a `SKILL.md`")
        for entry in entries:
            head, sep, _ = entry.partition("/")
            if entry != "SKILL.md" and not (sep and head in SKILL_ENTRIES):
                yield Finding(
                    f"{bundle}/{entry}",
                    None,
                    "a skill directory holds only `SKILL.md`, `references/`, "
                    "`scripts/`, and `agents/`",
                )


def _headings(repo: Repo, level: int) -> list[Heading]:
    """The global source's headings of one level, outside fences, in order."""
    return [h for h in repo.markdown[GLOBAL_CLAUDE].headings if h.level == level]


def _below_root(path: str) -> str | None:
    """The part of ``path`` below its harness root, or None outside both roots."""
    for root in HARNESS_ROOTS:
        if path.startswith(root):
            return path[len(root) :]
    return None
