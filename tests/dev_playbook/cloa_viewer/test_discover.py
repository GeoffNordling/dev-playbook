from pathlib import Path

import pytest
from cloa_viewer_fixtures import add_worktree, build_checkout

from dev_playbook.cloa_viewer.discover import checkouts, is_checkout


@pytest.fixture
def ws(tmp_path: Path) -> Path:
    return tmp_path / "ws"


@pytest.fixture
def main(ws: Path) -> Path:
    return build_checkout(ws)


@pytest.fixture
def wt(main: Path) -> Path:
    return add_worktree(main, "wt")


def test_a_directory_of_repos_yields_the_repo_and_its_worktree(
    ws: Path, main: Path, wt: Path
) -> None:
    assert checkouts([ws]) == [main, wt]


def test_a_checkout_source_is_the_one_checkout_shown(main: Path, wt: Path) -> None:
    assert checkouts([main]) == [main]


def test_a_directory_holding_no_repo_is_an_error(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(ValueError, match="no checkout found"):
        checkouts([empty])


def test_a_linked_worktree_is_a_checkout(wt: Path) -> None:
    assert is_checkout(wt)


def test_a_directory_of_repos_is_not_itself_a_checkout(ws: Path, main: Path) -> None:
    assert not is_checkout(ws)
