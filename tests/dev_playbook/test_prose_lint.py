"""Behavioral tests for the prose-lint detector, src/dev_playbook/prose_lint.py.

The rule prose.judgment-spelling flags the British judgement / judgements form
in authored Markdown; prose.banned-word flags the banned actor noun "human" in
every tracked file, with no code-span or fence escape. This test file is one of
the two files exempt from the ban (prose_lint.BANNED_EXEMPT) — its fixtures
must name the word to test it. The scanning logic is tested with string inputs;
the discovery, exclusion, and CLI behaviors are tested over throwaway git repos
(discovery goes through git ls-files, so every fixture is a git repo).
"""

import os
import subprocess
from pathlib import Path

import pytest

from dev_playbook import prose_lint
from dev_playbook.repo_init import RepoInitError, RepoSpec, render_tree

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


# --- scan_banned: the banned-word rule over string inputs ---


def test_flags_banned_actor_noun() -> None:
    findings = prose_lint.scan_banned("f.md", "ask the human first\n")

    assert len(findings) == 1
    assert findings[0].rule == prose_lint.BANNED_WORD
    assert findings[0].line == 1


def test_flags_plural_and_capitalized_forms() -> None:
    findings = prose_lint.scan_banned("f.md", "Humans differ.\nHUMAN input.\n")

    assert [f.line for f in findings] == [1, 2]


def test_flags_hyphenated_compound() -> None:
    # The word boundary sits at the hyphen, so compounds are the noun too.
    findings = prose_lint.scan_banned("f.md", "a human-readable name\n")

    assert len(findings) == 1


def test_longer_words_are_not_the_noun() -> None:
    assert prose_lint.scan_banned("f.md", "a humane, superhuman effort\n") == []


def test_code_span_is_not_an_escape_for_the_ban() -> None:
    # Unlike the spelling rule, the ban is absolute: backticks do not shelter it.
    assert len(prose_lint.scan_banned("f.md", "the `human` token\n")) == 1


def test_fenced_block_is_not_an_escape_for_the_ban() -> None:
    findings = prose_lint.scan_banned("f.md", "before\n```\nhuman\n```\nafter\n")

    assert [f.line for f in findings] == [3]


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


def test_skips_transient_plan_progress_scratch(tmp_path: Path) -> None:
    # PLAN.md / PROGRESS.md are the ralph-loop scratch pair — md.classify's
    # "excluded" category, out of the authored-content bundle. A British spelling
    # in throwaway scratch must not block every commit.
    repo = make_repo(
        tmp_path,
        {"PLAN.md": "a judgement in scratch\n", "PROGRESS.md": "another judgement\n"},
    )

    assert prose_lint.audit(repo) == []


def test_skips_root_tmp_scratch_tree(tmp_path: Path) -> None:
    # The root tmp/ tree is scratch too — excluded, never scanned.
    repo = make_repo(tmp_path, {"tmp/notes.md": "a judgement here\n"})

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


def test_ban_reaches_non_markdown_files(tmp_path: Path) -> None:
    # The ban reads every tracked file, not just Markdown — a code comment or a
    # config value carrying the noun is a finding.
    repo = make_repo(tmp_path, {"src/tool.py": "# reviewed by a human\n"})

    findings = prose_lint.audit(repo)

    assert [(f.file, f.rule) for f in findings] == [
        ("src/tool.py", prose_lint.BANNED_WORD)
    ]


def test_ban_reaches_frontmatter(tmp_path: Path) -> None:
    # The spelling rule scans the body only; the ban has no such carve-out.
    repo = make_repo(
        tmp_path,
        {"docs/x.md": "---\ntype: Standard\ndescription: for the human\n---\nbody\n"},
    )

    findings = prose_lint.audit(repo)

    assert [(f.file, f.line) for f in findings] == [("docs/x.md", 3)]


def test_ban_skips_vendored_and_verbatim(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "dotfiles/.agents/skills/x/SKILL.md": "the human partner\n",
            "standards/references/spec.md": "---\ntype: Reference\n---\nhuman\n",
        },
    )

    assert prose_lint.audit(repo) == []


def test_ban_exempt_roster_is_honored(tmp_path: Path) -> None:
    # The detector and its tests must name the word to ban it — the one
    # sanctioned residue.
    repo = make_repo(
        tmp_path,
        {
            "src/dev_playbook/prose_lint.py": "BANNED = 'human'\n",
            "tests/dev_playbook/test_prose_lint.py": "text = 'a human'\n",
        },
    )

    assert prose_lint.audit(repo) == []


def test_binary_file_is_skipped(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"data/blob.bin": ""})
    (repo / "data/blob.bin").write_bytes(b"human\0human")

    assert prose_lint.audit(repo) == []


def test_symlinked_content_is_not_scanned(tmp_path: Path) -> None:
    # A symlink's content belongs to its target: vendored targets are not ours,
    # and in-repo targets are scanned at their own path.
    repo = make_repo(
        tmp_path, {"dotfiles/.agents/skills/x/SKILL.md": "the human partner\n"}
    )
    link = repo / "dotfiles/dot-claude/skills/x/SKILL.md"
    link.parent.mkdir(parents=True)
    os.symlink("../../../.agents/skills/x/SKILL.md", link)

    assert prose_lint.audit(repo) == []


@pytest.mark.parametrize("name", ["the-human", "human-readable"])
def test_ban_reaches_repo_names(name: str) -> None:
    # repo-init consults the ban pattern before scaffolding, so a name that
    # would put the noun in a fresh CLAUDE.md H1 is refused up front.
    spec = RepoSpec(name=name, description="A demo repo", python=False)

    with pytest.raises(RepoInitError, match="prose-lint"):
        render_tree(spec, "0" * 40)


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
    assert result.stdout.split() == ["prose.banned-word", "prose.judgment-spelling"]


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
