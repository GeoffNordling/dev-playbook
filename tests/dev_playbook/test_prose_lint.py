"""Behavioral tests for the prose-lint detector, src/dev_playbook/prose_lint.py.

The rule prose.judgment-spelling flags the British judgement / judgements form
in authored Markdown. The scanning logic is tested with string inputs; the
discovery, exclusion, and CLI behaviors are tested over throwaway git repos
(discovery goes through git ls-files, so every fixture is a git repo).
"""

import subprocess
from pathlib import Path

from dev_playbook import prose_lint

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "prose-lint"


def make_repo(tmp_path: Path, files: dict[str, str]) -> Path:
    """Write files into a fresh git repo and return its root."""
    repo = tmp_path / "repo"
    for rel, content in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    return repo


# --- scan_text: the rule over string inputs ---


def test_flags_british_singular() -> None:
    findings = prose_lint.scan_text("f.md", "a judgement call\n")

    assert len(findings) == 1
    assert findings[0].rule == prose_lint.JUDGMENT_SPELLING
    assert findings[0].line == 1


def test_flags_british_plural() -> None:
    findings = prose_lint.scan_text("f.md", "two judgements later\n")

    assert len(findings) == 1


def test_american_spelling_is_clean() -> None:
    assert prose_lint.scan_text("f.md", "a judgment call\n") == []


def test_flags_capitalized_form() -> None:
    findings = prose_lint.scan_text("f.md", "Judgement matters here\n")

    assert len(findings) == 1


def test_judgemental_is_not_flagged() -> None:
    # The rule matches the words judgement / judgements only, not longer words
    # that merely contain the sequence.
    assert prose_lint.scan_text("f.md", "a judgemental tone\n") == []


def test_inline_code_span_is_skipped() -> None:
    assert prose_lint.scan_text("f.md", "the `judgement` token is fine\n") == []


def test_double_backtick_code_span_is_skipped() -> None:
    # A double-backtick span (the form used when the code itself contains a
    # backtick) must be stripped whole — not read as two adjacent empty
    # single-backtick spans that leave the word exposed to the scanner.
    assert prose_lint.scan_text("f.md", "the ``judgement`` token is fine\n") == []


def test_fenced_block_is_skipped() -> None:
    assert prose_lint.scan_text("f.md", "before\n```\njudgement\n```\nafter\n") == []


def test_reports_the_offending_line_number() -> None:
    findings = prose_lint.scan_text("f.md", "clean\nline\na judgement here\n")

    assert findings[0].line == 3


# --- audit: discovery, scope, and exclusions over a repo ---


def test_flags_harness_markdown(tmp_path: Path) -> None:
    # Scope is all authored Markdown, harness files included — not md.classify's
    # concept-only set. A CLAUDE.md (harness) carrying the British form is flagged.
    repo = make_repo(tmp_path, {"CLAUDE.md": "Exercise judgement here.\n"})

    findings = prose_lint.audit(repo)

    assert [f.file for f in findings] == ["CLAUDE.md"]


def test_skips_externally_managed_tree(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {"dotfiles/.agents/skills/x/SKILL.md": "vendored judgement text\n"},
    )

    assert prose_lint.audit(repo) == []


def test_skips_verbatim_reference_doc(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {"standards/references/x.md": "---\ntype: Reference\n---\na judgement\n"},
    )

    assert prose_lint.audit(repo) == []


def test_flags_non_reference_doc(tmp_path: Path) -> None:
    # Control for the verbatim exclusion: an authored (non-Reference) doc with
    # the same body is flagged.
    repo = make_repo(
        tmp_path,
        {"standards/x.md": "---\ntype: Standard\n---\na judgement\n"},
    )

    findings = prose_lint.audit(repo)

    assert [f.file for f in findings] == ["standards/x.md"]


def test_frontmatter_values_are_not_scanned_as_prose(tmp_path: Path) -> None:
    # Frontmatter is structured YAML, not prose, and a YAML scalar has no
    # backtick escape hatch — so a title/description carrying the British form in
    # a non-Reference doc must not be flagged. Only the body is scanned.
    repo = make_repo(
        tmp_path,
        {
            "standards/x.md": (
                "---\ntype: Standard\ntitle: A judgement of taste\n---\nclean body\n"
            )
        },
    )

    assert prose_lint.audit(repo) == []


def test_body_finding_reports_absolute_line_number(tmp_path: Path) -> None:
    # The scanner runs over the body only, but reported line numbers stay
    # absolute to the file so an editor jumps to the right line.
    repo = make_repo(
        tmp_path,
        {"standards/x.md": "---\ntype: Standard\n---\na judgement\n"},
    )

    findings = prose_lint.audit(repo)

    assert [(f.file, f.line) for f in findings] == [("standards/x.md", 4)]


def test_malformed_frontmatter_exits_two_not_traceback(tmp_path: Path) -> None:
    # A single .md with a malformed frontmatter block — even an untracked draft,
    # since discovery lists --others — must surface as the detector's exit 2, not
    # an uncaught YAML traceback that blocks every commit.
    repo = make_repo(
        tmp_path,
        {"draft.md": "---\ntype: [unterminated\n---\nbody\n"},
    )

    assert prose_lint.main([str(repo)]) == 2


# --- CLI: --list-rules, exit codes, and finding format ---


def run(repo: Path) -> subprocess.CompletedProcess:
    """Run scripts/prose-lint against repo and capture its output."""
    return subprocess.run(
        ["python3", str(SCRIPT), str(repo)],
        capture_output=True,
        text=True,
    )


def test_list_rules_prints_the_rule_id(tmp_path: Path) -> None:
    result = subprocess.run(
        ["python3", str(SCRIPT), "--list-rules"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.split() == ["prose.judgment-spelling"]


def test_clean_repo_exits_zero(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"doc.md": "a sound judgment\n"})

    result = run(repo)

    assert result.returncode == 0, result.stdout + result.stderr


def test_finding_line_is_gnu_format(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"doc.md": "a judgement call\n"})

    result = run(repo)

    assert result.returncode == 1
    assert "doc.md:1: prose.judgment-spelling " in result.stdout


def test_dev_playbook_self_scan_is_clean() -> None:
    repo = Path(__file__).resolve().parents[2]

    result = run(repo)

    assert result.returncode == 0, result.stdout + result.stderr
