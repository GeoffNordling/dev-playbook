"""The checkout watcher: an edit in a checkout becomes a refresh.

This is the second of the server's four jobs
([Server and Stack](/worktree-cloa-viewer-tool-working-docs/server-and-stack.md)):
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


async def watch_checkout(
    checkout: Path,
    *,
    debounce_ms: int = CHECKOUT_DEBOUNCE_MS,
    stop: asyncio.Event | None = None,
) -> None:
    """Refresh ``checkout`` after every settled batch of changes to its files.

    The refresh is ordinary blocking code, so it runs on a worker thread and
    the server keeps answering every other request while it does.
    """
    async for _ in watchfiles.awatch(
        checkout,
        debounce=debounce_ms,
        stop_event=stop,
        watch_filter=outside_git,
    ):
        await asyncio.to_thread(refresh.refresh, checkout)
