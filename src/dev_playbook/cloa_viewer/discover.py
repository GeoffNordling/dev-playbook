"""Discovery: the paths the command was given become the list of checkouts.

This is the first of the server's five jobs
([Server](/worktree-cloa-viewer-tool-working-docs/server.md)).
A path that is a checkout is shown as it is; a path that is not one,
``~/workspace/`` being the case that matters, is scanned for the repos directly
below it and every linked worktree of each. One server then covers the whole
workspace, and repo and branch are chosen on the page rather than on the
command line
([CLOA Viewer](/worktree-cloa-viewer-tool-working-docs/ROOT.md#constraints)).

Git answers which working copies a repo has. ``git worktree list`` knows about
a worktree wherever it sits on disk, including one under the main checkout's
own ``.claude/worktrees/``, so nothing here walks a tree looking for ``.git``
markers and no depth limit has to be invented.

Nothing here reads a checkout's contents or writes anything. The server calls
it again every time the page asks for the checkout list, so it must stay cheap
and free of side effects.
"""

import subprocess
from pathlib import Path

from dev_playbook.gitrepo import no_git_env

BLOCK_SEPARATOR = "\n\n"
GIT_MARKER = ".git"
# A block carrying either names no working copy to show: ``bare`` has no
# working tree at all, and ``prunable`` means git has already decided the
# directory is gone.
SKIPPED_ATTRIBUTES = ("bare", "prunable")
WORKTREE_PREFIX = "worktree "


def is_checkout(path: Path) -> bool:
    """True when ``path`` is a working copy of a repo.

    A main checkout carries a ``.git`` directory and a linked worktree a
    ``.git`` file naming the shared one, so the marker's existence is the whole
    test and its kind is not part of it.
    """
    return (path / GIT_MARKER).exists()


def worktrees(repo: Path) -> list[Path]:
    """Every working copy of ``repo``, the main checkout first, as git lists it.

    ``git worktree list --porcelain`` prints one block per working copy,
    separated by blank lines and beginning with ``worktree <path>``, the main
    checkout first. A block that also carries a ``bare`` or ``prunable`` line
    names nothing to show and is dropped.
    """
    result = subprocess.run(
        ["git", "-C", str(repo), "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
        env=no_git_env(),
    )
    found = []
    for block in result.stdout.split(BLOCK_SEPARATOR):
        lines = block.splitlines()
        if not lines or not lines[0].startswith(WORKTREE_PREFIX):
            continue
        if any(line.split(" ", 1)[0] in SKIPPED_ATTRIBUTES for line in lines):
            continue
        found.append(Path(lines[0][len(WORKTREE_PREFIX) :]).resolve())
    return found


def checkouts(sources: list[Path]) -> list[Path]:
    """Every checkout ``sources`` names, in the order the sources give them.

    A source that is itself a checkout contributes that one path and nothing
    else, so pointing the command at a main checkout shows that checkout even
    when it holds worktrees. Any other source is a directory of repos: every
    immediate child directory that is a checkout contributes all of its working
    copies, the children taken in name order.

    A source of the second sort that yields nothing raises ``ValueError``
    naming it. An empty list would leave the page blank with nothing on screen
    to explain it, and the command turns this into the error it prints before
    it starts the server.
    """
    found: list[Path] = []
    for source in sources:
        if is_checkout(source):
            found.append(source)
            continue
        scanned: list[Path] = []
        for child in sorted(source.iterdir()):
            if child.is_dir() and is_checkout(child):
                scanned.extend(worktrees(child))
        if not scanned:
            raise ValueError(f"{source}: no checkout found")
        found.extend(scanned)
    return list(dict.fromkeys(found))
