import asyncio
import json
from pathlib import Path

import pytest
import watchfiles
from cloa_viewer_fixtures import add_worktree, build_checkout

from dev_playbook.cloa_viewer import refresh, state, watch

ALPHA_VIEW = "markdown-file/alpha.md.json"
APPENDED = "Nine ten eleven twelve.\n"
DEBOUNCE_MS = 50
POLL_SECONDS = 0.05
QUIET_SECONDS = 2.0
SETTLE_SECONDS = 0.5
TIMEOUT_SECONDS = 5.0


@pytest.fixture
def checkout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    return build_checkout(tmp_path)


@pytest.fixture
def worktree(checkout: Path) -> Path:
    """A checkout inside the checkout, at ``.claude/worktrees/wt``."""
    return add_worktree(checkout, "wt")


def source_of(checkout: Path) -> str:
    """The source the last refresh wrote for ``alpha.md``."""
    view = state.checkout_dir(checkout) / ALPHA_VIEW
    source: str = json.loads(view.read_text())["payload"]["source"]
    return source


def refreshed_at(checkout: Path) -> int:
    """When ``refresh.json`` was last written, in nanoseconds.

    The record's own ``finished`` field is an RFC 3339 timestamp to the second,
    and two refreshes a fraction of a second apart carry the same one, so it
    cannot tell a refresh that did not happen from one that did. The file's
    modification time can: every refresh replaces the file.
    """
    record = state.checkout_dir(checkout) / refresh.RECORD_FILE
    return record.stat().st_mtime_ns


async def source_after_an_edit(checkout: Path, before: str) -> str:
    """Append a line to ``alpha.md`` under the watcher, and return the new source.

    The watcher starts first and settles, so the edit lands while it is
    running; the poll then waits for the refresh the edit caused to rewrite the
    view file, and the timeout makes a watcher that never fires a failure
    rather than a hang.
    """
    stop = asyncio.Event()
    watcher = asyncio.create_task(
        watch.watch_checkout(checkout, debounce_ms=DEBOUNCE_MS, stop=stop)
    )
    try:
        await asyncio.sleep(SETTLE_SECONDS)
        alpha = checkout / "alpha.md"
        alpha.write_text(alpha.read_text() + APPENDED)
        loop = asyncio.get_running_loop()
        deadline = loop.time() + TIMEOUT_SECONDS
        while loop.time() < deadline:
            source = source_of(checkout)
            if source != before:
                return source
            await asyncio.sleep(POLL_SECONDS)
        raise AssertionError(f"{ALPHA_VIEW} still reads the source it started with")
    finally:
        stop.set()
        await asyncio.wait_for(watcher, TIMEOUT_SECONDS)


def test_an_edit_in_the_checkout_refreshes_the_file_it_changed(
    checkout: Path,
) -> None:
    refresh.refresh(checkout)
    before = source_of(checkout)
    after = asyncio.run(source_after_an_edit(checkout, before))
    assert after.endswith(APPENDED)


async def refreshed_after_an_edit_in(
    checkout: Path, worktree: Path, before: int
) -> int:
    """Edit a file of ``worktree`` under a watcher of ``checkout`` that ignores it.

    The watcher settles first, so the edit lands while it is running. The poll
    then gives it every chance to refresh anyway, and returns the moment it
    does, so a failure names the time the refresh happened rather than only
    saying the two differ.
    """
    stop = asyncio.Event()
    watcher = asyncio.create_task(
        watch.watch_checkout(
            checkout, ignore=[worktree], debounce_ms=DEBOUNCE_MS, stop=stop
        )
    )
    try:
        await asyncio.sleep(SETTLE_SECONDS)
        alpha = worktree / "alpha.md"
        alpha.write_text(alpha.read_text() + APPENDED)
        loop = asyncio.get_running_loop()
        deadline = loop.time() + QUIET_SECONDS
        while loop.time() < deadline:
            refreshed = refreshed_at(checkout)
            if refreshed != before:
                return refreshed
            await asyncio.sleep(POLL_SECONDS)
        return refreshed_at(checkout)
    finally:
        stop.set()
        await asyncio.wait_for(watcher, TIMEOUT_SECONDS)


def test_an_edit_in_an_ignored_checkout_refreshes_nothing(
    checkout: Path, worktree: Path
) -> None:
    refresh.refresh(checkout)
    before = refreshed_at(checkout)
    assert asyncio.run(refreshed_after_an_edit_in(checkout, worktree, before)) == before


def test_a_path_inside_an_ignored_checkout_is_not_watched() -> None:
    keep = watch.watch_filter([Path("/home/user/repo/.claude/worktrees/wt")])
    assert not keep(
        watchfiles.Change.modified, "/home/user/repo/.claude/worktrees/wt/alpha.md"
    )


def test_a_path_outside_every_ignored_checkout_is_watched() -> None:
    keep = watch.watch_filter([Path("/home/user/repo/.claude/worktrees/wt")])
    assert keep(watchfiles.Change.modified, "/home/user/repo/alpha.md")


def test_a_path_inside_git_is_not_watched() -> None:
    assert not watch.outside_git(
        watchfiles.Change.modified, "/home/user/repo/.git/index"
    )


def test_a_file_of_the_checkout_is_watched() -> None:
    assert watch.outside_git(watchfiles.Change.modified, "/home/user/repo/alpha.md")
