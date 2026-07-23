from collections.abc import Callable
from pathlib import Path

from conftest import init_repo

from dev_playbook import pyast


def test_ambient_git_dir_does_not_redirect_find_python_files(
    tmp_path: Path, ambient_git_dir: Callable[[str], Path]
) -> None:
    target = tmp_path / "target"
    init_repo(target)
    (target / "real.py").write_text("x = 1\n")
    (target / ".gitignore").write_text("leaked.py\n")
    (target / "leaked.py").write_text("y = 2\n")
    ambient_git_dir("leaked.py")

    assert pyast.find_python_files(target) == [target / "real.py"]
