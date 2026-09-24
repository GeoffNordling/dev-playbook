"""Unit tests for the shell family's checks."""

from pathlib import Path

from dev_playbook.checks.shell import (
    bash_declared,
    no_shebang_no_strict_mode,
    strict_mode_first,
)
from dev_playbook.model import Repo

STRICT = b"#!/usr/bin/env bash\n# Says hello.\n\nset -euo pipefail\necho hi\n"


def test_bash_declared() -> None:
    repo = Repo.from_files(
        Path("/r"),
        {
            "a.sh": b"#!/bin/bash\necho a\n",
            "b.sh": b"# A fragment.\n\n# shellcheck shell=bash\nalias b=ls\n",
            "c.sh": b"#!/bin/sh\necho c\n",
            "d.sh": b"alias d=ls\n# shellcheck shell=bash\n",
            "hooks/run": b"#!/usr/bin/env sh\necho run\n",
            "hooks/tool": b"#!/usr/bin/env python3\nprint(1)\n",
            "notes.txt": b"#!/bin/sh\n",
        },
        executable=["hooks/run", "hooks/tool"],
    )
    assert [(f.path, f.line) for f in bash_declared(repo)] == [
        ("c.sh", 1),
        ("d.sh", 1),
        ("hooks/run", 1),
    ]


def test_strict_mode_first() -> None:
    repo = Repo.from_files(
        Path("/r"),
        {
            "good.sh": STRICT,
            "shebang.sh": b"#!/bin/bash\nset -euo pipefail\n",
            "late.sh": b"#!/usr/bin/env bash\necho hi\nset -euo pipefail\n",
            "empty.sh": b"#!/usr/bin/env bash\n# Nothing.\n",
            "sourced.sh": b"alias x=ls\n",
        },
        executable=["good.sh", "shebang.sh", "late.sh", "empty.sh"],
    )
    assert [(f.path, f.line) for f in strict_mode_first(repo)] == [
        ("empty.sh", None),
        ("late.sh", 2),
        ("shebang.sh", 1),
    ]


def test_no_shebang_no_strict_mode() -> None:
    repo = Repo.from_files(
        Path("/r"),
        {
            "dotfiles/.bashrc.d/good.sh": b"# shellcheck shell=bash\nalias g=ls\n",
            "dotfiles/.bashrc.d/bad.sh": b"#!/usr/bin/env bash\n  set -euo pipefail\n",
            "scripts/run.sh": STRICT,
        },
    )
    assert [(f.path, f.line) for f in no_shebang_no_strict_mode(repo)] == [
        ("dotfiles/.bashrc.d/bad.sh", 1),
        ("dotfiles/.bashrc.d/bad.sh", 2),
    ]
