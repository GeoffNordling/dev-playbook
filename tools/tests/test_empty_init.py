"""Behavioral tests for tools/bin/empty-init."""

import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "bin" / "empty-init"


def run(*args: str) -> subprocess.CompletedProcess:
    """Invoke the empty-init script with args; capture its output."""
    return subprocess.run(
        ["python3", str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


def make_git_repo(root: Path, files: dict[str, str], track: bool = True) -> None:
    """Init a git repo at root, write files, and (by default) stage them."""
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    for relpath, contents in files.items():
        path = root / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents)
    if track:
        subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)


def test_blank_tracked_init_passes(tmp_path: Path) -> None:
    make_git_repo(tmp_path, {"pkg/__init__.py": ""})

    result = run(str(tmp_path))

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""


def test_nonblank_tracked_init_fails_and_names_offender(tmp_path: Path) -> None:
    make_git_repo(tmp_path, {"pkg/__init__.py": '"""A docstring."""\n'})

    result = run(str(tmp_path))

    assert result.returncode == 1
    assert "pkg/__init__.py" in result.stdout
    assert "empty-init" in result.stdout


def test_untracked_init_is_not_scanned(tmp_path: Path) -> None:
    make_git_repo(tmp_path, {"pkg/__init__.py": '"""Untracked junk."""\n'}, track=False)

    result = run(str(tmp_path))

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""


def test_whitespace_only_init_passes(tmp_path: Path) -> None:
    make_git_repo(tmp_path, {"pkg/__init__.py": "\n  \n\t\n"})

    result = run(str(tmp_path))

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""


def test_repo_self_scan_is_clean() -> None:
    """Every tracked __init__.py in dev-playbook itself is empty."""
    repo = Path(__file__).resolve().parents[2]
    result = run(str(repo))
    assert result.returncode == 0, result.stdout + result.stderr


def test_gitignored_venv_init_is_not_scanned(tmp_path: Path) -> None:
    make_git_repo(
        tmp_path,
        {
            ".gitignore": ".venv/\n",
            ".venv/lib/pkg/__init__.py": '"""Third-party docstring."""\n',
        },
    )

    result = run(str(tmp_path))

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""
