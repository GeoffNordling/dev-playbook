"""The checkout watcher: an edit in a checkout becomes a refresh.

This is the second of the server's five jobs
([Server](/worktree-cloa-viewer-tool-working-docs/server.md)):
on any change to a file in the checkout, wait a short settle time, then run
every generator again. A refresh of this repo costs a fraction of a second, so
a whole refresh on every batch is affordable and no change needs a rule of its
own to be seen.

Nothing here talks to the page. The refresh rewrites view files, the state
watcher in ``server`` sees those writes, and the page hears about them from
there, so an edit reaches the screen through the same path a hand-run refresh
does.
"""

import asyncio
from collections.abc import Callable, Sequence
from pathlib import Path

import watchfiles

from dev_playbook.cloa_viewer import refresh

# A refresh runs git, and git writes inside .git. Without this filter the
# refresh would trigger the watcher that started it, forever.
GIT_DIR = ".git"
# Long enough for an editor's save (a write, a rename, a chmod) to land as one
# batch, short enough to leave most of the two-second budget to the refresh and
# the push that follow.
CHECKOUT_DEBOUNCE_MS = 300


def outside_git(change: watchfiles.Change, path: str) -> bool:
    """Whether ``path`` is a file of the checkout rather than one of git's."""
    return GIT_DIR not in Path(path).parts


def watch_filter(
    ignore: Sequence[Path],
) -> Callable[[watchfiles.Change, str], bool]:
    """The filter for a watcher whose checkout holds the checkouts in ``ignore``.

    A linked worktree under the main checkout's ``.claude/worktrees/`` sits
    inside the directory the outer watcher watches, and it is a checkout of its
    own with a watcher and a state directory of its own. Without this an edit
    there would refresh both checkouts, and the outer refresh would be pure
    waste because the worktree's files are not the outer checkout's files.
    """

    def keep(change: watchfiles.Change, path: str) -> bool:
        return outside_git(change, path) and not any(
            Path(path).is_relative_to(other) for other in ignore
        )

    return keep


async def watch_checkout(
    checkout: Path,
    *,
    ignore: Sequence[Path] = (),
    debounce_ms: int = CHECKOUT_DEBOUNCE_MS,
    stop: asyncio.Event | None = None,
) -> None:
    """Refresh ``checkout`` after every settled batch of changes to its files.

    ``ignore`` names the other checkouts that lie inside this one; a change
    below any of them belongs to that checkout's watcher, not this one.

    The refresh is ordinary blocking code, so it runs on a worker thread and
    the server keeps answering every other request while it does.
    """
    async for _ in watchfiles.awatch(
        checkout,
        debounce=debounce_ms,
        stop_event=stop,
        watch_filter=watch_filter(ignore),
    ):
        await asyncio.to_thread(refresh.refresh, checkout)
