"""Smoke tests that exercise spec-tools against its own specs collection.

Adds real-world coverage that synthetic tmp_path fixtures cannot. As the
public surface grows (parse, render, ...), this file grows alongside it.
"""

import pathlib

import pytest

from spec_tools.discover import find

SPEC_TOOLS_ROOT = pathlib.Path(__file__).resolve().parent.parent


@pytest.mark.covers("dsn~discover.find~0")
def test_find_enumerates_spec_tools_own_specs():
    result = find(SPEC_TOOLS_ROOT)

    assert result, "expected spec-tools to ship at least one spec file"
    for path in result:
        assert path.is_relative_to(SPEC_TOOLS_ROOT / "specs")
        assert path.suffix == ".md"
        assert path.name != "index.md"

    assert SPEC_TOOLS_ROOT / "specs" / "design" / "discover.md" in result
    assert (
        SPEC_TOOLS_ROOT / "specs" / "functional_requirements" / "discover.md" in result
    )
