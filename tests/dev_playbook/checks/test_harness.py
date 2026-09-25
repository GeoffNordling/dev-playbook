"""Unit tests for the harness family's checks."""

from collections.abc import Callable, Iterator
from pathlib import Path

from dev_playbook.check_registry import Finding
from dev_playbook.checks.harness import (
    behaviors_then_principles,
    is_a_registered_member,
    no_frontmatter,
    read_the_standards_first,
    runbook_at_a_fixed_path,
    two_required_rules,
)
from dev_playbook.model import Repo

GLOBAL = "dotfiles/dot-claude/CLAUDE.md"

GOOD_GLOBAL = b"""\
# Global

## Behaviors

### Read the standards

### Navigate docs by index

## Principles

### Be direct
"""

BAD_GLOBAL = b"""\
# Global

## Principles

### Be direct

```
## Behaviors
### Navigate docs by index
```

## Behaviors

### Read the standards
"""


def found(
    check: Callable[[Repo], Iterator[Finding]], contents: dict[str, bytes]
) -> list[tuple[str, int | None]]:
    repo = Repo.from_files(Path("/r"), contents)
    return [(f.path, f.line) for f in check(repo)]


def test_no_frontmatter() -> None:
    assert found(
        no_frontmatter,
        {
            "CLAUDE.md": b"# Repo\n",
            "sub/CLAUDE.md": b"---\ntitle: x\n---\n# Sub\n",
            "notes.md": b"---\ntitle: x\n---\n# Notes\n",
        },
    ) == [("sub/CLAUDE.md", 1)]


def test_behaviors_then_principles() -> None:
    assert found(behaviors_then_principles, {GLOBAL: GOOD_GLOBAL}) == []
    assert found(behaviors_then_principles, {"CLAUDE.md": BAD_GLOBAL}) == []
    assert found(behaviors_then_principles, {GLOBAL: BAD_GLOBAL}) == [(GLOBAL, None)]


def test_two_required_rules() -> None:
    assert found(two_required_rules, {GLOBAL: GOOD_GLOBAL}) == []
    repo = Repo.from_files(Path("/r"), {GLOBAL: BAD_GLOBAL})
    messages = [f.message for f in two_required_rules(repo)]
    assert messages == ["missing heading `### Navigate docs by index`"]


def test_read_the_standards_first() -> None:
    assert found(read_the_standards_first, {GLOBAL: GOOD_GLOBAL}) == []
    assert found(read_the_standards_first, {GLOBAL: BAD_GLOBAL}) == [(GLOBAL, 5)]
    assert found(read_the_standards_first, {GLOBAL: b"## Behaviors\n### Other\n"}) == []


def test_every_harness_file_is_a_registered_member() -> None:
    assert found(
        is_a_registered_member,
        {
            ".claude/settings.local.json": b"{}\n",
            ".claude/workflows/loop.js": b"\n",
            ".claude/skills/a/references/deep/x.md": b"x\n",
            ".claude/notes.txt": b"x\n",
            "dotfiles/dot-claude/CLAUDE.md": b"# Global\n",
            "dotfiles/dot-claude/statusline.sh": b"\n",
            "dotfiles/dot-claude/hooks/sub/run": b"\n",
            "dotfiles/dot-claude/rules/a/b.md": b"x\n",
            "dotfiles/dot-claude/skills/stray.md": b"x\n",
            "docs/notes.txt": b"x\n",
        },
    ) == [
        (".claude/notes.txt", None),
        ("dotfiles/dot-claude/rules/a/b.md", None),
        ("dotfiles/dot-claude/skills/stray.md", None),
    ]


def test_every_runbook_at_a_fixed_path() -> None:
    assert found(
        runbook_at_a_fixed_path,
        {
            ".claude/skills/good/SKILL.md": b"x\n",
            ".claude/skills/good/references/a.md": b"x\n",
            ".claude/skills/good/scripts/run.sh": b"\n",
            ".claude/skills/good/agents/openai.yaml": b"x\n",
            ".claude/skills/bare/references/a.md": b"x\n",
            ".claude/skills/extra/SKILL.md": b"x\n",
            ".claude/skills/extra/README.md": b"x\n",
            ".claude/agents/ok.md": b"x\n",
            ".claude/agents/notes.txt": b"x\n",
            "dotfiles/dot-claude/agents/sub/deep.md": b"x\n",
            "skills/elsewhere/README.md": b"x\n",
        },
    ) == [
        (".claude/agents/notes.txt", None),
        ("dotfiles/dot-claude/agents/sub/deep.md", None),
        (".claude/skills/bare", None),
        (".claude/skills/extra/README.md", None),
    ]
