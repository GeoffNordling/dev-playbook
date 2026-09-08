import asyncio
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import watchfiles
from cloa_viewer_fixtures import build_checkout
from starlette.testclient import TestClient

from dev_playbook.cloa_viewer import refresh, server, state

QUIET_SECONDS = 2.0
SETTLE_SECONDS = 0.5


@pytest.fixture(autouse=True)
def _drop_subscribers() -> Iterator[None]:
    """Leave the module-level subscriber set empty for the next test."""
    yield
    server.SUBSCRIBERS.clear()


@pytest.fixture
def checkout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    return build_checkout(tmp_path)


@pytest.fixture
def dist(tmp_path: Path) -> Path:
    """A stand-in for the built page: one index file and an empty assets tree."""
    built = tmp_path / "dist"
    (built / "assets").mkdir(parents=True)
    (built / "index.html").write_text("<p>cloa-viewer</p>\n")
    return built


@pytest.fixture
def client(checkout: Path, dist: Path) -> TestClient:
    """A client on a server holding the refreshed fixture checkout."""
    refresh.refresh(checkout)
    return TestClient(server.build_app([checkout], dist))


def directory_name(checkout: Path) -> str:
    """The name the server addresses ``checkout`` by."""
    return state.checkout_dir(checkout).name


def test_the_root_serves_the_built_page(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.text == "<p>cloa-viewer</p>\n"


def test_the_kind_list_names_every_registered_kind(client: TestClient) -> None:
    response = client.get("/api/kinds")
    assert response.json() == [
        {"name": "index-tree", "version": 1, "per_subject": False},
        {"name": "markdown-file", "version": 1, "per_subject": True},
    ]


def test_a_schema_is_served_by_name(client: TestClient) -> None:
    response = client.get("/api/schemas/envelope")
    assert "required" in response.json()


def test_an_unregistered_schema_name_is_a_404(client: TestClient) -> None:
    assert client.get("/api/schemas/nope").status_code == 404


def test_a_schema_name_cannot_walk_out_of_the_package(client: TestClient) -> None:
    assert client.get("/api/schemas/..%2F..%2Fpyproject").status_code == 404


def test_the_checkout_list_carries_the_facts_on_disk(
    client: TestClient, checkout: Path
) -> None:
    response = client.get("/api/checkouts")
    assert response.json() == [
        {
            "dir": directory_name(checkout),
            "path": str(checkout.resolve()),
            "repo": "fixture",
            "branch": "main",
            "head": state.head_commit(checkout),
        }
    ]


def test_the_file_list_holds_every_view_file(
    client: TestClient, checkout: Path
) -> None:
    listed = client.get(f"/api/checkouts/{directory_name(checkout)}/files").json()
    assert listed == [
        "index-tree.json",
        "markdown-file/alpha.md.json",
        "markdown-file/docs/beta.md.json",
        "markdown-file/docs/decisions/0001-alpha.md.json",
        "markdown-file/docs/decisions/index.md.json",
        "markdown-file/docs/index.md.json",
        "markdown-file/index.md.json",
        "markdown-file/orphan.md.json",
    ]


def test_a_view_file_is_served_whole(client: TestClient, checkout: Path) -> None:
    response = client.get(
        f"/api/checkouts/{directory_name(checkout)}/view/index-tree.json"
    )
    assert response.json()["kind"] == "index-tree"


def test_a_view_file_below_a_directory_is_served(
    client: TestClient, checkout: Path
) -> None:
    response = client.get(
        f"/api/checkouts/{directory_name(checkout)}/view/markdown-file/alpha.md.json"
    )
    assert response.json()["subject"] == "alpha.md"


def test_a_missing_view_file_is_a_404(client: TestClient, checkout: Path) -> None:
    response = client.get(f"/api/checkouts/{directory_name(checkout)}/view/nope.json")
    assert response.status_code == 404


def test_an_unknown_checkout_is_a_404_everywhere(client: TestClient) -> None:
    assert client.get("/api/checkouts/nope/files").status_code == 404
    assert client.get("/api/checkouts/nope/view/index-tree.json").status_code == 404
    assert client.get("/api/checkouts/nope/refresh").status_code == 404
    assert client.post("/api/checkouts/nope/refresh").status_code == 404


def test_the_refresh_record_is_served(client: TestClient, checkout: Path) -> None:
    record = client.get(f"/api/checkouts/{directory_name(checkout)}/refresh").json()
    assert record["commit"] == state.head_commit(checkout)


def test_posting_a_refresh_runs_every_generator(
    client: TestClient, checkout: Path
) -> None:
    record = client.post(f"/api/checkouts/{directory_name(checkout)}/refresh").json()
    assert [generator["kind"] for generator in record["generators"]] == [
        "index-tree",
        "markdown-file",
    ]
    assert [generator["status"] for generator in record["generators"]] == ["ok", "ok"]


def test_a_published_message_reaches_every_subscriber() -> None:
    first = server.subscribe()
    second = server.subscribe()
    message: dict[str, Any] = {
        "event": "changed",
        "checkout": "fixture-0badcafe",
        "path": "markdown-file/alpha.md.json",
    }
    server.publish(message)
    assert first.get_nowait() == message
    assert second.get_nowait() == message


def test_a_dropped_subscriber_gets_no_message() -> None:
    queue = server.subscribe()
    server.unsubscribe(queue)
    server.publish({"event": "changed", "checkout": "x", "path": "y.json"})
    with pytest.raises(asyncio.QueueEmpty):
        queue.get_nowait()


async def collect_messages(checkout: Path) -> list[dict[str, Any]]:
    """Watch the state directory across one refresh, and return what it published."""
    queue = server.subscribe()
    watcher = asyncio.create_task(server.watch_state())
    try:
        await asyncio.sleep(SETTLE_SECONDS)
        await asyncio.to_thread(refresh.refresh, checkout)
        messages = []
        while True:
            try:
                messages.append(await asyncio.wait_for(queue.get(), QUIET_SECONDS))
            except TimeoutError:
                return messages
    finally:
        watcher.cancel()
        server.unsubscribe(queue)


def test_republishing_a_kind_removes_no_view_file_that_still_exists(
    checkout: Path,
) -> None:
    refresh.refresh(checkout)
    messages = asyncio.run(collect_messages(checkout))
    assert [message for message in messages if message["event"] == "removed"] == []
    assert {"event": "refreshed", "checkout": directory_name(checkout)} in messages


def test_republishing_a_kind_announces_every_view_file_it_wrote(
    checkout: Path,
) -> None:
    refresh.refresh(checkout)
    messages = asyncio.run(collect_messages(checkout))
    changed = {message["path"] for message in messages if message["event"] == "changed"}
    assert "markdown-file/alpha.md.json" in changed
    assert "index-tree.json" in changed


def test_a_written_view_file_becomes_a_changed_message(tmp_path: Path) -> None:
    messages = server.messages_for(
        watchfiles.Change.modified,
        tmp_path / "fixture-0badcafe" / "markdown-file" / "alpha.md.json",
        tmp_path,
    )
    assert messages == [
        {
            "event": "changed",
            "checkout": "fixture-0badcafe",
            "path": "markdown-file/alpha.md.json",
        }
    ]


def test_a_deleted_view_file_becomes_a_removed_message(tmp_path: Path) -> None:
    messages = server.messages_for(
        watchfiles.Change.deleted,
        tmp_path / "fixture-0badcafe" / "index-tree.json",
        tmp_path,
    )
    assert messages == [
        {
            "event": "removed",
            "checkout": "fixture-0badcafe",
            "path": "index-tree.json",
        }
    ]


def test_a_deleted_view_file_that_is_there_again_becomes_a_changed_message(
    tmp_path: Path,
) -> None:
    view = tmp_path / "fixture-0badcafe" / "index-tree.json"
    view.parent.mkdir(parents=True)
    view.write_text("{}\n")
    messages = server.messages_for(watchfiles.Change.deleted, view, tmp_path)
    assert messages == [
        {
            "event": "changed",
            "checkout": "fixture-0badcafe",
            "path": "index-tree.json",
        }
    ]


def test_a_republished_directory_becomes_one_message_per_view_file(
    tmp_path: Path,
) -> None:
    kind = tmp_path / "fixture-0badcafe" / "markdown-file"
    (kind / "docs").mkdir(parents=True)
    (kind / "alpha.md.json").write_text("{}\n")
    (kind / "docs" / "beta.md.json").write_text("{}\n")
    messages = server.messages_for(watchfiles.Change.added, kind, tmp_path)
    assert messages == [
        {
            "event": "changed",
            "checkout": "fixture-0badcafe",
            "path": "markdown-file/alpha.md.json",
        },
        {
            "event": "changed",
            "checkout": "fixture-0badcafe",
            "path": "markdown-file/docs/beta.md.json",
        },
    ]


def test_the_refresh_record_becomes_a_refreshed_message(tmp_path: Path) -> None:
    messages = server.messages_for(
        watchfiles.Change.modified,
        tmp_path / "fixture-0badcafe" / "refresh.json",
        tmp_path,
    )
    assert messages == [{"event": "refreshed", "checkout": "fixture-0badcafe"}]


def test_the_staging_tree_and_the_checkout_facts_carry_no_message(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "fixture-0badcafe"
    staged = directory / ".staging" / "markdown-file" / "alpha.md.json"
    assert server.messages_for(watchfiles.Change.added, staged, tmp_path) == []
    facts = directory / "checkout.json"
    assert server.messages_for(watchfiles.Change.modified, facts, tmp_path) == []
    partial = directory / "index-tree.tmp"
    assert server.messages_for(watchfiles.Change.added, partial, tmp_path) == []
