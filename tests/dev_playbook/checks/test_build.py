"""Unit tests for the build family's checks."""

from collections.abc import Callable, Iterator
from pathlib import Path

from conftest import init_repo

from dev_playbook.check_registry import Finding
from dev_playbook.checks.build import (
    carry_the_uv_shebang,
    ciyml_byte_identical,
    dependencies_live_in_pyprojecttoml,
    entry_points_resolve_to_main,
    files_every_repo_carries,
    gitignore_holds_every_canonical_pattern,
    has_tests,
    holds_every_canonical_block,
    lock_file_tracked_python_version_pinned,
    makefile_holds_its_layers_targets,
    names_the_project_and_package,
    no_other_future_work_file,
    one_at_the_root_or_none,
    one_package_under_src,
    one_version_set,
    pyprojecttoml_matches_every_pinned_value,
    python_version_byte_identical,
    runnables_live_in_scripts,
)
from dev_playbook.model import Repo

Check = Callable[[Repo], Iterator[Finding]]
C = "standards/build/canonical/"

CANON_PYPROJECT = b"""\
[project]
name = "<repo>"
requires-python = ">=3.14"

[build-system]
requires = ["uv_build>=0.11,<0.12"]
build-backend = "uv_build"

[tool.pytest.ini_options]
testpaths = ["tests"]

[dependency-groups]
dev = ["mypy>=2.0", "ruff>=0.15.20"]

[tool.ruff]
target-version = "py314"
line-length = 88

[tool.ruff.lint]
select = ["E", "D"]
ignore = ["E501"]

[tool.ruff.lint.pydocstyle]
convention = "pep257"

[tool.ruff.lint.isort]
known-first-party = ["<package>"]

[tool.mypy]
python_version = "3.14"
disallow_untyped_defs = true
"""

CANON_CONFIG = b"""\
repos:
  - repo: https://github.com/GeoffNordling/dev-playbook
    rev: <pinned-sha>
    hooks:
      - id: playbook-lint
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.20
    hooks:
      - id: ruff-check
  - repo: local
    hooks:
      - id: make-check
"""

CANON = {
    C + ".gitignore": b"# caches\n__pycache__/\n.venv/\n",
    C + ".pre-commit-config.yaml": CANON_CONFIG,
    C + ".python-version": b"3.14\n",
    C + "Makefile.base": b"check:\n\tuvx pre-commit run --all-files\n",
    C + "Makefile.python": b"typecheck:\n\tuv run mypy <code-roots>\n",
    C + "ci.yml": b"name: ci\n",
    C + "pyproject.toml": CANON_PYPROJECT,
}

GOOD_PYPROJECT = CANON_PYPROJECT.replace(b"<repo>", b"my-repo").replace(
    b"<package>", b"my_repo"
)


def found(
    run: Check, contents: dict[str, bytes], executable: tuple[str, ...] = ()
) -> list[tuple[str, int | None]]:
    repo = Repo.from_files(Path("/r"), contents, executable)
    return [(f.path, f.line) for f in run(repo)]


def test_files_every_repo_carries() -> None:
    base = {
        "README.md": b"# R\n",
        "CLAUDE.md": b"# C\n",
        "index.md": b"# I\n",
        ".gitignore": b"",
        ".pre-commit-config.yaml": b"repos: []\n",
        "Makefile": b"",
        ".github/workflows/ci.yml": b"",
    }
    assert found(files_every_repo_carries, base) == []
    missing = {k: v for k, v in base.items() if k not in ("CLAUDE.md", "Makefile")}
    assert found(files_every_repo_carries, missing) == [
        ("CLAUDE.md", None),
        ("Makefile", None),
    ]


def test_one_at_the_root_or_none() -> None:
    root = {"pyproject.toml": b"", "CONTEXT.md": b"", "CANDIDATES.md": b""}
    assert found(one_at_the_root_or_none, {**root, **CANON}) == []
    nested = {"sub/pyproject.toml": b"", "docs/CONTEXT.md": b"", "a/CANDIDATES.md": b""}
    assert found(one_at_the_root_or_none, nested) == [
        ("a/CANDIDATES.md", None),
        ("docs/CONTEXT.md", None),
        ("sub/pyproject.toml", None),
    ]


def test_no_other_future_work_file() -> None:
    assert found(no_other_future_work_file, {"CANDIDATES.md": b""}) == []
    assert found(
        no_other_future_work_file, {"TODO.md": b"", "docs/ROADMAP.md": b""}
    ) == [("TODO.md", None), ("docs/ROADMAP.md", None)]


def test_runnables_live_in_scripts() -> None:
    assert found(runnables_live_in_scripts, {"scripts/go": b"", "a/bin/x": b""}) == []
    assert found(runnables_live_in_scripts, {"bin/go": b"", "tools/x/y": b""}) == [
        ("bin/", None),
        ("tools/", None),
    ]


def test_dependencies_live_in_pyprojecttoml() -> None:
    assert found(dependencies_live_in_pyprojecttoml, {"pyproject.toml": b""}) == []
    assert found(dependencies_live_in_pyprojecttoml, {"a/requirements.txt": b""}) == [
        ("a/requirements.txt", None)
    ]


def test_lock_file_tracked_python_version_pinned() -> None:
    assert found(lock_file_tracked_python_version_pinned, {"README.md": b""}) == []
    pinned = {"pyproject.toml": b"", "uv.lock": b"", ".python-version": b"3.14\n"}
    assert found(lock_file_tracked_python_version_pinned, pinned) == []
    assert found(lock_file_tracked_python_version_pinned, {"pyproject.toml": b""}) == [
        ("uv.lock", None),
        (".python-version", None),
    ]


def test_one_package_under_src() -> None:
    good = {"pyproject.toml": GOOD_PYPROJECT, "src/my_repo/__init__.py": b""}
    assert found(one_package_under_src, good) == []
    bad = {
        "pyproject.toml": GOOD_PYPROJECT,
        "src/other/__init__.py": b"",
        "src/loose.py": b"",
    }
    assert found(one_package_under_src, bad) == [
        ("src/loose.py", None),
        ("src/other", None),
        ("src/my_repo/", None),
    ]


def test_tests_present() -> None:
    assert found(has_tests, {"scripts/run.sh": b"echo\n"}) == []
    assert found(has_tests, {"scripts/a.py": b"", "tests/test_a.py": b""}) == []
    assert found(has_tests, {"pyproject.toml": b"", "src/p/__init__.py": b""}) == [
        ("tests/", None)
    ]


def test_ciyml_byte_identical_to_canonical() -> None:
    same = {**CANON, ".github/workflows/ci.yml": b"name: ci\n"}
    assert found(ciyml_byte_identical, same) == []
    assert found(ciyml_byte_identical, {".github/workflows/ci.yml": b"x\n"}) == []
    differs = {**CANON, ".github/workflows/ci.yml": b"name: ci \n"}
    assert found(ciyml_byte_identical, differs) == [(".github/workflows/ci.yml", None)]


def test_python_version_byte_identical_to_canonical() -> None:
    assert (
        found(python_version_byte_identical, {**CANON, ".python-version": b"3.14\n"})
        == []
    )
    assert found(
        python_version_byte_identical, {**CANON, ".python-version": b"3.13\n"}
    ) == [(".python-version", None)]


def test_pre_commit_configyaml_holds_every_canonical_block() -> None:
    extended = CANON_CONFIG.replace(
        b"      - id: ruff-check\n", b"      - id: ruff-check\n      - id: extra\n"
    )
    good = {**CANON, ".pre-commit-config.yaml": extended}
    assert found(holds_every_canonical_block, good) == []
    dropped = CANON_CONFIG.replace(b"    rev: v0.15.20\n", b"    rev: v0.1.0\n")
    assert found(
        holds_every_canonical_block, {**CANON, ".pre-commit-config.yaml": dropped}
    ) == [(".pre-commit-config.yaml", None)]


def test_makefile_holds_its_layers_targets() -> None:
    base = {**CANON, "Makefile": b"all:\ncheck:\n\tuvx pre-commit run --all-files\n"}
    assert found(makefile_holds_its_layers_targets, base) == []
    python = {
        **CANON,
        "pyproject.toml": b"",
        "src/p/a.py": b"",
        "tests/test_a.py": b"",
        "Makefile": b"typecheck:\n\tuv run mypy src tests\n",
    }
    assert found(makefile_holds_its_layers_targets, python) == []
    wrong_roots = {**python, "scripts/b.py": b""}
    assert found(makefile_holds_its_layers_targets, wrong_roots) == [("Makefile", None)]


def test_pyprojecttoml_matches_every_pinned_value() -> None:
    good = {**CANON, "pyproject.toml": GOOD_PYPROJECT, "src/my_repo/a.py": b""}
    assert found(pyprojecttoml_matches_every_pinned_value, good) == []
    drifted = GOOD_PYPROJECT.replace(b"line-length = 88", b"line-length = 100")
    assert found(
        pyprojecttoml_matches_every_pinned_value,
        {**good, "pyproject.toml": drifted},
    ) == [("pyproject.toml", None)]
    scripts_only = {**CANON, "pyproject.toml": GOOD_PYPROJECT}
    assert found(pyprojecttoml_matches_every_pinned_value, scripts_only) == [
        ("pyproject.toml", None),
        ("pyproject.toml", None),
    ]
    assert found(
        pyprojecttoml_matches_every_pinned_value, {"pyproject.toml": b"["}
    ) == [("pyproject.toml", None)]


def test_gitignore_holds_every_canonical_pattern() -> None:
    good = {**CANON, ".gitignore": b".venv/\n__pycache__/\nnode_modules/\n"}
    assert found(gitignore_holds_every_canonical_pattern, good) == []
    assert found(
        gitignore_holds_every_canonical_pattern, {**CANON, ".gitignore": b".venv/\n"}
    ) == [(".gitignore", None)]


def test_one_version_set() -> None:
    assert found(one_version_set, CANON) == []
    assert found(one_version_set, {"pyproject.toml": b"["}) == []
    off = {
        **CANON,
        C + ".python-version": b"3.13\n",
        C + ".pre-commit-config.yaml": CANON_CONFIG.replace(b"v0.15.20", b"v0.16.0"),
    }
    assert found(one_version_set, off) == [
        (C + "pyproject.toml", None),
        (C + "pyproject.toml", None),
        (C + "pyproject.toml", None),
        (C + ".pre-commit-config.yaml", None),
    ]


def test_the_repo_directory_names_the_project_and_package(tmp_path: Path) -> None:
    root = tmp_path / "My-Repo"
    init_repo(root)
    good = Repo.from_files(root, {"pyproject.toml": GOOD_PYPROJECT})
    assert list(names_the_project_and_package(good)) == []
    renamed = GOOD_PYPROJECT.replace(b'name = "my-repo"', b'name = "My-Repo"')
    bad = Repo.from_files(root, {"pyproject.toml": renamed})
    assert [(f.path, f.line) for f in names_the_project_and_package(bad)] == [
        ("pyproject.toml", None)
    ]


def test_every_entry_point_resolves_to_a_modules_main() -> None:
    scripts = b"""\
[project.scripts]
good = "my_repo.cli:main"
pkg = "my_repo.sub:main"
"""
    good = {
        "pyproject.toml": GOOD_PYPROJECT + scripts,
        "src/my_repo/cli.py": b"def main() -> int:\n    return 0\n",
        "src/my_repo/sub/__init__.py": b"from my_repo.cli import main\n",
    }
    assert found(entry_points_resolve_to_main, good) == []
    bad_scripts = b"""\
[project.scripts]
no-main = "my_repo.cli:main"
outside = "other.cli:main"
not-main = "my_repo.cli:run"
"""
    bad = {
        "pyproject.toml": GOOD_PYPROJECT + bad_scripts,
        "src/my_repo/cli.py": b"def run() -> int:\n    return 0\n",
    }
    assert found(entry_points_resolve_to_main, bad) == [
        ("pyproject.toml", None),
        ("pyproject.toml", None),
        ("pyproject.toml", None),
    ]


def test_executable_scripts_carry_the_uv_shebang_and_inline_metadata() -> None:
    good = (
        b"#!/usr/bin/env -S uv run --script\n"
        b'# /// script\n# requires-python = ">=3.14"\n# ///\n'
    )
    contents = {
        ".python-version": b"3.14\n",
        "scripts/good": good,
        "scripts/lib.py": b"x = 1\n",
        "scripts/old": b"#!/usr/bin/env python3\n",
        "scripts/floor": good.replace(b">=3.14", b">=3.13"),
    }
    executable = ("scripts/good", "scripts/old", "scripts/floor")
    assert found(carry_the_uv_shebang, contents, executable) == [
        ("scripts/floor", None),
        ("scripts/old", 1),
        ("scripts/old", None),
    ]
