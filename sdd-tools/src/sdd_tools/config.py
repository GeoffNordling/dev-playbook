"""Read [tool.pytest-sdd] from pyproject.toml.

Used by the pytest plugin (rootdir = pytest's rootpath) and by per-view CLIs
(rootdir = nearest ancestor containing pyproject.toml).

Keys:
    spec_dirs : list[str]   relative to project root
    oft_jar   : str         relative to project root
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SddConfig:
    """Resolved sdd-tools configuration for a project."""

    spec_dirs: list[Path]
    oft_jar: Path


def load_config_from_root(root: Path) -> SddConfig | None:
    """Load config given an explicit project root directory.

    Returns None if pyproject.toml has no [tool.pytest-sdd] section.
    Raises ValueError when the section is present but malformed.
    """
    pyproject = root / "pyproject.toml"
    if not pyproject.is_file():
        return None

    with open(pyproject, "rb") as f:
        data = tomllib.load(f)

    section = data.get("tool", {}).get("pytest-sdd")
    if section is None:
        return None

    raw_dirs = section.get("spec_dirs")
    if not raw_dirs:
        raise ValueError("[tool.pytest-sdd] missing required field 'spec_dirs'")
    if isinstance(raw_dirs, str):
        raw_dirs = [raw_dirs]
    spec_dirs = [root / d for d in raw_dirs]

    raw_jar = section.get("oft_jar")
    if not raw_jar:
        raise ValueError("[tool.pytest-sdd] missing required field 'oft_jar'")
    oft_jar = root / raw_jar

    return SddConfig(spec_dirs=spec_dirs, oft_jar=oft_jar)


def find_project_root(start: Path | None = None) -> Path:
    """Walk up from start (default cwd) to find a directory with pyproject.toml."""
    cwd = start or Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / "pyproject.toml").is_file():
            return parent
    return cwd
