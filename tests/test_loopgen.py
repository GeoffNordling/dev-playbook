"""loopgen checks a Loop's Mermaid graph against the verb sections around it."""

import subprocess
from pathlib import Path

LOOPGEN = Path(__file__).resolve().parent.parent / "scripts" / "loopgen"

RUNBOOK = "---\nname: tidy\ndescription: Tidies\n---\n\nTidy the tree.\n"
STANDARD = (
    "---\ntype: Standard\ntitle: Tidy Tree\ndescription: A tidy tree\n"
    'population: "a tree"\n---\n\n# Tidy Tree\n\n## Flat\n\nNo nesting.\n'
)
CARD = (
    "---\ntype: Standard-Card\ntitle: Tidy\ndescription: How the tree stays tidy\n"
    "---\n\n# Tidy\n\n## Define\n\n[Tidy Tree](/standards/tidy/tree.md)\n\n"
    "## Audit\n\n`scripts/tidy-lint`\n\n## Enforce\n\nNone.\n\n## Adopt\n\nNone.\n"
)
LOOP = """---
type: Loop
title: Tidy
description: Drives the tree tidy
---

# Tidy

Drives the repo's tree toward Tidy Tree.

```mermaid
flowchart LR
    tidy[tidy] -->|every iteration| flat[flat?]
    flat -->|findings| ask{ask?}
    ask -->|none met| tidy
    ask -->|3 rounds| user([the user])
    user -->|resumes| tidy
```

## Acts

- `tidy` — [tidy](/skills/tidy.md), fires every iteration.

## Checks

- `flat` — [Tidy](/standards/tidy/card.md#audit), fires every
  iteration.

## Yields

- `ask` — to the user, yields when three rounds have run.
"""


def make_repo(tmp_path: Path, loop: str = LOOP) -> Path:
    files = {
        "skills/tidy.md": RUNBOOK,
        "standards/tidy/tree.md": STANDARD,
        "standards/tidy/card.md": CARD,
        "loops/tidy.md": loop,
    }
    for rel, text in files.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return tmp_path


def run_loopgen(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", "--script", str(LOOPGEN), "--check", str(root)],
        capture_output=True,
        text=True,
    )


def test_graph_and_prose_that_agree_pass(tmp_path: Path) -> None:
    result = run_loopgen(make_repo(tmp_path))

    assert result.returncode == 0, result.stdout + result.stderr
    assert "1 loop(s), 4 node(s)" in result.stdout


def test_a_node_with_no_entry_fails(tmp_path: Path) -> None:
    loop = LOOP.replace(
        "    ask -->|none met| tidy\n",
        "    ask -->|none met| tidy\n    extra[extra] --> tidy\n",
    )

    result = run_loopgen(make_repo(tmp_path, loop))

    assert result.returncode == 1
    assert "`extra` has no entry and no yield leads to it" in result.stdout


def test_an_entry_with_no_node_fails(tmp_path: Path) -> None:
    loop = LOOP.replace(
        "## Checks\n",
        "## Checks\n\n- `ghost` — [Tidy](/standards/tidy/card.md#audit), fires every iteration.\n",
    )

    result = run_loopgen(make_repo(tmp_path, loop))

    assert result.returncode == 1
    assert "`ghost` has an entry but is not a node" in result.stdout


def test_an_edge_the_shape_does_not_allow_fails(tmp_path: Path) -> None:
    loop = LOOP.replace(
        "    flat -->|findings| ask{ask?}\n",
        "    flat -->|findings| ask{ask?}\n    flat --> tidy\n",
    )

    result = run_loopgen(make_repo(tmp_path, loop))

    assert result.returncode == 1
    assert "`flat` → `tidy` is check → act" in result.stdout


def test_a_check_that_links_the_standard_not_the_card_fails(tmp_path: Path) -> None:
    loop = LOOP.replace(
        "[Tidy](/standards/tidy/card.md#audit)", "[Tidy Tree](/standards/tidy/tree.md)"
    )

    result = run_loopgen(make_repo(tmp_path, loop))

    assert result.returncode == 1
    assert "a check links a card's Audit cell" in result.stdout


def test_a_check_that_links_the_card_without_the_audit_cell_fails(
    tmp_path: Path,
) -> None:
    loop = LOOP.replace("/standards/tidy/card.md#audit", "/standards/tidy/card.md")

    result = run_loopgen(make_repo(tmp_path, loop))

    assert result.returncode == 1
    assert "a check links a card's Audit cell" in result.stdout


def test_a_link_that_does_not_resolve_fails(tmp_path: Path) -> None:
    loop = LOOP.replace("/skills/tidy.md", "/skills/gone.md")

    result = run_loopgen(make_repo(tmp_path, loop))

    assert result.returncode == 1
    assert "does not resolve" in result.stdout


def test_a_yield_with_no_condition_fails(tmp_path: Path) -> None:
    loop = LOOP.replace("yields when three rounds have run", "after three rounds")

    result = run_loopgen(make_repo(tmp_path, loop))

    assert result.returncode == 1
    assert "`ask` states no condition" in result.stdout


def test_a_tree_with_no_loops_passes(tmp_path: Path) -> None:
    (tmp_path / "loops").mkdir()

    result = run_loopgen(tmp_path)

    assert result.returncode == 0
    assert "0 loop(s)" in result.stdout
