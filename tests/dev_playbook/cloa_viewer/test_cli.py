import contextlib
import os
import signal
import socket
import subprocess
import time
from collections.abc import Iterator
from pathlib import Path

import httpx
import pytest
from cloa_viewer_fixtures import add_worktree, build_checkout
from playwright.sync_api import Page, expect
from starlette.applications import Starlette

from dev_playbook.cloa_viewer import cli, registry, state
from dev_playbook.cloa_viewer.entry import Kind, View

# tests/dev_playbook/cloa_viewer/test_cli.py -> the checkout root, which holds
# the .venv the end-to-end test starts the real command from.
REPO_ROOT = Path(__file__).resolve().parents[3]


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
def empty(tmp_path: Path) -> Path:
    """A directory holding no repository at all."""
    nothing = tmp_path / "empty"
    nothing.mkdir()
    return nothing


@pytest.fixture
def unbuilt(tmp_path: Path) -> Path:
    """A stand-in for a web directory ``make web`` has never built."""
    built = tmp_path / "unbuilt"
    built.mkdir()
    return built


def use_dist(monkeypatch: pytest.MonkeyPatch, built: Path) -> None:
    """Point the command at ``built`` instead of the page inside the package."""
    monkeypatch.setattr(cli, "dist_dir", lambda: built)


def record_serve(monkeypatch: pytest.MonkeyPatch) -> list[tuple[Starlette, int]]:
    """Replace the blocking server with a recorder, and return what it records."""
    calls: list[tuple[Starlette, int]] = []
    monkeypatch.setattr(cli, "serve", lambda app, port: calls.append((app, port)))
    return calls


def breaking_generate(checkout: Path) -> list[View]:
    """Stand in for a kind whose generator raises."""
    raise RuntimeError("the generator broke")


def free_port() -> int:
    """A port nothing holds, found by binding one and letting it go again."""
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def start_server(
    checkout: Path, port: int, state_home: Path
) -> subprocess.Popen[bytes]:
    """Start the real command on ``checkout``, and wait until it answers.

    The entry point is run directly rather than through ``uv run``: uv stays
    the parent, so killing it leaves the server holding the port and the event
    stream, and a signal reaches uv rather than the server it wraps.
    """
    server = subprocess.Popen(
        [
            str(REPO_ROOT / ".venv" / "bin" / "cloa-viewer"),
            str(checkout),
            "--port",
            str(port),
        ],
        cwd=REPO_ROOT,
        env={**os.environ, "XDG_STATE_HOME": str(state_home)},
    )
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if server.poll() is not None:
            raise AssertionError(f"cloa-viewer exited with {server.returncode}")
        try:
            httpx.get(f"http://127.0.0.1:{port}/api/checkouts", timeout=1)
        except httpx.HTTPError:
            time.sleep(0.1)
        else:
            return server
    server.kill()
    raise AssertionError("cloa-viewer did not answer within 10 seconds")


@contextlib.contextmanager
def serving(
    source: Path, state_home: Path, port: int
) -> Iterator[subprocess.Popen[bytes]]:
    """Run the real command on ``source`` at ``port``, and yield the process.

    The command serves the page ``make web`` builds inside the package, so a
    checkout that has never built it cannot run this at all: that is a missing
    build step, not a failing viewer, and this says which.

    ``kill`` on the way out is a no-op on a process a test already stopped, so
    a test is free to stop the server itself and read the status it exited with.
    """
    if not (cli.dist_dir() / "index.html").is_file():
        pytest.fail("run make web first")
    running = start_server(source, port, state_home)
    try:
        yield running
    finally:
        running.kill()
        running.wait(timeout=10)


@pytest.fixture
def port() -> int:
    """The port this test's own server holds, so two runs never collide."""
    return free_port()


@pytest.fixture
def server(
    checkout: Path, tmp_path: Path, port: int
) -> Iterator[subprocess.Popen[bytes]]:
    """The real command serving the fixture checkout alone."""
    with serving(checkout, tmp_path, port) as running:
        yield running


@pytest.fixture
def address(server: subprocess.Popen[bytes], port: int) -> str:
    """The address of that server's page."""
    return f"http://127.0.0.1:{port}/"


@pytest.fixture
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A directory of repos, the case one server covering a workspace is for."""
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    return tmp_path / "ws"


@pytest.fixture
def in_workspace(workspace: Path) -> Path:
    """The fixture checkout, sitting inside that directory of repos."""
    return build_checkout(workspace)


@pytest.fixture
def worktree(in_workspace: Path) -> Path:
    """A linked worktree of it, on its own branch and holding one file of its own.

    The branch is the label the toggle shows, and the extra document is what
    tells this checkout's tree from the main checkout's on screen.
    """
    added = add_worktree(in_workspace, "wt")
    (added / "only-here.md").write_text(
        "---\n"
        "type: Guide\n"
        "title: Only here\n"
        "description: The document the worktree alone holds\n"
        "---\n"
        "\n"
        "# Only here\n"
    )
    return added


@pytest.fixture
def workspace_address(
    workspace: Path, worktree: Path, tmp_path: Path, port: int
) -> Iterator[str]:
    """The real command serving that directory: two checkouts of one repo."""
    with serving(workspace, tmp_path, port):
        yield f"http://127.0.0.1:{port}/"


def test_port_defaults_to_8765() -> None:
    assert cli.parse_args([]).port == 8765


def test_port_flag_parses_to_an_integer() -> None:
    assert cli.parse_args(["--port", "9000"]).port == 9000


def test_path_arguments_collect_into_a_list() -> None:
    assert cli.parse_args(["/a", "/b"]).path == ["/a", "/b"]


def test_no_path_argument_is_an_empty_list() -> None:
    assert cli.parse_args([]).path == []


def test_unknown_flag_exits() -> None:
    with pytest.raises(SystemExit):
        cli.parse_args(["--nope"])


def test_an_unbuilt_page_returns_two(
    checkout: Path, unbuilt: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    use_dist(monkeypatch, unbuilt)
    assert cli.main([str(checkout)]) == 2


def test_an_unbuilt_page_names_the_build_command(
    checkout: Path,
    unbuilt: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    use_dist(monkeypatch, unbuilt)
    cli.main([str(checkout)])
    assert capsys.readouterr().err == "page not built: run make web\n"


def test_an_unbuilt_page_refreshes_nothing_and_serves_nothing(
    checkout: Path, unbuilt: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    use_dist(monkeypatch, unbuilt)
    calls = record_serve(monkeypatch)
    cli.main([str(checkout)])
    assert calls == []
    assert not state.checkout_dir(checkout).exists()


def test_the_command_returns_zero_when_the_server_stops(
    checkout: Path, dist: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    use_dist(monkeypatch, dist)
    record_serve(monkeypatch)
    assert cli.main([str(checkout)]) == 0


def test_the_port_reaches_the_server(
    checkout: Path, dist: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    use_dist(monkeypatch, dist)
    calls = record_serve(monkeypatch)
    cli.main([str(checkout), "--port", "9001"])
    assert calls[0][1] == 9001


def test_the_checkout_is_refreshed_before_the_server_starts(
    checkout: Path, dist: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    use_dist(monkeypatch, dist)
    record_serve(monkeypatch)
    cli.main([str(checkout)])
    assert (state.checkout_dir(checkout) / "refresh.json").is_file()
    assert (state.checkout_dir(checkout) / "index-tree.json").is_file()


def test_the_address_is_printed(
    checkout: Path,
    dist: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    use_dist(monkeypatch, dist)
    record_serve(monkeypatch)
    cli.main([str(checkout), "--port", "9001"])
    assert capsys.readouterr().out == "cloa-viewer at http://127.0.0.1:9001/\n"


def test_a_failed_generator_is_named_on_stderr(
    checkout: Path,
    dist: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    broken = Kind(
        name="broken", version=1, per_subject=False, generate=breaking_generate
    )
    monkeypatch.setattr(registry, "KINDS", (broken,))
    use_dist(monkeypatch, dist)
    record_serve(monkeypatch)
    assert cli.main([str(checkout)]) == 0
    assert capsys.readouterr().err == f"refresh failed: broken in {checkout}\n"


def test_a_working_generator_says_nothing_on_stderr(
    checkout: Path,
    dist: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    use_dist(monkeypatch, dist)
    record_serve(monkeypatch)
    cli.main([str(checkout)])
    assert capsys.readouterr().err == ""


def test_no_path_argument_serves_the_repo_holding_the_directory(
    checkout: Path, dist: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    use_dist(monkeypatch, dist)
    calls = record_serve(monkeypatch)
    monkeypatch.chdir(checkout / "docs")
    cli.main([])
    assert calls[0][0].state.sources == [checkout.resolve()]


def test_a_path_holding_no_checkout_returns_two(
    empty: Path, dist: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    use_dist(monkeypatch, dist)
    record_serve(monkeypatch)
    assert cli.main([str(empty)]) == 2


def test_a_path_holding_no_checkout_is_named_on_stderr(
    empty: Path,
    dist: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    use_dist(monkeypatch, dist)
    record_serve(monkeypatch)
    cli.main([str(empty)])
    assert capsys.readouterr().err == f"{empty}: no checkout found\n"


def test_the_current_checkout_is_the_repo_root(
    checkout: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(checkout / "docs")
    assert cli.current_checkout().resolve() == checkout.resolve()


def test_page_shows_tree_and_updates(checkout: Path, address: str, page: Page) -> None:
    page.goto(address)
    expect(page.locator(".tree")).to_contain_text("Harness-owned files")
    expect(page.locator(".tree")).to_contain_text("Not indexed")
    row = page.locator(".tree .tree-row").filter(has_text="Alpha")
    expect(row).to_have_count(1)
    row.click()
    expect(page.locator(".panel-title")).to_have_text("Alpha")
    expect(page.locator(".panel-body")).to_contain_text("Second heading")
    alpha = checkout / "alpha.md"
    alpha.write_text(alpha.read_text() + "\nnine ten\n")
    expect(page.locator(".panel-body")).to_contain_text("nine ten", timeout=5000)


def test_interrupt_stops_the_server_while_a_page_holds_the_stream(
    server: subprocess.Popen[bytes], address: str, page: Page
) -> None:
    page.goto(address)
    expect(page.locator(".tree")).to_be_visible()
    server.send_signal(signal.SIGINT)
    server.wait(timeout=10)
    assert server.returncode == 0


def test_the_toggle_lists_every_discovered_checkout(
    workspace_address: str, page: Page
) -> None:
    page.goto(workspace_address)
    expect(page.locator(".topbar-checkout optgroup")).to_have_attribute(
        "label", "fixture"
    )
    expect(page.locator(".topbar-checkout option")).to_have_count(2)


def test_choosing_a_checkout_swaps_the_tree_and_the_address(
    worktree: Path, workspace_address: str, page: Page
) -> None:
    page.goto(workspace_address)
    unindexed = page.locator(".tree .tree-row").filter(has_text="Not indexed")
    # The main checkout leaves one document unindexed, the worktree two, so the
    # count is the tree saying which checkout it belongs to.
    expect(unindexed).to_contain_text("1 files")
    page.select_option(".topbar-checkout", label="wt")
    expect(page).to_have_url(f"{workspace_address}#{state.checkout_dir(worktree).name}")
    expect(unindexed).to_contain_text("2 files")
    unindexed.click()
    expect(page.locator(".tree")).to_contain_text("Only here")
    expect(page.locator(".tree")).to_contain_text("Alpha")


def test_a_reload_returns_to_the_chosen_checkout(
    worktree: Path, workspace_address: str, page: Page
) -> None:
    page.goto(workspace_address)
    page.select_option(".topbar-checkout", label="wt")
    expect(page).to_have_url(f"{workspace_address}#{state.checkout_dir(worktree).name}")
    page.reload()
    expect(page.locator(".topbar-checkout")).to_have_value(
        state.checkout_dir(worktree).name
    )
