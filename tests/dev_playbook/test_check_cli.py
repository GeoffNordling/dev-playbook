"""Tests for the playbook console script, src/dev_playbook/check_cli.py."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from conftest import commit_all, init_repo

from dev_playbook import check_cli, check_registry
from dev_playbook.check_registry import WORKSPACE, Check, Finding
from dev_playbook.model import Repo


def a_repo(tmp_path: Path, files: dict[str, str]) -> Path:
    root = tmp_path / "repo"
    init_repo(root)
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    commit_all(root)
    return root


def first_line_of_every_markdown(repo: Repo) -> Iterator[Finding]:
    for path in repo.markdown:
        yield Finding(path, 1, "flagged")


def needs_workspace(repo: Repo) -> Iterator[Finding]:
    yield Finding("README.md", None, "needs the workspace")


def fake_registry(monkeypatch: pytest.MonkeyPatch, *entries: Check) -> None:
    monkeypatch.setattr(check_registry, "load", lambda: {e.id: e for e in entries})


class TestChecks:
    def test_lists_id_module_and_hook(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert check_cli.main(["checks"]) == 0
        out = capsys.readouterr().out
        assert "shell.shellcheck-clean\tdev_playbook.checks.shell\tshellcheck\n" in out

    def test_family_filter(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert check_cli.main(["checks", "--family", "nope"]) == 0
        assert capsys.readouterr().out == ""

    def test_without_filter_and_tags(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        fake_registry(
            monkeypatch,
            Check("fam.a", needs_workspace, None, frozenset({WORKSPACE}), "m.fam"),
            Check("fam.b", first_line_of_every_markdown, None, frozenset(), "m.fam"),
        )
        assert check_cli.main(["checks"]) == 0
        assert capsys.readouterr().out == "fam.a\tm.fam\tworkspace\nfam.b\tm.fam\t-\n"
        assert check_cli.main(["checks", "--without", "workspace"]) == 0
        assert capsys.readouterr().out == "fam.b\tm.fam\t-\n"


class TestCheck:
    def test_clean_repo_exits_0(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        root = a_repo(tmp_path, {"README.md": "# R\n"})
        assert check_cli.main(["check", str(root)]) == 0
        captured = capsys.readouterr()
        assert captured.out == ""
        assert "0 finding(s)" in captured.err

    def test_findings_carry_the_rule_id_and_exit_1(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        root = a_repo(tmp_path, {"README.md": "# R\n", "docs/a.md": "# A\n"})
        fake_registry(
            monkeypatch,
            Check("fam.b", first_line_of_every_markdown, None, frozenset(), "m.fam"),
            Check("fam.t", None, "shfmt", frozenset(), "m.fam"),
        )
        assert check_cli.main(["check", str(root)]) == 1
        captured = capsys.readouterr()
        assert (
            captured.out == "README.md:1: fam.b flagged\ndocs/a.md:1: fam.b flagged\n"
        )
        assert "1 check(s)" in captured.err
        assert "2 finding(s)" in captured.err

    def test_without_leaves_out_tagged_checks(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        root = a_repo(tmp_path, {"README.md": "# R\n"})
        fake_registry(
            monkeypatch,
            Check("fam.a", needs_workspace, None, frozenset({WORKSPACE}), "m.fam"),
        )
        assert check_cli.main(["check", str(root)]) == 1
        assert capsys.readouterr().out == "README.md: fam.a needs the workspace\n"
        assert check_cli.main(["check", "--without", "workspace", str(root)]) == 0
        assert capsys.readouterr().out == ""

    def test_unparseable_file_exits_2_and_names_it(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        root = a_repo(tmp_path, {"bad.md": "a\n```\nb\n"})
        assert check_cli.main(["check", str(root)]) == 2
        assert "bad.md: unclosed" in capsys.readouterr().err

    def test_outside_a_git_repo_exits_2(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert check_cli.main(["check", str(tmp_path)]) == 2
        assert "cannot build the model" in capsys.readouterr().err
