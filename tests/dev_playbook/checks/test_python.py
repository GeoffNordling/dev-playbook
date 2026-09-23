"""Unit tests for the python family's checks."""

from pathlib import Path

from dev_playbook.checks.python import empty_init, no_future_annotations
from dev_playbook.model import Repo


def test_empty_init() -> None:
    repo = Repo.from_files(
        Path("/r"),
        {
            "pkg/__init__.py": b"\n  \n",
            "bad/__init__.py": b'"""A docstring."""\n',
            "pkg/mod.py": b'"""Not an init."""\n',
        },
    )
    assert [(f.path, f.line) for f in empty_init(repo)] == [("bad/__init__.py", 1)]


def test_no_future_annotations() -> None:
    repo = Repo.from_files(
        Path("/r"),
        {
            "good.py": b"from __future__ import division\n",
            "build/bad.py": b'"""Doc."""\n\nfrom __future__ import annotations\n',
            "scripts/tool": (
                b"#!/usr/bin/env python3\nfrom __future__ import annotations\n"
            ),
        },
    )
    assert [(f.path, f.line) for f in no_future_annotations(repo)] == [
        ("build/bad.py", 3),
        ("scripts/tool", 2),
    ]
