"""Unit tests for the testing family's checks."""

from pathlib import Path

from dev_playbook.checks.testing import carries_test_prefix, mirrors_source_tree
from dev_playbook.model import Repo


def test_test_files_carry_the_test_prefix() -> None:
    repo = Repo.from_files(
        Path("/r"),
        {
            "tests/test_good.py": b"def test_one() -> None:\n    pass\n",
            "tests/helpers.py": b"def make() -> None:\n    pass\n",
            "tests/check_login.py": b"import os\n\n\ndef test_login() -> None:\n    pass\n",
            "tests/cases.py": b"class TestCases:\n    pass\n",
        },
    )
    assert [(f.path, f.line) for f in carries_test_prefix(repo)] == [
        ("tests/cases.py", 1),
        ("tests/check_login.py", 4),
    ]


def test_test_tree_mirrors_the_source_tree() -> None:
    repo = Repo.from_files(
        Path("/r"),
        {
            "src/auth/login.py": b"",
            "src/auth/__init__.py": b"",
            "tests/auth/test_login.py": b"",
            "tests/unit/auth/test_login.py": b"",
            "tests/test_login.py": b"",
            "tests/test_init.py": b"",
            "tests/e2e/test_flow.py": b"",
        },
    )
    assert [(f.path, f.line) for f in mirrors_source_tree(repo)] == [
        ("tests/test_login.py", None),
    ]
