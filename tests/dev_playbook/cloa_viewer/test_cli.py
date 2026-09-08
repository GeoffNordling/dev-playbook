from pathlib import Path

import pytest
from cloa_viewer_fixtures import build_checkout
from starlette.applications import Starlette

from dev_playbook.cloa_viewer import cli, registry, state
from dev_playbook.cloa_viewer.entry import Kind, View


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


def test_port_defaults_to_8765() -> None:
    assert cli.parse_args([]).port == 8765


def test_port_flag_parses_to_an_integer() -> None:
    assert cli.parse_args(["--port", "9000"]).port == 9000


def test_checkout_arguments_collect_into_a_list() -> None:
    assert cli.parse_args(["/a", "/b"]).checkout == ["/a", "/b"]


def test_no_checkout_argument_is_an_empty_list() -> None:
    assert cli.parse_args([]).checkout == []


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


def test_no_checkout_argument_serves_the_repo_holding_the_directory(
    checkout: Path, dist: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    use_dist(monkeypatch, dist)
    calls = record_serve(monkeypatch)
    monkeypatch.chdir(checkout / "docs")
    cli.main([])
    assert list(calls[0][0].state.checkouts) == [state.checkout_dir(checkout).name]


def test_the_current_checkout_is_the_repo_root(
    checkout: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(checkout / "docs")
    assert cli.current_checkout().resolve() == checkout.resolve()
