"""Behavioral tests for scripts/testing-lint.

testing-lint walks a repo's Python files once and applies one rule to the
test files it finds: mirror-layout (test placement).
Discovery goes through `git ls-files`, so every fixture is a git repo; a
directory (repo root) is the only positional argument.
"""

import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "testing-lint"


def run(repo: Path) -> subprocess.CompletedProcess:
    """Run testing-lint against repo and capture its output."""
    return subprocess.run(
        ["python3", str(SCRIPT), str(repo)],
        capture_output=True,
        text=True,
    )


def make_repo(tmp_path: Path, files: dict[str, str]) -> Path:
    """Write files into a fresh git repo and return its root."""
    repo = tmp_path / "repo"
    for rel, content in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    return repo


# --- mirror-layout rule ---


def test_test_file_off_its_module_mirror_is_flagged(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "src/pkg/thing.py": "def public():\n    return 1\n",
            "tests/test_thing.py": "def test_it():\n    pass\n",
        },
    )
    result = run(repo)
    assert result.returncode == 1
    assert "testing.mirror-source-structure" in result.stdout
    assert "tests/test_thing.py" in result.stdout
    assert "tests/pkg/test_thing.py" in result.stdout


def test_test_file_at_its_module_mirror_is_clean(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "src/pkg/thing.py": "def public():\n    return 1\n",
            "tests/pkg/test_thing.py": "def test_it():\n    pass\n",
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_test_file_at_a_scoped_mirror_is_clean(tmp_path: Path) -> None:
    """``unit`` and ``integration`` are recognized scope directories; the mirror
    beneath each is an accepted location."""
    repo = make_repo(
        tmp_path,
        {
            "src/pkg/thing.py": "def public():\n    return 1\n",
            "src/pkg/other.py": "def public():\n    return 1\n",
            "tests/unit/pkg/test_thing.py": "def test_it():\n    pass\n",
            "tests/integration/pkg/test_other.py": "def test_it():\n    pass\n",
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_test_file_under_an_unrecognized_scope_directory_is_flagged(
    tmp_path: Path,
) -> None:
    """The scope set is fixed; any other directory in that position is a
    misplacement, not a scope."""
    repo = make_repo(
        tmp_path,
        {
            "src/pkg/thing.py": "def public():\n    return 1\n",
            "tests/helpers/pkg/test_thing.py": "def test_it():\n    pass\n",
        },
    )
    result = run(repo)
    assert result.returncode == 1
    assert "testing.mirror-source-structure" in result.stdout
    assert "tests/helpers/pkg/test_thing.py" in result.stdout


def test_test_file_matching_no_module_is_outside_the_rule(tmp_path: Path) -> None:
    """A flattened name whose stem names no src module is not policed."""
    repo = make_repo(
        tmp_path,
        {
            "src/pkg/render.py": "def public():\n    return 1\n",
            "tests/test_pkg_render_edgecases.py": "def test_it():\n    pass\n",
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_conftest_is_outside_the_rule(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "src/pkg/conftest.py": "x = 1\n",
            "tests/conftest.py": "import pytest\n",
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_test_file_outside_the_top_level_tests_tree_is_outside_the_rule(
    tmp_path: Path,
) -> None:
    """A nested scaffold's test tree is not matched against the repo's src/."""
    repo = make_repo(
        tmp_path,
        {
            "src/pkg/cli.py": "def public():\n    return 1\n",
            "templates/scaffold/tests/test_cli.py": "def test_it():\n    pass\n",
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_mirror_finding_is_file_level_without_a_line(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "src/pkg/thing.py": "def public():\n    return 1\n",
            "tests/test_thing.py": "def test_it():\n    pass\n",
        },
    )
    result = run(repo)
    assert "tests/test_thing.py: testing.mirror-source-structure " in result.stdout


# --- rule ids and finding format ---


def test_list_rules_prints_card_prefixed_ids_from_any_cwd(tmp_path: Path) -> None:
    """--list-rules names every rule, card-prefixed, needing no repository."""
    result = subprocess.run(
        ["python3", str(SCRIPT), "--list-rules"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.split() == ["testing.mirror-source-structure"]
