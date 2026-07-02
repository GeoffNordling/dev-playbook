"""Behavioral tests for tools/bin/python-lint.

python-lint merges the former no-future-annotations, empty-init, and
test-privacy hooks into one walk. Discovery goes through `git ls-files`, so
every fixture is a git repo; a directory (repo root) is the only argument.
"""

import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "bin" / "python-lint"


def run(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", str(SCRIPT), str(repo)],
        capture_output=True,
        text=True,
    )


def make_repo(tmp_path: Path, files: dict[str, str]) -> Path:
    repo = tmp_path / "repo"
    for rel, content in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    return repo


# --- no-future-annotations rule ---


def test_clean_repo_exits_zero(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"ok.py": "x: int | None = None\n"})
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""


def test_flags_future_annotations(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path, {"bad.py": "from __future__ import annotations\nx = 1\n"}
    )
    result = run(repo)
    assert result.returncode == 1
    assert "bad.py" in result.stdout
    assert "no-future-annotations" in result.stdout


def test_flags_extensionless_python_shebang(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {"mytool": "#!/usr/bin/env python3\nfrom __future__ import annotations\n"},
    )
    result = run(repo)
    assert result.returncode == 1
    assert "mytool" in result.stdout


def test_ignores_non_python_extensionless_files(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"notes": "from __future__ import annotations\n"})
    result = run(repo)
    assert result.returncode == 0


def test_ignores_string_literals(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"s.py": 'x = "from __future__ import annotations"\n'})
    result = run(repo)
    assert result.returncode == 0


def test_other_future_imports_allowed(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"d.py": "from __future__ import division\n"})
    result = run(repo)
    assert result.returncode == 0


def test_skips_excluded_dirs_by_name(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path, {".venv/lib/bad.py": "from __future__ import annotations\n"}
    )
    result = run(repo)
    assert result.returncode == 0


def test_honors_gitignore(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            ".gitignore": "ignored/\n",
            "ignored/bad.py": "from __future__ import annotations\n",
        },
    )
    result = run(repo)
    assert result.returncode == 0


# --- empty-init rule ---


def test_blank_init_passes(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"pkg/__init__.py": ""})
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_nonblank_init_fails_and_names_offender(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"pkg/__init__.py": '"""A docstring."""\n'})
    result = run(repo)
    assert result.returncode == 1
    assert "pkg/__init__.py" in result.stdout
    assert "empty-init" in result.stdout


def test_whitespace_only_init_passes(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"pkg/__init__.py": "\n  \n\t\n"})
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_unreadable_init_reports_tool_error(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    bad = repo / "pkg" / "__init__.py"
    bad.parent.mkdir(parents=True)
    bad.write_bytes(b"\xff\xfe not valid utf-8")
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    result = run(repo)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "python-lint" in result.stderr


# --- test-privacy rule ---


def test_import_of_private_name_from_non_test_module_is_flagged(
    tmp_path: Path,
) -> None:
    repo = make_repo(
        tmp_path,
        {
            "mypkg/thing.py": "def _secret():\n    return 1\n",
            "tests/test_thing.py": "from mypkg.thing import _secret\n",
        },
    )
    result = run(repo)
    assert result.returncode == 1
    assert "privacy.import-private" in result.stdout
    assert "tests/test_thing.py" in result.stdout


def test_attribute_access_into_private_name_is_flagged(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "mypkg/thing.py": "def _secret():\n    return 1\n",
            "tests/test_thing.py": "import mypkg.thing\n\n\ndef test_it():\n    mypkg.thing._secret()\n",
        },
    )
    result = run(repo)
    assert result.returncode == 1
    assert "privacy.attribute-access" in result.stdout


def test_dunder_access_is_public(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "mypkg/thing.py": "class T:\n    pass\n",
            "tests/test_thing.py": "import mypkg.thing\n\n\ndef test_it():\n    mypkg.thing.__name__\n",
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_public_access_in_test_is_clean(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "mypkg/thing.py": "def public():\n    return 1\n",
            "tests/test_thing.py": "from mypkg.thing import public\n\n\ndef test_it():\n    assert public() == 1\n",
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


# --- combined ---


def test_multiple_rules_report_together(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "pkg/__init__.py": '"""nope."""\n',
            "bad.py": "from __future__ import annotations\n",
        },
    )
    result = run(repo)
    assert result.returncode == 1
    assert "empty-init" in result.stdout
    assert "no-future-annotations" in result.stdout


# --- per-rule directory scope (restores each retired hook's original coverage) ---


def test_empty_init_polices_deprecated_tree(tmp_path: Path) -> None:
    """empty-init has no directory exclusions — a non-empty __init__.py under
    deprecated/ is still an offender, as the retired empty-init hook enforced."""
    repo = make_repo(tmp_path, {"deprecated/pkg/__init__.py": '"""nope."""\n'})
    result = run(repo)
    assert result.returncode == 1
    assert "deprecated/pkg/__init__.py" in result.stdout
    assert "empty-init" in result.stdout


def test_future_rule_skips_deprecated_tree(tmp_path: Path) -> None:
    """no-future-annotations keeps its original exclusions — deprecated/ (and
    build/dist/.agents/.dhub) are not scanned for the banned import."""
    repo = make_repo(
        tmp_path,
        {"deprecated/old.py": "from __future__ import annotations\n"},
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_privacy_rule_scans_deprecated_tree(tmp_path: Path) -> None:
    """test-privacy's original exclusions were caches only — a private-access
    violation under deprecated/ is still flagged."""
    repo = make_repo(
        tmp_path,
        {
            "deprecated/thing.py": "def _secret():\n    return 1\n",
            "deprecated/tests/test_thing.py": "from deprecated.thing import _secret\n",
        },
    )
    result = run(repo)
    assert result.returncode == 1
    assert "privacy.import-private" in result.stdout
    assert "deprecated/tests/test_thing.py" in result.stdout


def test_repo_self_scan_is_clean() -> None:
    """The dev-playbook repo itself passes all three rules."""
    repo = Path(__file__).resolve().parents[2]
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr
