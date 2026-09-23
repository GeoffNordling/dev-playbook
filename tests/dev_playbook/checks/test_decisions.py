"""Unit tests for the decisions family's checks."""

from pathlib import Path

from dev_playbook.checks.decisions import (
    date_or_null,
    frontmatter_keys_and_h1,
    records_index_readme_only,
    sequential_numbering,
    status_vocabulary,
    superseded_by_existing,
)
from dev_playbook.model import Repo


def _record(title: str = "T", extra: str = "", date: str = "2026-09-22") -> bytes:
    return (
        f"---\ntype: Decision-Record\ntitle: {title}\ndescription: d\n"
        f"date: {date}\n{extra}---\n\n# {title}\n"
    ).encode()


def test_numbered_records_index_readme_nothing_else() -> None:
    repo = Repo.from_files(
        Path("/r"),
        {
            "docs/decisions/0001-a.md": _record(),
            "docs/decisions/index.md": b"",
            "docs/decisions/notes.txt": b"",
            "docs/decisions/old/0002-b.md": _record(),
            "other/decisions/stray.md": b"",
        },
    )
    assert [(f.path, f.line) for f in records_index_readme_only(repo)] == [
        ("docs/decisions", None),
        ("docs/decisions/notes.txt", None),
        ("docs/decisions/old/0002-b.md", None),
    ]


def test_four_digits_from_0001_no_gaps_or_repeats() -> None:
    repo = Repo.from_files(
        Path("/r"),
        {
            "docs/decisions/0001-a.md": _record(),
            "docs/decisions/0001-b.md": _record(),
            "docs/decisions/05-c.md": _record(),
            "docs/decisions/index.md": b"",
        },
    )
    assert [(f.path, f.line) for f in sequential_numbering(repo)] == [
        ("docs/decisions/0001-a.md", None),
        ("docs/decisions/0001-b.md", None),
        ("docs/decisions/05-c.md", None),
        ("docs/decisions", None),
    ]


def test_four_frontmatter_keys_title_repeated_as_h1() -> None:
    repo = Repo.from_files(
        Path("/r"),
        {
            "docs/decisions/0001-good.md": _record(),
            "docs/decisions/0002-no-date.md": (
                b"---\ntype: Decision-Record\ntitle: T\ndescription: d\n---\n\n# T\n"
            ),
            "docs/decisions/0003-wrong-h1.md": _record().replace(b"# T", b"# U"),
        },
    )
    assert [(f.path, f.line) for f in frontmatter_keys_and_h1(repo)] == [
        ("docs/decisions/0002-no-date.md", 1),
        ("docs/decisions/0003-wrong-h1.md", 8),
    ]


def test_yyyy_mm_dd_date_or_null() -> None:
    repo = Repo.from_files(
        Path("/r"),
        {
            "docs/decisions/0001-date.md": _record(),
            "docs/decisions/0002-null.md": _record(date="null"),
            "docs/decisions/0003-string.md": _record(date="'2026-09-22'"),
            "docs/decisions/0004-time.md": _record(date="2026-09-22 10:00:00"),
        },
    )
    assert [(f.path, f.line) for f in date_or_null(repo)] == [
        ("docs/decisions/0003-string.md", 1),
        ("docs/decisions/0004-time.md", 1),
    ]


def test_proposed_accepted_deprecated_superseded_or_absent() -> None:
    repo = Repo.from_files(
        Path("/r"),
        {
            "docs/decisions/0001-none.md": _record(),
            "docs/decisions/0002-ok.md": _record(extra="status: accepted\n"),
            "docs/decisions/0003-super.md": _record(
                extra="status: superseded by 0002\n"
            ),
            "docs/decisions/0004-null.md": _record(extra="status: null\n"),
            "docs/decisions/0005-bad.md": _record(extra="status: done\n"),
        },
    )
    assert [(f.path, f.line) for f in status_vocabulary(repo)] == [
        ("docs/decisions/0004-null.md", 1),
        ("docs/decisions/0005-bad.md", 1),
    ]


def test_superseded_by_a_record_that_exists() -> None:
    repo = Repo.from_files(
        Path("/r"),
        {
            "docs/decisions/0001-a.md": _record(extra="status: superseded by 0002\n"),
            "docs/decisions/0002-b.md": _record(extra="status: superseded by 0009\n"),
        },
    )
    assert [(f.path, f.line) for f in superseded_by_existing(repo)] == [
        ("docs/decisions/0002-b.md", 1),
    ]
