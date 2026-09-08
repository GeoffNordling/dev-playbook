import asyncio
import json
from pathlib import Path

import pytest
import watchfiles
from cloa_viewer_fixtures import build_checkout

from dev_playbook.cloa_viewer import refresh, state, watch

ALPHA_VIEW = "markdown-file/alpha.md.json"
APPENDED = "Nine ten eleven twelve.\n"
APPENDED_WORDS = 4
DEBOUNCE_MS = 50
POLL_SECONDS = 0.05
SETTLE_SECONDS = 0.5
TIMEOUT_SECONDS = 5.0


@pytest.fixture
def checkout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    return build_checkout(tmp_path)


def words_of(checkout: Path) -> int:
    """The word count the last refresh wrote for ``alpha.md``."""
    view = state.checkout_dir(checkout) / ALPHA_VIEW
    words: int = json.loads(view.read_text())["payload"]["words"]
    return words


async def words_after_an_edit(checkout: Path, before: int) -> int:
    """Append a line to ``alpha.md`` under the watcher, and return the new count.

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
            words = words_of(checkout)
            if words != before:
                return words
            await asyncio.sleep(POLL_SECONDS)
        raise AssertionError(f"{ALPHA_VIEW} still reads {before} words")
    finally:
        stop.set()
        await asyncio.wait_for(watcher, TIMEOUT_SECONDS)


def test_an_edit_in_the_checkout_refreshes_the_file_it_changed(
    checkout: Path,
) -> None:
    refresh.refresh(checkout)
    before = words_of(checkout)
    after = asyncio.run(words_after_an_edit(checkout, before))
    assert after == before + APPENDED_WORDS


def test_a_path_inside_git_is_not_watched() -> None:
    assert not watch.outside_git(
        watchfiles.Change.modified, "/home/user/repo/.git/index"
    )


def test_a_file_of_the_checkout_is_watched() -> None:
    assert watch.outside_git(watchfiles.Change.modified, "/home/user/repo/alpha.md")
