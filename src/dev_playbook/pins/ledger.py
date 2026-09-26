"""The ledger: one row per governed repo per release, on dev-playbook ``main``.

``docs/pin-updates.md`` in dev-playbook is a ``Log`` whose last section is one
table: time, release head, repo, verdict, landing, notes. ``update-pins``
appends its rows there and commits them, so the release history of the
workspace reads in ``git log`` and the IDE. The commit changes the ledger
alone, which is the property ``release.release_head`` relies on to step over
it.

The ledger is also the trigger. A repo with a row at the release head,
whatever its verdict, is done for that release; ``recorded`` is how a run
learns what is left.

**The table holds the last three release heads.** Each ``record`` drops the
rows of older heads in the same commit that appends the new ones, so the page
stays short and reads as recent history. Nothing is lost: every dropped row is
in ``git log -p docs/pin-updates.md``. The trigger reads only the current
head's rows, which are always kept.
"""

from dataclasses import dataclass
from pathlib import Path

from dev_playbook.errors import ToolError
from dev_playbook.pins.release import (
    HOOK_REPO_ROOT,
    LEDGER,
    hook_repo_slug,
    published_file,
)
from dev_playbook.pins.worktree import fetch_origin, git_out, probe_worktree

HEADER = "| Time (UTC) | Release head | Repo | Verdict | Landing | Notes |"
RULE = "|---|---|---|---|---|---|"
# How many release heads the table keeps; older heads' rows live in git history.
KEEP_HEADS = 3


@dataclass(frozen=True)
class Row:
    """One ledger row: one repo's outcome at one release head in one run."""

    time: str
    head: str
    repo: str
    verdict: str
    landing: str
    notes: str

    def render(self) -> str:
        """The row as the ledger table carries it."""
        cells = (
            self.time,
            self.head[:12],
            self.repo,
            self.verdict,
            self.landing,
            self.notes,
        )
        return "| " + " | ".join(cell.replace("|", "/") for cell in cells) + " |"


def rows(text: str) -> list[tuple[str, ...]]:
    """The cells of every data row in the ledger's table, in file order."""
    return [cells for line in text.splitlines() if (cells := _cells(line))]


def _cells(line: str) -> tuple[str, ...] | None:
    """The cells of ``line`` when it is a data row of the table, else None."""
    stripped = line.strip()
    if not stripped.startswith("|"):
        return None
    cells = tuple(cell.strip() for cell in stripped.strip("|").split("|"))
    if cells[:2] == ("Time (UTC)", "Release head") or set(cells[0]) <= {"-"}:
        return None
    return cells


def trim(text: str, keep: int = KEEP_HEADS) -> str:
    """``text`` with only the rows of the newest ``keep`` release heads.

    Heads are ordered by their first row in the file, which the append-only
    table makes the order they were released. Every line that is not a data
    row — the frontmatter, the prose, the header — is kept as it stands.
    """
    heads: list[str] = []
    for cells in rows(text):
        if cells[1] not in heads:
            heads.append(cells[1])
    kept = set(heads[-keep:])
    return "".join(
        line
        for line in text.splitlines(keepends=True)
        if (row := _cells(line)) is None or row[1] in kept
    )


def recorded(text: str, head: str) -> set[str]:
    """The repos the ledger already carries a row for at ``head``."""
    return {cells[2] for cells in rows(text) if head.startswith(cells[1])}


def published(*, required: bool) -> str:
    """The ledger as dev-playbook's ``main`` has it, or empty when absent and not required."""
    text = published_file(hook_repo_slug(), LEDGER)
    if text is None:
        if required:
            raise ToolError(
                f"no {LEDGER} on {hook_repo_slug()} main; update-pins records "
                "into that file and cannot run without it"
            )
        return ""
    return text


def record(new_rows: list[Row], hook_repo: Path | None = None) -> str:
    """Append ``new_rows`` to the ledger on dev-playbook ``origin/main``, trim, push; the commit sha.

    In a throwaway worktree, so the checkout this command runs from — the
    timer's main checkout, or a session's worktree — is never written. The
    commit touches the ledger alone, so it carries ``[skip ci]``.
    """
    repo = hook_repo if hook_repo is not None else HOOK_REPO_ROOT
    fetch_origin(repo)
    with probe_worktree(repo) as tree:
        ledger = tree / LEDGER
        if not ledger.is_file():
            raise ToolError(f"no {LEDGER} in {repo} at origin/main")
        text = ledger.read_text(encoding="utf-8")
        if not text.endswith("\n"):
            text += "\n"
        text += "".join(row.render() + "\n" for row in new_rows)
        ledger.write_text(trim(text), encoding="utf-8")
        git_out(tree, "add", LEDGER)
        heads = sorted({row.head[:12] for row in new_rows})
        git_out(
            tree,
            "commit",
            "-q",
            "-m",
            f"Pin updates: {len(new_rows)} row(s) at {', '.join(heads)}\n\n[skip ci]",
        )
        sha = git_out(tree, "rev-parse", "HEAD")
        git_out(tree, "push", "-q", "origin", "HEAD:main")
    return sha
