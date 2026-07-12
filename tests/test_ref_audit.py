"""Behavioral tests for scripts/ref-audit — assert on exit code and stderr.

Two reference forms are validated (see this repo's cross-reference standard):
a root-absolute `/path` **Link** for same-repo targets, and a
`~/workspace/<repo>/...` **Citation** for cross-repo targets. A same-repo
Citation in a fixed-root file is a `wrong-form` violation; the same Citation in
a rootless file (skills, rules, box artifacts) is legitimate. The tests below
use the Link form wherever the subject under test is anchor/existence logic,
and the Citation form wherever the citation handling itself is the subject.
"""

import os
import re
import subprocess
from pathlib import Path

import pytest

REF_AUDIT = Path(__file__).resolve().parents[1] / "scripts" / "ref-audit"


def run_ref_audit(
    repo_root: Path, home: Path, *args: str
) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["HOME"] = str(home)
    return subprocess.run(
        ["python3", str(REF_AUDIT), *args, str(repo_root)],
        capture_output=True,
        text=True,
        env=env,
    )


def init_repo(path: Path) -> None:
    subprocess.run(
        ["git", "init", "-q", "-b", "main", str(path)],
        check=True,
        capture_output=True,
    )


def commit_all(repo: Path) -> None:
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.email=t@example.com",
            "-c",
            "user.name=test",
            "commit",
            "-q",
            "-m",
            "init",
        ],
        check=True,
    )


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    ws = tmp_path / "workspace"
    ws.mkdir()
    return ws


def write(file: Path, content: str) -> None:
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(content)


# --- Link class: root-absolute `/path` targets, the same-repo form ---


def test_root_link_to_existing_file_is_ok(tmp_path: Path, workspace: Path) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "standards" / "target.md", "x")
    write(repo / "docs.md", "see [target](/standards/target.md)\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0, result.stderr
    assert "all ok" in result.stderr


def test_root_link_to_missing_file_is_broken(tmp_path: Path, workspace: Path) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "docs.md", "see [gone](/standards/gone.md)\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 1
    assert "1 broken" in result.stderr
    assert "/standards/gone.md" in result.stdout


def test_root_link_resolves_against_worktree_working_copy(
    tmp_path: Path, workspace: Path
) -> None:
    """A `/`-root Link resolves against the invoking worktree's own root, so a
    file present only in the worktree resolves as ok."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "README.md", "base")
    commit_all(repo)

    wt = repo / ".claude" / "worktrees" / "feature-x"
    subprocess.run(
        ["git", "-C", str(repo), "worktree", "add", "-q", str(wt), "-b", "feature-x"],
        check=True,
    )
    write(wt / "target.md", "only here")
    write(wt / "docs.md", "see [target](/target.md)\n")
    assert not (repo / "target.md").exists()

    result = run_ref_audit(wt, tmp_path)

    assert result.returncode == 0, result.stderr


def test_bare_slash_token_is_prose_not_a_link(tmp_path: Path, workspace: Path) -> None:
    """`/commit` and other bare slash tokens are slash-skills/prose, not Links —
    a `/` target is only checked inside markdown link syntax."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "docs.md", "run /commit then /open-pr to finish /nonexistent\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0
    assert "no cross-references found" in result.stderr


def test_root_link_inside_inline_code_is_skipped(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "docs.md", "the linter lives at `/tools/bin/ref-audit`\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0
    assert "no cross-references found" in result.stderr


def test_root_link_inside_fenced_block_is_skipped(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "docs.md", "intro\n```\n[x](/gone.md)\n```\nend\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0
    assert "no cross-references found" in result.stderr


def test_root_link_to_directory_with_fragment_is_out_of_scope(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    (repo / "standards").mkdir()
    write(repo / "docs.md", "see [dir](/standards#anything)\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0


# --- Citation class: `~/workspace/<repo>/...` targets ---


def test_cross_repo_ref_to_existing_file_is_ok(tmp_path: Path, workspace: Path) -> None:
    repo = workspace / "primary"
    other = workspace / "other"
    init_repo(repo)
    other.mkdir()
    write(other / "thing.md", "x")
    write(repo / "docs.md", "see ~/workspace/other/thing.md\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0


def test_cross_repo_ref_to_missing_file_is_broken(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    other = workspace / "other"
    init_repo(repo)
    other.mkdir()
    write(repo / "docs.md", "see ~/workspace/other/missing.md\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 1
    assert "1 broken" in result.stderr


def test_cross_repo_ref_to_missing_repo_is_broken(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "docs.md", "see ~/workspace/no-such-repo/foo.md\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 1


def test_reference_inside_inline_code_is_skipped(
    tmp_path: Path, workspace: Path
) -> None:
    """Backticked content is prose — refs inside `~/workspace/<placeholder>`
    syntax must not be classified."""
    repo = workspace / "primary"
    init_repo(repo)
    write(
        repo / "docs.md",
        "see `~/workspace/<name>/missing.md` for the template\n",
    )

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0
    assert "no cross-references found" in result.stderr


def test_reference_inside_fenced_code_block_is_skipped(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(
        repo / "docs.md",
        "intro\n```\nsee ~/workspace/other/missing.md\n```\nend\n",
    )

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0
    assert "no cross-references found" in result.stderr


def test_citation_inside_link_text_is_validated(
    tmp_path: Path, workspace: Path
) -> None:
    """A ~/workspace citation in a link's *text* (not its target) is still a
    citation and must be validated — the bare-citation pass strips link spans
    to their text, not away entirely, so text stays scannable."""
    repo = workspace / "primary"
    init_repo(repo)
    write(
        repo / "docs.md",
        "[see ~/workspace/other/missing.md now](https://example.com)\n",
    )

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 1
    assert "1 broken" in result.stderr
    assert "~/workspace/other/missing.md" in result.stdout


def test_citation_inside_link_text_resolving_is_ok(
    tmp_path: Path, workspace: Path
) -> None:
    """The happy path of the above: an existing citation in link text passes."""
    repo = workspace / "primary"
    other = workspace / "other"
    init_repo(repo)
    other.mkdir()
    write(other / "thing.md", "x")
    write(
        repo / "docs.md",
        "[see ~/workspace/other/thing.md](https://example.com)\n",
    )

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0, result.stderr
    assert "all ok" in result.stderr


# --- wrong-form: same-repo Citation in a fixed-root file ---


def test_same_repo_citation_in_fixed_root_file_is_wrong_form(
    tmp_path: Path, workspace: Path
) -> None:
    """A concept doc must reference same-repo targets by Link, not Citation —
    even when the target exists, the citation form is a violation."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "x")
    write(repo / "docs.md", "see ~/workspace/primary/target.md\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 1
    assert "1 wrong-form" in result.stderr
    assert "wrong-form" in result.stdout


def test_wrong_form_reported_even_when_target_missing(
    tmp_path: Path, workspace: Path
) -> None:
    """The form is the actionable error, so it short-circuits existence: a
    same-repo citation to a missing file reports wrong-form, not broken."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "docs.md", "see ~/workspace/primary/missing.md\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 1
    assert "1 wrong-form" in result.stderr
    assert "0 broken" in result.stderr


# --- rootless files: skills, rules, box artifacts use the Citation form ---


def test_same_repo_citation_in_skill_is_ok(tmp_path: Path, workspace: Path) -> None:
    """A skill has no fixed repo root, so a same-repo Citation is legitimate."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "standards" / "target.md", "x")
    write(
        repo / "skills" / "demo" / "SKILL.md",
        "see ~/workspace/primary/standards/target.md\n",
    )

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0, result.stderr
    assert "all ok" in result.stderr


def test_same_repo_citation_in_rules_is_ok(tmp_path: Path, workspace: Path) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "x")
    write(repo / "rules" / "a.md", "see ~/workspace/primary/target.md\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0, result.stderr


def test_same_repo_citation_in_box_artifact_is_ok(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "conventions.md", "x")
    write(repo / "box" / "charter.md", "see ~/workspace/primary/conventions.md\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0, result.stderr


def test_same_repo_citation_to_missing_file_in_rootless_file_is_broken(
    tmp_path: Path, workspace: Path
) -> None:
    """The Citation form is legitimate in a skill, so it is existence-checked
    normally — a missing target is broken, not wrong-form."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "skills" / "demo" / "SKILL.md", "see ~/workspace/primary/gone.md\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 1
    assert "1 broken" in result.stderr


def test_worktree_resolves_rootless_citation_to_worktree_working_copy(
    tmp_path: Path, workspace: Path
) -> None:
    """A same-repo Citation in a skill resolves against the worktree's own
    working copy, so a file present only in the worktree resolves as ok."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "README.md", "base")
    commit_all(repo)

    wt = repo / ".claude" / "worktrees" / "feature-x"
    subprocess.run(
        ["git", "-C", str(repo), "worktree", "add", "-q", str(wt), "-b", "feature-x"],
        check=True,
    )
    write(wt / "target.md", "only here")
    write(wt / "skills" / "demo" / "SKILL.md", "see ~/workspace/primary/target.md\n")
    assert not (repo / "target.md").exists()

    result = run_ref_audit(wt, tmp_path)

    assert result.returncode == 0, result.stderr


# --- Decision Records are excluded as reference sources ---


def test_broken_refs_inside_decisions_directory_are_skipped(
    tmp_path: Path, workspace: Path
) -> None:
    """Decision Records are immutable — broken refs in them are expected
    staleness, not lint errors. The exemption is permanent and scoped to the
    records directory, docs/decisions/."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "x")
    write(repo / "other.md", "see [target](/target.md)\n")
    write(
        repo / "docs" / "decisions" / "0001-decision.md",
        "see ~/workspace/primary/gone.md\n",
    )

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0
    assert "all ok" in result.stderr


def test_broken_refs_under_standards_decisions_are_still_validated(
    tmp_path: Path, workspace: Path
) -> None:
    """The exemption is scoped to docs/decisions/, not any 'decisions' segment:
    the contract under standards/decisions/ is validated like any other doc."""
    repo = workspace / "primary"
    init_repo(repo)
    write(
        repo / "standards" / "decisions" / "records.md",
        "see [gone](/nope.md)\n",
    )

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 1
    assert "broken" in result.stdout


# --- environment failures ---


def test_not_a_git_repo_exits_2(tmp_path: Path, workspace: Path) -> None:
    not_a_repo = workspace / "no-git-here"
    not_a_repo.mkdir()
    write(not_a_repo / "docs.md", "irrelevant\n")

    result = run_ref_audit(not_a_repo, tmp_path)

    assert result.returncode == 2
    assert "not a git repository" in result.stderr


# --- fragment anchors (exercised through the Link form) ---


def test_anchor_matching_existing_heading_is_ok(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "## Real heading\n")
    write(repo / "docs.md", "see [x](/target.md#real-heading)\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0
    assert "all ok" in result.stderr


def test_anchor_missing_on_existing_file_is_broken(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "## Real heading\n")
    write(repo / "docs.md", "see [x](/target.md#no-such-section)\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 1
    assert "1 broken" in result.stderr


def test_slug_handles_numbered_heading_with_periods(
    tmp_path: Path, workspace: Path
) -> None:
    """`### 2.2.3 revision` slugs to `223-revision` — periods drop, spaces hyphenate."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "### 2.2.3 revision\n")
    write(repo / "docs.md", "see [x](/target.md#223-revision)\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0


def test_slug_handles_parentheses_in_heading(tmp_path: Path, workspace: Path) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "## Issue body format (the brief is the body)\n")
    write(
        repo / "docs.md",
        "see [x](/target.md#issue-body-format-the-brief-is-the-body)\n",
    )

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0


def test_slug_handles_em_dash_in_heading(tmp_path: Path, workspace: Path) -> None:
    """Em dashes drop; surrounding spaces produce a double hyphen (no collapsing)."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "## Step 1 — See the shape\n")
    write(repo / "docs.md", "see [x](/target.md#step-1--see-the-shape)\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0


def test_slug_strips_inline_code_in_heading(tmp_path: Path, workspace: Path) -> None:
    """Backtick spans in a heading contribute their text content, not the backticks."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "## Without `fast` (default staging)\n")
    write(repo / "docs.md", "see [x](/target.md#without-fast-default-staging)\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0


def test_slug_keeps_intraword_underscores(tmp_path: Path, workspace: Path) -> None:
    """Underscores flanked by word chars are literal, not emphasis — matching
    GitHub's rendered-text anchors. `## load_issue helper` → `#load_issue-helper`."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "## load_issue helper\n")
    write(repo / "docs.md", "see [x](/target.md#load_issue-helper)\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0
    assert "all ok" in result.stderr


def test_slug_strips_underscore_emphasis_at_word_boundaries(
    tmp_path: Path, workspace: Path
) -> None:
    """A whole-word `_emphasis_` is real emphasis: markers drop, text stays."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "## the _important_ part\n")
    write(repo / "docs.md", "see [x](/target.md#the-important-part)\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0


def test_reference_without_fragment_does_not_require_headings(
    tmp_path: Path, workspace: Path
) -> None:
    """Existing behavior: file-only refs are validated against file existence."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "no headings at all in this file\n")
    write(repo / "docs.md", "see [x](/target.md)\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0


def test_heading_inside_fenced_block_in_target_is_ignored(
    tmp_path: Path, workspace: Path
) -> None:
    """A `## Heading` inside a fenced code block in the target is not real."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "```\n## Fake heading\n```\n")
    write(repo / "docs.md", "see [x](/target.md#fake-heading)\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 1


def test_fragment_on_non_markdown_target_is_out_of_scope(
    tmp_path: Path, workspace: Path
) -> None:
    """A fragment on a non-.md target is treated as ok — anchors aren't a thing there."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "script.py", "print('hi')\n")
    write(repo / "docs.md", "see [x](/script.py#some-fragment)\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0


def test_missing_file_with_fragment_is_broken_not_anchor_check(
    tmp_path: Path, workspace: Path
) -> None:
    """File-missing short-circuits: anchor never evaluated when file is absent."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "docs.md", "see [x](/nope.md#make-believe-heading)\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 1
    assert "1 broken" in result.stderr


def test_multiple_headings_in_one_target_are_all_addressable(
    tmp_path: Path, workspace: Path
) -> None:
    """Every ATX heading level contributes a slug; a ref to any of them is ok."""
    repo = workspace / "primary"
    init_repo(repo)
    write(
        repo / "target.md",
        "# Top\n## Middle\n### Inner\n#### Deepest\n",
    )
    write(
        repo / "docs.md",
        "see [a](/target.md#top)\n"
        "see [b](/target.md#middle)\n"
        "see [c](/target.md#inner)\n"
        "see [d](/target.md#deepest)\n",
    )

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0
    assert "all ok" in result.stderr


def test_worktree_resolves_anchor_against_worktree_target(
    tmp_path: Path, workspace: Path
) -> None:
    """Anchor validation must use the worktree's copy of the target file.

    A heading renamed in the worktree must resolve against the worktree
    state, not the main checkout — otherwise edits within a worktree
    would fail ref-audit until merged.
    """
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "README.md", "base")
    commit_all(repo)

    wt = repo / ".claude" / "worktrees" / "feature-x"
    subprocess.run(
        ["git", "-C", str(repo), "worktree", "add", "-q", str(wt), "-b", "feature-x"],
        check=True,
    )
    write(wt / "target.md", "## Renamed in worktree\n")
    write(wt / "docs.md", "see [x](/target.md#renamed-in-worktree)\n")
    assert not (repo / "target.md").exists()

    result = run_ref_audit(wt, tmp_path)

    assert result.returncode == 0, result.stderr


def test_same_file_self_anchor_resolves(tmp_path: Path, workspace: Path) -> None:
    """A self-reference (source == target) with an anchor still validates."""
    repo = workspace / "primary"
    init_repo(repo)
    write(
        repo / "foo.md",
        "See [the details below](/foo.md#details).\n\n## Details\n",
    )

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0
    assert "all ok" in result.stderr


# --- counting across classes ---


def test_both_link_classes_counted_in_one_run(tmp_path: Path, workspace: Path) -> None:
    """A Link and a cross-repo Citation on the same file both count."""
    repo = workspace / "primary"
    other = workspace / "other"
    init_repo(repo)
    other.mkdir()
    write(repo / "target.md", "x")
    write(other / "thing.md", "x")
    write(
        repo / "docs.md",
        "a [link](/target.md) and a citation ~/workspace/other/thing.md\n",
    )

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 0, result.stderr
    assert "2 references, all ok" in result.stderr


def test_list_rules_prints_docs_prefixed_ids_from_any_cwd(tmp_path: Path) -> None:
    result = subprocess.run(
        ["python3", str(REF_AUDIT), "--list-rules"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    ids = result.stdout.split()
    assert "docs.broken-reference" in ids
    assert "docs.wrong-form-citation" in ids
    assert all(rule.startswith("docs.") for rule in ids), ids


def test_broken_reference_renders_as_gnu_finding(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "docs.md", "see [gone](/standards/gone.md)\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 1
    assert re.search(
        r"^docs\.md:\d+: docs\.broken-reference .*standards/gone\.md",
        result.stdout,
        re.MULTILINE,
    ), result.stdout


def test_wrong_form_citation_renders_as_gnu_finding(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "x")
    write(repo / "docs.md", "see ~/workspace/primary/target.md\n")

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 1
    assert re.search(
        r"^docs\.md:\d+: docs\.wrong-form-citation ",
        result.stdout,
        re.MULTILINE,
    ), result.stdout


def test_mixed_pass_and_fail_in_one_run_reports_only_the_broken(
    tmp_path: Path, workspace: Path
) -> None:
    """Default-mode output contains the broken ref only; summary counts both."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "## Real heading\n")
    write(
        repo / "docs.md",
        "ok ref:     [a](/target.md#real-heading)\n"
        "broken ref: [b](/target.md#missing-heading)\n",
    )

    result = run_ref_audit(repo, tmp_path)

    assert result.returncode == 1
    assert "1/2 need fixing" in result.stderr
    assert "#missing-heading" in result.stdout
    assert "#real-heading" not in result.stdout
