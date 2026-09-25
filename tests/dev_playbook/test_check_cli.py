"""Tests for the playbook console script, src/dev_playbook/check_cli.py."""

import os
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


def nothing_found(repo: Repo) -> Iterator[Finding]:
    yield from ()


def needs_workspace(repo: Repo) -> Iterator[Finding]:
    yield Finding("README.md", None, "needs the workspace")


def fake_registry(monkeypatch: pytest.MonkeyPatch, *entries: Check) -> None:
    monkeypatch.setattr(
        check_registry, "load", lambda repo=None: {e.id: e for e in entries}
    )


class TestChecks:
    def test_lists_id_module_and_hook(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert check_cli.main(["checks"]) == 0
        out = capsys.readouterr().out
        assert "shell.shellcheck-clean\tdev_playbook.checks.shell\tshellcheck\n" in out

    def test_family_filter(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert check_cli.main(["checks", "--family", "nope"]) == 0
        assert capsys.readouterr().out == ""

    def test_without_filter_and_tags(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        root = str(a_repo(tmp_path, {"README.md": "# R\n"}))
        fake_registry(
            monkeypatch,
            Check("fam.a", needs_workspace, None, frozenset({WORKSPACE}), "m.fam"),
            Check("fam.b", first_line_of_every_markdown, None, frozenset(), "m.fam"),
        )
        assert check_cli.main(["checks", root]) == 0
        assert capsys.readouterr().out == "fam.a\tm.fam\tworkspace\nfam.b\tm.fam\t-\n"
        assert check_cli.main(["checks", root, "--without", "workspace"]) == 0
        assert capsys.readouterr().out == "fam.b\tm.fam\t-\n"


class TestCheck:
    def test_clean_repo_exits_0(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        root = a_repo(tmp_path, {"README.md": "# R\n"})
        fake_registry(
            monkeypatch,
            Check("fam.n", nothing_found, None, frozenset(), "m.fam"),
        )
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


RULES = """\
# Local

## No todo

No tracked text file holds the word TODO.

`local.no-todo` · deterministic
"""

LOCAL_CHECKS = """\
from dev_playbook.check_registry import Finding, check


@check("local.no-todo")
def no_todo(repo):
    for path in repo.files:
        if b"TODO" in repo.contents[path] and path.startswith("notes/"):
            yield Finding(path, None, "holds TODO")
"""

LOCAL_TESTS = "def test_no_todo():\n    pass\n"

PYPROJECT = '[project]\nname = "local-repo"\n'


class TestRepoChecks:
    def test_local_runs_the_repo_checks_and_not_dev_playbooks(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        root = a_repo(
            tmp_path,
            {
                "pyproject.toml": PYPROJECT,
                "standards/local/rules.md": RULES,
                "src/local_repo/checks/local.py": LOCAL_CHECKS,
                "tests/local_repo/checks/test_local.py": LOCAL_TESTS,
                "notes/a.txt": "TODO\n",
            },
        )
        assert check_cli.main(["check", "--local", str(root)]) == 1
        captured = capsys.readouterr()
        assert captured.out == "notes/a.txt: local.no-todo holds TODO\n"
        assert "1 local check(s)" in captured.err
        assert check_cli.main(["checks", "--local", str(root)]) == 0
        assert capsys.readouterr().out == "local.no-todo\tlocal_repo.checks.local\t-\n"

    def test_without_local_the_repo_checks_are_not_loaded(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        root = a_repo(
            tmp_path,
            {
                "pyproject.toml": PYPROJECT,
                "standards/local/rules.md": RULES,
                "src/local_repo/checks/local.py": "import not_installed_here\n",
            },
        )
        assert check_cli.main(["checks", str(root), "--family", "local"]) == 0
        assert capsys.readouterr().out == ""

    def test_a_repo_check_imports_the_repo_package(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        imports = LOCAL_CHECKS.replace(
            "from dev_playbook", "from local_repo.words import WORD\nfrom dev_playbook"
        ).replace('b"TODO"', "WORD")
        root = a_repo(
            tmp_path,
            {
                "pyproject.toml": PYPROJECT,
                "standards/local/rules.md": RULES,
                "src/local_repo/__init__.py": "",
                "src/local_repo/words.py": 'WORD = b"TODO"\n',
                "src/local_repo/checks/__init__.py": "",
                "src/local_repo/checks/local.py": imports,
                "tests/local_repo/checks/test_local.py": LOCAL_TESTS,
                "notes/a.txt": "TODO\n",
            },
        )
        monkeypatch.syspath_prepend(str(root / "src"))
        assert check_cli.main(["check", "--local", str(root)]) == 1
        assert capsys.readouterr().out == "notes/a.txt: local.no-todo holds TODO\n"

    def test_local_over_dev_playbook_exits_2(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        root = a_repo(
            tmp_path, {"pyproject.toml": '[project]\nname = "dev-playbook"\n'}
        )
        assert check_cli.main(["check", "--local", str(root)]) == 2
        assert "run without --local" in capsys.readouterr().err

    def test_a_rule_with_no_check_exits_2(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        root = a_repo(tmp_path, {"standards/local/rules.md": RULES})
        assert check_cli.main(["check", "--local", str(root)]) == 2
        assert (
            "playbook check: local.no-todo: the rule in standards/local/rules.md "
            "has no check" in capsys.readouterr().err
        )

    def test_a_check_with_no_test_exits_2(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        root = a_repo(
            tmp_path,
            {
                "pyproject.toml": PYPROJECT,
                "standards/local/rules.md": RULES,
                "src/local_repo/checks/local.py": LOCAL_CHECKS,
            },
        )
        assert check_cli.main(["check", "--local", str(root)]) == 2
        assert (
            "local.no-todo: no test_no_todo in tests/local_repo/checks/test_local.py"
            in capsys.readouterr().err
        )

    def test_a_module_that_cannot_register_exits_2(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        root = a_repo(
            tmp_path,
            {
                "pyproject.toml": PYPROJECT,
                "src/local_repo/checks/other.py": LOCAL_CHECKS,
            },
        )
        assert check_cli.main(["check", "--local", str(root)]) == 2
        assert (
            "cannot load repo's checks: local.no-todo: registered from module "
            "other, not local" in capsys.readouterr().err
        )


FAKE_UVX = """\
#!/bin/sh
echo "$@" > "$FAKE_UVX_LOG"
echo 'bad manifest' >&2
exit 1
"""


class TestSteps:
    def test_skip_names_a_tag(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        # SKIP=workspace, the line a CI file sets, is --without workspace.
        root = a_repo(tmp_path, {"README.md": "# R\n"})
        fake_registry(
            monkeypatch,
            Check("fam.a", needs_workspace, None, frozenset({WORKSPACE}), "m.fam"),
        )
        monkeypatch.setenv("SKIP", "ruff-check,workspace")
        assert check_cli.main(["check", str(root)]) == 0
        captured = capsys.readouterr()
        assert captured.out == ""
        assert "playbook check: without workspace" in captured.err

    def test_validate_manifest_runs_where_a_manifest_exists(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        # A fake uvx on PATH stands in for pre-commit: it records its argv and
        # fails, so the step's exit reaches the aggregate.
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        fake = bin_dir / "uvx"
        fake.write_text(FAKE_UVX)
        fake.chmod(0o755)
        log = tmp_path / "uvx.log"
        monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ['PATH']}")
        monkeypatch.setenv("FAKE_UVX_LOG", str(log))
        fake_registry(monkeypatch)
        plain = a_repo(tmp_path / "a", {"README.md": "# R\n"})
        assert check_cli.main(["check", str(plain)]) == 0
        assert not log.exists()
        publisher = a_repo(
            tmp_path / "b", {"README.md": "# R\n", ".pre-commit-hooks.yaml": "[]\n"}
        )
        assert check_cli.main(["check", str(publisher)]) == 1
        assert log.read_text().split() == [
            "pre-commit",
            "validate-manifest",
            str(publisher / ".pre-commit-hooks.yaml"),
        ]
        capsys.readouterr()
