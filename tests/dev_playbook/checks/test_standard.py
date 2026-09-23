"""Unit tests for the standard family's checks."""

from collections.abc import Callable, Iterator
from pathlib import Path

from dev_playbook.check_registry import Finding
from dev_playbook.checks.standard import (
    every_subdirectory_a_standard_directory,
    no_shadowing,
    offered_by_the_canonical_template,
    opens_with_the_governing_sentence,
    the_catalog_lists_every_directory,
)
from dev_playbook.model import Repo

CANONICAL = "standards/build/canonical/.pre-commit-config.yaml"
STANDARD = b"---\ntype: Standard\npopulation: x\n---\n# A\n"


def found(
    check: Callable[[Repo], Iterator[Finding]], contents: dict[str, bytes]
) -> list[tuple[str, int | None]]:
    repo = Repo.from_files(Path("/r"), contents)
    return [(f.path, f.line) for f in check(repo)]


def index(name: str, sentence: str) -> bytes:
    return f"# standards/{name}/ — index\n\n{sentence}\nmore.\n".encode()


def test_every_subdirectory_a_standard_directory() -> None:
    assert found(
        every_subdirectory_a_standard_directory,
        {
            "standards/README.md": b"# R\n",
            "standards/index.md": b"# I\n",
            "standards/stray.md": b"# S\n",
            "standards/good/index.md": b"# I\n",
            "standards/good/deep/rule.md": STANDARD,
            "standards/mixed/rule.md": STANDARD,
            "standards/mixed/notes.md": b"---\ntype: Guide\n---\n# N\n",
            "standards/empty/index.md": b"# I\n",
            "standards/empty/data.yaml": b"a: 1\n",
        },
    ) == [
        ("standards/mixed/notes.md", None),
        ("standards/stray.md", None),
        ("standards/empty", None),
    ]


def test_directory_index_opens_with_the_governing_sentence() -> None:
    assert found(
        opens_with_the_governing_sentence,
        {
            "standards/good/index.md": index(
                "good", "Good governs how things\nare done — rules, tables."
            ),
            "standards/bad/index.md": index("bad", "Bad covers some things."),
            "standards/bare/index.md": b"# Bare\n",
            "standards/bare/rule.md": STANDARD,
            "standards/good/deep/index.md": index("deep", "Nothing here."),
        },
    ) == [("standards/bad/index.md", 3), ("standards/bare/index.md", None)]


GOOD_OPENING = "Alpha governs a — b"
CATALOG_HEAD = "# standards/ — index\n\n- [Standards](/standards/README.md) — R\n"
ALPHA = f"- [alpha/](/standards/alpha/index.md) — {GOOD_OPENING}\n"
BUILD = "- [build/](/standards/build/index.md) — Build governs b — c\n"
META = "- [standard/](/standards/standard/index.md) — Meta governs x — y\n"


def catalog_repo(entries: str, canonical: bool) -> dict[str, bytes]:
    files = {
        "standards/README.md": b"# R\n",
        "standards/index.md": (CATALOG_HEAD + entries).encode(),
        "standards/alpha/index.md": index("alpha", GOOD_OPENING + "."),
        "standards/build/index.md": index("build", "Build governs b — c."),
        "standards/standard/index.md": index("standard", "Meta governs x — y."),
    }
    if canonical:
        files[CANONICAL] = b"repos: []\n"
    return files


def test_the_catalog_lists_every_directory() -> None:
    check = the_catalog_lists_every_directory
    assert found(check, catalog_repo(META + ALPHA + BUILD, canonical=True)) == []
    assert found(check, catalog_repo(ALPHA + BUILD + META, canonical=False)) == []
    assert found(check, catalog_repo(ALPHA + BUILD + META, canonical=True)) == [
        ("standards/index.md", 4)
    ]
    assert found(
        check,
        catalog_repo(
            META + "- [x](/guides/x.md) — X\n" + ALPHA.replace(" — b", " — c") + BUILD,
            canonical=True,
        ),
    ) == [("standards/index.md", 5), ("standards/index.md", 6)]
    assert found(check, catalog_repo(META + BUILD, canonical=True)) == [
        ("standards/index.md", None)
    ]
    assert found(check, {"standards/a/rule.md": STANDARD}) == [
        ("standards/index.md", None)
    ]
    assert found(check, {"README.md": b"# R\n"}) == []


def test_no_shadowing() -> None:
    consumer = {"standards/build/rule.md": STANDARD, "standards/mine/rule.md": STANDARD}
    assert found(no_shadowing, consumer) == [("standards/build", None)]
    assert found(no_shadowing, consumer | {CANONICAL: b"repos: []\n"}) == []


OFFERING = b"""\
repos:
  - repo: https://github.com/GeoffNordling/dev-playbook
    rev: x
    hooks:
      - id: playbook-check
      - id: extra
  - repo: local
    hooks:
      - id: other
"""
MANIFEST = b"- id: playbook-check\n- id: other\n"


def test_offered_by_the_canonical_template() -> None:
    check = offered_by_the_canonical_template
    assert found(check, {".pre-commit-hooks.yaml": MANIFEST}) == []
    repo = Repo.from_files(
        Path("/r"), {CANONICAL: OFFERING, ".pre-commit-hooks.yaml": MANIFEST}
    )
    assert [f.message for f in check(repo)] == [
        "published hook other is not in the dev-playbook block",
        "dev-playbook block hook extra is not published in .pre-commit-hooks.yaml",
    ]
    assert found(check, {CANONICAL: b"repos: [\n"}) == [(CANONICAL, None)]
