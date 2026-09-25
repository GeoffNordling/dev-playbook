"""Reading a stint's target from the workstream: the rule ids, the check, and the files."""

from pathlib import Path

import pytest

from dev_playbook.stint.target import TargetFault, read_target

HEAD_FILE = """\
---
type: Workstream
---

# WS

## Stints

- **Planned.** Budget: six iterations.
  Targets: `ws.one`, `ws.two`.
- **2026-09-01.** Budget: two. Targets: `ws.old`. Spent: two.
"""

DRAFT = """\
---
type: Standard
---

# Draft

## One

`ws.one` · deterministic

## Two

`ws.two` · deterministic

## Three

`ws.three` · stochastic
"""


@pytest.fixture
def copy(tmp_path: Path) -> Path:
    ws = tmp_path / "ws"
    (ws / "rules").mkdir(parents=True)
    (ws / "WORKSTREAM.md").write_text(HEAD_FILE)
    (ws / "rules" / "draft.md").write_text(DRAFT)
    (ws / "notes.md").write_text("---\ntype: General-Sheet\n---\n\n# Notes\n")
    (ws / "check").write_text("#!/bin/sh\nexit 0\n")
    (ws / "check").chmod(0o755)
    return tmp_path


def test_the_target_is_the_planned_entrys_rules(copy: Path) -> None:
    target = read_target(copy, "ws")
    assert target.rules == ("ws.one", "ws.two")
    assert target.command == "ws/check ws.one ws.two"
    assert sorted(target.files) == ["ws/WORKSTREAM.md", "ws/check", "ws/rules/draft.md"]


@pytest.mark.parametrize(
    ("old", "new", "want"),
    [
        ("- **Planned.** Budget: six iterations.\n", "", "has no planned stint entry"),
        ("  Targets: `ws.one`, `ws.two`.\n", "", "names no Targets"),
        ("`ws.two`.", "`ws.nine`.", "no draft Standard holds ws.nine"),
        ("`ws.two`.", "`ws.three`.", "ws.three is stochastic"),
        ("## Stints\n", "## Notes\n", "has no ## Stints"),
    ],
)
def test_a_head_file_with_no_runnable_target_is_refused(
    copy: Path, old: str, new: str, want: str
) -> None:
    head = copy / "ws" / "WORKSTREAM.md"
    head.write_text(head.read_text().replace(old, new))
    with pytest.raises(TargetFault, match=want):
        read_target(copy, "ws")


def test_a_check_that_is_not_executable_is_refused(copy: Path) -> None:
    (copy / "ws" / "check").chmod(0o644)
    with pytest.raises(TargetFault, match="ws/check is not an executable file"):
        read_target(copy, "ws")


def test_a_missing_check_is_refused(copy: Path) -> None:
    (copy / "ws" / "check").unlink()
    with pytest.raises(TargetFault, match="ws/check is not an executable file"):
        read_target(copy, "ws")
