"""Load pytest-sdd configuration from pyproject.toml.

Configuration lives in [tool.pytest-sdd]:

    [tool.pytest-sdd]
    spec_dirs = ["specs/functional_requirements", "specs/design"]
    oft_jar = "../dev-playbook/sdd-tools/lib/openfasttrace-4.2.2.jar"

All fields are required when the section is present. Returns None if the
section is absent (plugin disabled for this project).
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path

import pytest


@dataclass
class SddConfig:
    """Resolved pytest-sdd configuration for a project."""

    spec_dirs: list[Path]
    oft_jar: Path


def load_config(config: pytest.Config) -> "SddConfig | None":
    """Read [tool.pytest-sdd] from pyproject.toml at the project root.

    Returns None if the section is absent (plugin is disabled).
    Raises ValueError if the section is present but fields are missing or
    point to non-existent paths.
    """
    rootdir = Path(config.rootpath)
    return load_config_from_root(rootdir)


def load_config_from_root(root: Path) -> "SddConfig | None":
    """Load config given an explicit root directory (testable without pytest)."""
    pyproject = root / "pyproject.toml"
    if not pyproject.is_file():
        return None

    with open(pyproject, "rb") as f:
        data = tomllib.load(f)

    section = data.get("tool", {}).get("pytest-sdd")
    if section is None:
        return None

    # spec_dirs — required
    raw_dirs = section.get("spec_dirs")
    if not raw_dirs:
        raise ValueError("[tool.pytest-sdd] missing required field 'spec_dirs'")
    if isinstance(raw_dirs, str):
        raw_dirs = [raw_dirs]
    spec_dirs = [root / d for d in raw_dirs]

    # oft_jar — required
    raw_jar = section.get("oft_jar")
    if not raw_jar:
        raise ValueError("[tool.pytest-sdd] missing required field 'oft_jar'")
    oft_jar = root / raw_jar

    return SddConfig(spec_dirs=spec_dirs, oft_jar=oft_jar)
