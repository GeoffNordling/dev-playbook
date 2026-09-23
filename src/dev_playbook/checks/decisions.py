"""The decisions family: the rules of ``standards/decisions/``.

Six rules are decided by functions over the model, all over the records
under a repo's ``docs/decisions/``: the directory's contents, the record
numbering, the frontmatter keys and H1, the date, the status vocabulary,
and the record a supersession names.
"""

import datetime
import re
from collections import Counter
from collections.abc import Iterator
from pathlib import PurePosixPath

from dev_playbook.check_registry import Finding, check
from dev_playbook.model import Repo

DECISIONS_DIR = "docs/decisions"
DIRECTORY_FILES = ("README.md", "index.md")

# A record file: a numeric prefix, a hyphen, a slug, then ``.md``.
RECORD_NAME = re.compile(r"^(\d+)-.+\.md$")

FIXED_STATUSES = frozenset({"proposed", "accepted", "deprecated"})
SUPERSEDED = re.compile(r"^superseded by (\d{4})$")
VOCABULARY = "proposed | accepted | deprecated | superseded by NNNN"
RECORD_TYPE = "Decision-Record"
REQUIRED_KEYS = ("title", "description", "date")


def _records(repo: Repo) -> list[tuple[str, str]]:
    """Each record path under ``docs/decisions/`` with its numeric prefix."""
    records: list[tuple[str, str]] = []
    for path in repo.files:
        parts = PurePosixPath(path).parts
        if parts[:2] != ("docs", "decisions"):
            continue
        match = RECORD_NAME.match(parts[-1])
        if match is not None:
            records.append((path, match.group(1)))
    return records


def _frontmatter(repo: Repo, path: str) -> dict[str, object]:
    """The record's parsed frontmatter, empty when it has none."""
    return repo.markdown[path].frontmatter or {}


@check("decisions.numbered-records-index-readme-nothing-else")
def records_index_readme_only(repo: Repo) -> Iterator[Finding]:
    """A ``docs/decisions/`` with a record has only records, ``index.md``, and ``README.md``."""
    prefix = f"{DECISIONS_DIR}/"
    entries = [path for path in repo.files if path.startswith(prefix)]
    top_level = {
        path.removeprefix(prefix)
        for path in entries
        if "/" not in path.removeprefix(prefix)
    }
    if not any(RECORD_NAME.match(name) for name in top_level):
        return
    for name in DIRECTORY_FILES:
        if name not in top_level:
            yield Finding(DECISIONS_DIR, None, f"records directory has no `{name}`")
    for path in entries:
        name = path.removeprefix(prefix)
        if "/" in name:
            yield Finding(path, None, "records directory has no subdirectory")
        elif name not in DIRECTORY_FILES and not RECORD_NAME.match(name):
            yield Finding(
                path,
                None,
                "not a record `<digits>-<slug>.md`, `index.md`, or `README.md`",
            )


def _runs(numbers: list[int]) -> list[tuple[int, int]]:
    """Collapse sorted ints into ``(low, high)`` runs of consecutive values."""
    runs: list[tuple[int, int]] = []
    for number in numbers:
        if runs and number == runs[-1][1] + 1:
            runs[-1] = (runs[-1][0], number)
        else:
            runs.append((number, number))
    return runs


@check("decisions.four-digits-from-0001-no-gaps-or-repeats")
def sequential_numbering(repo: Repo) -> Iterator[Finding]:
    """Record numbers are four digits and run from ``0001`` up by one, each once."""
    records = _records(repo)
    counts = Counter(int(prefix) for _, prefix in records)
    for path, prefix in records:
        number = int(prefix)
        if number < 1:
            yield Finding(
                path,
                None,
                f"record number {number:04d} is below the sequence start 0001",
            )
        if len(prefix) != 4:
            yield Finding(
                path,
                None,
                f"record number '{prefix}' is not zero-padded to four digits",
            )
        if counts[number] > 1:
            yield Finding(path, None, f"record number {number:04d} is duplicated")
    present = set(counts)
    missing = sorted(set(range(1, max(present) + 1)) - present) if present else []
    for low, high in _runs(missing):
        if low == high:
            message = f"record number {low:04d} is missing from the sequence"
        else:
            message = (
                f"record numbers {low:04d} through {high:04d} "
                "are missing from the sequence"
            )
        yield Finding(DECISIONS_DIR, None, message)


@check("decisions.four-frontmatter-keys-title-repeated-as-h1")
def frontmatter_keys_and_h1(repo: Repo) -> Iterator[Finding]:
    """A record has ``type: Decision-Record``, ``title``, ``description``, ``date``, and ``# <title>`` first."""
    for path, _ in _records(repo):
        front = _frontmatter(repo, path)
        if front.get("type") != RECORD_TYPE:
            yield Finding(path, 1, f"frontmatter `type` is not `{RECORD_TYPE}`")
        for key in REQUIRED_KEYS:
            if key not in front:
                yield Finding(path, 1, f"frontmatter has no `{key}`")
        title = front.get("title")
        if not isinstance(title, str):
            continue
        first = next(
            ((n, text) for n, text in repo.markdown[path].content if text.strip()),
            None,
        )
        if first is None:
            yield Finding(path, None, f"body does not open with `# {title}`")
        elif first[1] != f"# {title}":
            yield Finding(path, first[0], f"first body line is not `# {title}`")


@check("decisions.yyyy-mm-dd-date-or-null")
def date_or_null(repo: Repo) -> Iterator[Finding]:
    """A record's ``date`` is a ``YYYY-MM-DD`` date or ``null``."""
    for path, _ in _records(repo):
        front = _frontmatter(repo, path)
        if "date" not in front:
            continue
        date = front["date"]
        if date is None:
            continue
        if isinstance(date, datetime.date) and not isinstance(date, datetime.datetime):
            continue
        yield Finding(path, 1, f"date {date!r} is not a YYYY-MM-DD date or null")


@check("decisions.proposed-accepted-deprecated-superseded-or-absent")
def status_vocabulary(repo: Repo) -> Iterator[Finding]:
    """A record's ``status``, if it has one, is in the status vocabulary."""
    for path, _ in _records(repo):
        front = _frontmatter(repo, path)
        if "status" not in front:
            continue
        status = front["status"]
        if isinstance(status, str) and (
            status in FIXED_STATUSES or SUPERSEDED.fullmatch(status) is not None
        ):
            continue
        yield Finding(path, 1, f"status {status!r} is not one of {VOCABULARY}")


@check("decisions.superseded-by-a-record-that-exists")
def superseded_by_existing(repo: Repo) -> Iterator[Finding]:
    """A ``superseded by NNNN`` status names a record ``docs/decisions/NNNN-*.md``."""
    numbers = {
        prefix
        for path, prefix in _records(repo)
        if PurePosixPath(path).parent == PurePosixPath(DECISIONS_DIR)
    }
    for path, _ in _records(repo):
        status = _frontmatter(repo, path).get("status")
        if not isinstance(status, str):
            continue
        match = SUPERSEDED.fullmatch(status)
        if match is not None and match.group(1) not in numbers:
            yield Finding(
                path,
                1,
                f"superseded by {match.group(1)}, but no record {match.group(1)} exists",
            )
