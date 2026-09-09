"""The one fixture checkout every cloa-viewer suite reads.

Nine markdown files, one of every class ``md.classify`` answers: a root index
listing a document and a directory, that document with frontmatter and four
links — one resolving, one broken, a Citation of this repo and a Citation of
another — a docs index listing one document and a directory, that document, a
decisions index, a numbered Decision Record whose two links are one resolving
and one gone, an orphan no index reaches, a harness-owned ``CLAUDE.md``, and an
excluded ``PLAN.md`` that must reach neither the tree nor a view file.

The tenth file is a ``.gitignore`` holding ``.claude/worktrees/``, so a worktree
``add_worktree`` puts there stays out of the main checkout's ``git_files``, the
way this workspace's own repos are arranged.

It sits here, beside ``transcript_fakes``, rather than in a ``conftest.py``
under ``tests/dev_playbook/cloa_viewer/``. A second ``conftest.py`` anywhere
under ``tests/`` shadows the root one, because pytest prepends each collected
file's directory to ``sys.path``: the seven suites that read
``from conftest import init_repo`` would find that file instead and fail to
collect. ``tests/`` is also the only directory both pytest and mypy resolve a
bare import from, mypy through ``mypy_path``.

A test module wraps ``build_checkout`` in a three-line ``checkout`` fixture of
its own rather than importing a fixture, because ruff reads an imported fixture
as redefined by every test that takes it as a parameter (F811).
"""

import subprocess
from pathlib import Path

from conftest import commit_all, init_repo

from dev_playbook.gitrepo import no_git_env

WORKTREES_DIR = ".claude/worktrees"

FILES = {
    ".gitignore": f"{WORKTREES_DIR}/\n",
    "index.md": (
        "# Fixture — index\n"
        "\n"
        "The fixture bundle. Two documents and a directory.\n"
        "\n"
        "- [Alpha](/alpha.md) — The alpha document\n"
        "- [docs/](/docs/index.md) — The docs directory\n"
    ),
    "alpha.md": (
        "---\n"
        "type: Guide\n"
        "title: Alpha\n"
        "description: The alpha document\n"
        "---\n"
        "\n"
        "# Alpha\n"
        "\n"
        "One two three [beta](/docs/beta.md) and [gone](/missing.md).\n"
        "\n"
        "## Second heading\n"
        "\n"
        "Four five.\n"
        "\n"
        "See [beta again](~/workspace/fixture/docs/beta.md#beta) and "
        "[afar](~/workspace/elsewhere/notes.md).\n"
    ),
    "docs/index.md": (
        "# docs — index\n"
        "\n"
        "The docs directory.\n"
        "\n"
        "- [Beta](/docs/beta.md) — The beta document\n"
        "- [decisions/](/docs/decisions/index.md) — The decisions directory\n"
    ),
    "docs/beta.md": (
        "---\n"
        "type: Guide\n"
        "title: Beta\n"
        "description: The beta document\n"
        "---\n"
        "\n"
        "# Beta\n"
        "\n"
        "Six.\n"
    ),
    "docs/decisions/index.md": (
        "# decisions — index\n"
        "\n"
        "The fixture decisions.\n"
        "\n"
        "- [Alpha decided](/docs/decisions/0001-alpha.md) — The fixture decision\n"
    ),
    "docs/decisions/0001-alpha.md": (
        "---\n"
        "type: Decision-Record\n"
        "title: Alpha decided\n"
        "description: The fixture decision\n"
        "---\n"
        "\n"
        "# Alpha decided\n"
        "\n"
        "See [alpha](/alpha.md) and [gone](/gone.md).\n"
    ),
    "orphan.md": "# Orphan\n\nSeven eight.\n",
    "CLAUDE.md": "Read the index first.\n",
    "PLAN.md": "# Plan\n\n- [ ] nothing\n",
}


def build_checkout(tmp_path: Path) -> Path:
    """Write and commit a checkout holding the files above; return its root."""
    repo = tmp_path / "fixture"
    init_repo(repo)
    for relpath, text in FILES.items():
        path = repo / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    commit_all(repo)
    return repo


def add_worktree(checkout: Path, name: str) -> Path:
    """Add a linked worktree of ``checkout`` on a new branch ``name``; return its root.

    It lands under ``.claude/worktrees/``, which the fixture's ``.gitignore``
    covers, so the main checkout's file list does not grow the worktree's copy
    of every file. The branch is new, so the label the page shows for it differs
    from the main checkout's.
    """
    path = checkout / WORKTREES_DIR / name
    subprocess.run(
        ["git", "-C", str(checkout), "worktree", "add", str(path), "-b", name],
        check=True,
        capture_output=True,
        env=no_git_env(),
    )
    return path
