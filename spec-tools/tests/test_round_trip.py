"""Round-trip closure tests for `req~model.round-trip~0`.

Covers both directions of the round-trip contract:

- model -> text -> model identity (a SpecItem serialized then parsed
  equals the original).
- text -> model -> text byte-equality on canonically-formatted input
  (parsing then re-serializing reproduces the source bytes exactly).
"""

import pathlib

import pytest

from spec_tools.deserialize import parse
from spec_tools.model import ItemId, SpecItem
from spec_tools.serialize import render, write

GOOD_FIXTURES_DIR = pathlib.Path(__file__).parent / "fixtures" / "good"


@pytest.mark.covers("req~model.round-trip~0")
def test_round_trip_fully_loaded_spec_item(tmp_path: pathlib.Path) -> None:
    original = SpecItem(
        heading="Fully Loaded Item",
        id=ItemId("dsn", "fully.loaded", 3),
        description="Line one of description.\nLine two of description.",
        rationale="Why we did this.\nAcross two lines.",
        comment="A side note.",
        covers=[ItemId("req", "alpha", 0), ItemId("req", "beta", 1)],
        depends=[ItemId("dsn", "gamma", 2)],
        needs=["utest", "itest"],
        tags=["alpha", "beta"],
        interface=["mod.f() -> None", "mod.g(x: int) -> int"],
        agent_review=["check 1", "check 2"],
    )
    spec_path = tmp_path / "fully_loaded.md"
    write([original], spec_path)

    [parsed] = parse(spec_path)

    assert parsed == original


@pytest.mark.covers("req~model.round-trip~0")
def test_round_trip_minimal_spec_item(tmp_path: pathlib.Path) -> None:
    original = SpecItem(
        heading="Minimal Item",
        id=ItemId("dsn", "minimal", 0),
        description="Just a description.",
        rationale=None,
        comment=None,
        covers=[],
        depends=[],
        needs=[],
        tags=[],
        interface=[],
        agent_review=[],
    )
    spec_path = tmp_path / "minimal.md"
    write([original], spec_path)

    [parsed] = parse(spec_path)

    assert parsed == original


@pytest.mark.covers("req~model.round-trip~0")
@pytest.mark.parametrize(
    "fixture_path",
    sorted(GOOD_FIXTURES_DIR.glob("*.md")),
    ids=lambda p: p.name,
)
def test_round_trip_text_byte_equality_on_good_fixtures(
    fixture_path: pathlib.Path,
) -> None:
    original_text = fixture_path.read_text()

    parsed = parse(fixture_path)
    rendered_text = render(parsed)

    assert rendered_text == original_text
