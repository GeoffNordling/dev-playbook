"""Behavioral tests for scripts/decisions-lint.

decisions-lint walks a repo's markdown files once, keeps the ones under
docs/decisions/, and applies two rules to the records it finds:
sequential-numbering (contiguous, zero-padded, no-duplicate NNNN-slug.md files)
and status-vocabulary (a record's optional `status` frontmatter key holds one of
the contract's status words). Discovery goes through `git ls-files`, so every
fixture is a git repo; a directory (repo root) is the only positional argument.
The shim declares pyyaml via PEP 723, so it is invoked the way pre-commit runs
it: `uv run --script`.
"""

import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "decisions-lint"


def run(repo: Path) -> subprocess.CompletedProcess:
    """Run decisions-lint against repo and capture its output."""
    return subprocess.run(
        ["uv", "run", "--script", str(SCRIPT), str(repo)],
        capture_output=True,
        text=True,
    )


def make_repo(tmp_path: Path, files: dict[str, str]) -> Path:
    """Write files into a fresh git repo and return its root."""
    repo = tmp_path / "repo"
    for rel, content in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    return repo


def record(title: str, *, status: str | None = None) -> str:
    """A minimal Decision Record body, optionally carrying a status key."""
    status_line = f"status: {status}\n" if status is not None else ""
    return (
        f"---\ntype: Decision-Record\ntitle: {title}\n"
        f"description: {title}\n{status_line}---\n\n# {title}\n\nWe decided.\n"
    )


# --- sequential-numbering rule ---


def test_contiguous_zero_padded_numbering_is_clean(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "docs/decisions/0001-first.md": record("First"),
            "docs/decisions/0002-second.md": record("Second"),
            "docs/decisions/0003-third.md": record("Third"),
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_gap_in_the_sequence_is_flagged(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "docs/decisions/0001-first.md": record("First"),
            "docs/decisions/0003-third.md": record("Third"),
        },
    )
    result = run(repo)
    assert result.returncode == 1
    assert "decisions.sequential-numbering" in result.stdout
    assert "0002" in result.stdout


def test_single_mis_numbered_record_yields_one_gap_finding(tmp_path: Path) -> None:
    """A lone high-numbered record is one mistake, so it yields one gap signal —
    not one finding per absent integer down to 0001."""
    repo = make_repo(
        tmp_path,
        {"docs/decisions/0050-first.md": record("First")},
    )
    result = run(repo)
    assert result.returncode == 1
    gap_lines = [
        line
        for line in result.stdout.splitlines()
        if "missing from the sequence" in line
    ]
    assert len(gap_lines) == 1, result.stdout


def test_duplicate_number_is_flagged(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "docs/decisions/0001-first.md": record("First"),
            "docs/decisions/0001-again.md": record("Again"),
        },
    )
    result = run(repo)
    assert result.returncode == 1
    assert "decisions.sequential-numbering" in result.stdout
    assert "0001" in result.stdout


def test_zeroth_record_is_flagged(tmp_path: Path) -> None:
    """Records number contiguously from 0001, so a 0000-slug record is off
    the contract even though it clears the padding and gap checks."""
    repo = make_repo(
        tmp_path,
        {"docs/decisions/0000-zero.md": record("Zero")},
    )
    result = run(repo)
    assert result.returncode == 1
    assert "decisions.sequential-numbering" in result.stdout
    assert "docs/decisions/0000-zero.md" in result.stdout


def test_non_zero_padded_number_is_flagged(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {"docs/decisions/1-first.md": record("First")},
    )
    result = run(repo)
    assert result.returncode == 1
    assert "decisions.sequential-numbering" in result.stdout
    assert "docs/decisions/1-first.md" in result.stdout


def test_index_and_readme_are_not_records(tmp_path: Path) -> None:
    """index.md and README.md carry no number, so they do not perturb the run."""
    repo = make_repo(
        tmp_path,
        {
            "docs/decisions/0001-first.md": record("First"),
            "docs/decisions/index.md": "# docs/decisions/ — index\n",
            "docs/decisions/README.md": (
                "---\ntype: README\ntitle: Records\ndescription: Records\n---\n\n# R\n"
            ),
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_absent_decisions_directory_passes(tmp_path: Path) -> None:
    """A repo with no docs/decisions/ is clean — the directory is lazily created."""
    repo = make_repo(tmp_path, {"README.md": "# Repo\n"})
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_numbered_file_outside_decisions_is_not_scanned(tmp_path: Path) -> None:
    """The rule is scoped to docs/decisions/; a stray NNNN-slug elsewhere is ignored."""
    repo = make_repo(
        tmp_path,
        {
            "docs/decisions/0001-first.md": record("First"),
            "docs/0003-loose.md": record("Loose"),
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


# --- status-vocabulary rule ---


def test_proposed_status_is_clean(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {"docs/decisions/0001-first.md": record("First", status="proposed")},
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_record_without_status_is_clean(tmp_path: Path) -> None:
    """status is optional; a record that omits it is not flagged."""
    repo = make_repo(
        tmp_path,
        {"docs/decisions/0001-first.md": record("First")},
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_status_off_the_vocabulary_is_flagged(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {"docs/decisions/0001-first.md": record("First", status="draft")},
    )
    result = run(repo)
    assert result.returncode == 1
    assert "decisions.status-vocabulary" in result.stdout
    assert "docs/decisions/0001-first.md" in result.stdout


def test_superseded_by_number_is_valid(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "docs/decisions/0001-first.md": record(
                "First", status="superseded by 0002"
            ),
            "docs/decisions/0002-second.md": record("Second"),
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_superseded_without_a_padded_number_is_flagged(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {"docs/decisions/0001-first.md": record("First", status="superseded")},
    )
    result = run(repo)
    assert result.returncode == 1
    assert "decisions.status-vocabulary" in result.stdout


def test_status_check_ignores_non_record_files(tmp_path: Path) -> None:
    """status-vocabulary, like sequential-numbering, judges only NNNN-slug.md
    records: a non-record file (index.md/README.md) that carries an
    off-vocabulary status must not be flagged as a record."""
    repo = make_repo(
        tmp_path,
        {
            "docs/decisions/0001-first.md": record("First"),
            "docs/decisions/README.md": record("Readme", status="draft"),
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


# --- environment failures ---


def test_malformed_frontmatter_cannot_run_exits_2(tmp_path: Path) -> None:
    """A record with a broken frontmatter block is a precondition the detector
    cannot judge: it exits 2 (cannot run) with a clear message, not a traceback."""
    repo = make_repo(
        tmp_path,
        {"docs/decisions/0001-first.md": "---\ntitle: [unterminated\n---\n\n# X\n"},
    )
    result = run(repo)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "cannot run" in result.stderr.lower()
    assert "docs/decisions/0001-first.md" in result.stderr


# --- rule ids and finding format ---


def test_list_rules_prints_card_prefixed_ids_from_any_cwd(tmp_path: Path) -> None:
    """--list-rules names both rules, card-prefixed, needing no repository."""
    result = subprocess.run(
        ["uv", "run", "--script", str(SCRIPT), "--list-rules"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    ids = result.stdout.split()
    assert "decisions.sequential-numbering" in ids
    assert "decisions.status-vocabulary" in ids


def test_finding_line_is_gnu_format(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {"docs/decisions/0001-first.md": record("First", status="draft")},
    )
    result = run(repo)
    assert result.returncode == 1
    assert "docs/decisions/0001-first.md: decisions.status-vocabulary " in result.stdout
