"""Behavioral tests for scripts/loop-lint.

loop-lint walks a repo's markdown files once, keeps the ones under loops/ typed
Loop, and checks each one's Mermaid graph against the verb sections around it
under the five Loop Conventions rules. Discovery goes through `git ls-files`,
so every fixture is a git repo; a directory (repo root) is the only positional
argument. The shim declares pyyaml via PEP 723, so it is invoked the way
pre-commit runs it: `uv run --script`.
"""

import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "loop-lint"

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


def run(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", "--script", str(SCRIPT), str(repo)],
        capture_output=True,
        text=True,
    )


def make_repo(tmp_path: Path, loop: str | None = LOOP) -> Path:
    """A git repo holding a runbook, a Standard, its card, and one Loop."""
    files = {
        "skills/tidy.md": RUNBOOK,
        "standards/tidy/tree.md": STANDARD,
        "standards/tidy/card.md": CARD,
    }
    if loop is not None:
        files["loops/tidy.md"] = loop
    repo = tmp_path / "repo"
    for rel, text in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    return repo


def test_graph_and_prose_that_agree_pass(tmp_path: Path) -> None:
    result = run(make_repo(tmp_path))

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""
    assert "1 loop(s), 4 node(s)" in result.stderr


def test_a_node_with_no_entry_fails(tmp_path: Path) -> None:
    loop = LOOP.replace(
        "    ask -->|none met| tidy\n",
        "    ask -->|none met| tidy\n    extra[extra] --> tidy\n",
    )

    result = run(make_repo(tmp_path, loop))

    assert result.returncode == 1
    assert result.stdout.startswith("loops/tidy.md: knowledge-organization.loop-nodes ")
    assert "`extra` has no entry and no yield leads to it" in result.stdout


def test_an_entry_with_no_node_fails(tmp_path: Path) -> None:
    loop = LOOP.replace(
        "## Checks\n",
        "## Checks\n\n- `ghost` — [Tidy](/standards/tidy/card.md#audit), fires every iteration.\n",
    )

    result = run(make_repo(tmp_path, loop))

    assert result.returncode == 1
    assert (
        "knowledge-organization.loop-nodes `ghost` has an entry but is not a node"
        in result.stdout
    )


def test_an_edge_the_shape_does_not_allow_fails(tmp_path: Path) -> None:
    loop = LOOP.replace(
        "    flat -->|findings| ask{ask?}\n",
        "    flat -->|findings| ask{ask?}\n    flat --> tidy\n",
    )

    result = run(make_repo(tmp_path, loop))

    assert result.returncode == 1
    assert (
        "knowledge-organization.loop-edges edge `flat` → `tidy` is check → act"
        in result.stdout
    )


def test_a_check_that_links_the_standard_not_the_card_fails(tmp_path: Path) -> None:
    loop = LOOP.replace(
        "[Tidy](/standards/tidy/card.md#audit)", "[Tidy Tree](/standards/tidy/tree.md)"
    )

    result = run(make_repo(tmp_path, loop))

    assert result.returncode == 1
    assert "knowledge-organization.loop-entries" in result.stdout
    assert "a check links a card's Audit cell" in result.stdout


def test_a_check_that_links_the_card_without_the_audit_cell_fails(
    tmp_path: Path,
) -> None:
    loop = LOOP.replace("/standards/tidy/card.md#audit", "/standards/tidy/card.md")

    result = run(make_repo(tmp_path, loop))

    assert result.returncode == 1
    assert "a check links a card's Audit cell" in result.stdout


def test_a_link_that_does_not_resolve_fails(tmp_path: Path) -> None:
    loop = LOOP.replace("/skills/tidy.md", "/skills/gone.md")

    result = run(make_repo(tmp_path, loop))

    assert result.returncode == 1
    assert (
        "knowledge-organization.loop-entries link '/skills/gone.md' does not resolve"
        in result.stdout
    )


def test_a_yield_with_no_condition_fails(tmp_path: Path) -> None:
    loop = LOOP.replace("yields when three rounds have run", "after three rounds")

    result = run(make_repo(tmp_path, loop))

    assert result.returncode == 1
    assert (
        "knowledge-organization.loop-entries `ask` states no condition" in result.stdout
    )


def test_verb_sections_out_of_order_fail(tmp_path: Path) -> None:
    loop = LOOP.replace("## Checks", "## Measures")

    result = run(make_repo(tmp_path, loop))

    assert result.returncode == 1
    assert "knowledge-organization.loop-sections verb sections are" in result.stdout


def test_two_paragraphs_before_the_graph_fail(tmp_path: Path) -> None:
    loop = LOOP.replace(
        "Drives the repo's tree toward Tidy Tree.\n",
        "Drives the tree.\n\nToward Tidy Tree.\n",
    )

    result = run(make_repo(tmp_path, loop))

    assert result.returncode == 1
    assert (
        "knowledge-organization.loop-graph 2 paragraphs before the graph"
        in result.stdout
    )


def test_a_repo_with_no_loops_tree_is_clean(tmp_path: Path) -> None:
    result = run(make_repo(tmp_path, loop=None))

    assert result.returncode == 0, result.stdout + result.stderr
    assert "0 loop(s)" in result.stderr


def test_list_rules_prints_the_five_rule_ids() -> None:
    result = subprocess.run(
        ["uv", "run", "--script", str(SCRIPT), "--list-rules"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout.split() == [
        "knowledge-organization.loop-edges",
        "knowledge-organization.loop-entries",
        "knowledge-organization.loop-graph",
        "knowledge-organization.loop-nodes",
        "knowledge-organization.loop-sections",
    ]
