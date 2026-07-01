"""Behavioral tests for tools/bin/ref-check — assert on exit code and stderr."""

import os
import subprocess
from pathlib import Path

import pytest

REF_CHECK = Path(__file__).resolve().parents[1] / "bin" / "ref-check"


def run_ref_check(
    repo_root: Path, home: Path, *args: str
) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["HOME"] = str(home)
    return subprocess.run(
        ["python3", str(REF_CHECK), *args, str(repo_root)],
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


def test_in_repo_ref_to_existing_file_is_ok(tmp_path: Path, workspace: Path) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "x")
    write(repo / "docs.md", "see ~/workspace/primary/target.md\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0
    assert "all ok" in result.stderr


def test_in_repo_ref_to_missing_file_is_broken(tmp_path: Path, workspace: Path) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "docs.md", "see ~/workspace/primary/missing.md\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 1
    assert "1/1 broken" in result.stderr


def test_cross_repo_ref_to_existing_file_is_ok(tmp_path: Path, workspace: Path) -> None:
    repo = workspace / "primary"
    other = workspace / "other"
    init_repo(repo)
    other.mkdir()
    write(other / "thing.md", "x")
    write(repo / "docs.md", "see ~/workspace/other/thing.md\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0


def test_cross_repo_ref_to_missing_file_is_broken(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    other = workspace / "other"
    init_repo(repo)
    other.mkdir()
    write(repo / "docs.md", "see ~/workspace/other/missing.md\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 1


def test_cross_repo_ref_to_missing_repo_is_broken(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "docs.md", "see ~/workspace/no-such-repo/foo.md\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 1


def test_reference_inside_inline_code_is_skipped(
    tmp_path: Path, workspace: Path
) -> None:
    """Backticked content is prose per repo-documentation.md — refs inside
    `~/workspace/<placeholder>` syntax must not be classified."""
    repo = workspace / "primary"
    init_repo(repo)
    write(
        repo / "docs.md",
        "see `~/workspace/<name>/missing.md` for the template\n",
    )

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0
    assert "no cross-references found" in result.stderr


def test_reference_inside_fenced_code_block_is_skipped(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(
        repo / "docs.md",
        "intro\n```\nsee ~/workspace/primary/missing.md\n```\nend\n",
    )

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0
    assert "no cross-references found" in result.stderr


def test_broken_refs_inside_adr_directory_are_skipped(
    tmp_path: Path, workspace: Path
) -> None:
    """ADRs are immutable historical records — broken refs in them are
    expected staleness, not lint errors."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "x")
    write(repo / "other.md", "see ~/workspace/primary/target.md\n")
    write(
        repo / "docs" / "adr" / "0001-decision.md",
        "see ~/workspace/primary/gone.md\n",
    )

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0
    assert "all ok" in result.stderr


def test_worktree_resolves_in_repo_refs_to_worktree_working_copy(
    tmp_path: Path, workspace: Path
) -> None:
    """File present only in the worktree's working copy must resolve as ok."""
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
    write(wt / "docs.md", "see ~/workspace/primary/target.md\n")
    assert not (repo / "target.md").exists()

    result = run_ref_check(wt, tmp_path)

    assert result.returncode == 0, result.stderr


def test_not_a_git_repo_exits_2(tmp_path: Path, workspace: Path) -> None:
    not_a_repo = workspace / "no-git-here"
    not_a_repo.mkdir()
    write(not_a_repo / "docs.md", "irrelevant\n")

    result = run_ref_check(not_a_repo, tmp_path)

    assert result.returncode == 2
    assert "not a git repository" in result.stderr


def test_anchor_matching_existing_heading_is_ok(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "## Real heading\n")
    write(repo / "docs.md", "see ~/workspace/primary/target.md#real-heading\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0
    assert "all ok" in result.stderr


def test_anchor_missing_on_existing_file_is_broken(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "## Real heading\n")
    write(repo / "docs.md", "see ~/workspace/primary/target.md#no-such-section\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 1
    assert "1/1 broken" in result.stderr


def test_slug_handles_numbered_heading_with_periods(
    tmp_path: Path, workspace: Path
) -> None:
    """`### 2.2.3 revision` slugs to `223-revision` — periods drop, spaces hyphenate."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "### 2.2.3 revision\n")
    write(repo / "docs.md", "see ~/workspace/primary/target.md#223-revision\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0


def test_slug_handles_parentheses_in_heading(tmp_path: Path, workspace: Path) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "## Issue body format (the brief is the body)\n")
    write(
        repo / "docs.md",
        "see ~/workspace/primary/target.md#issue-body-format-the-brief-is-the-body\n",
    )

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0


def test_slug_handles_em_dash_in_heading(tmp_path: Path, workspace: Path) -> None:
    """Em dashes drop; surrounding spaces produce a double hyphen (no collapsing)."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "## Step 1 — See the shape\n")
    write(repo / "docs.md", "see ~/workspace/primary/target.md#step-1--see-the-shape\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0


def test_slug_strips_inline_code_in_heading(tmp_path: Path, workspace: Path) -> None:
    """Backtick spans in a heading contribute their text content, not the backticks."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "## Without `fast` (default staging)\n")
    write(
        repo / "docs.md",
        "see ~/workspace/primary/target.md#without-fast-default-staging\n",
    )

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0


def test_slug_keeps_intraword_underscores(tmp_path: Path, workspace: Path) -> None:
    """Underscores flanked by word chars are literal, not emphasis — matching
    GitHub's rendered-text anchors. `## load_issue helper` → `#load_issue-helper`."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "## load_issue helper\n")
    write(repo / "docs.md", "see ~/workspace/primary/target.md#load_issue-helper\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0
    assert "all ok" in result.stderr


def test_slug_strips_underscore_emphasis_at_word_boundaries(
    tmp_path: Path, workspace: Path
) -> None:
    """A whole-word `_emphasis_` is real emphasis: markers drop, text stays."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "## the _important_ part\n")
    write(repo / "docs.md", "see ~/workspace/primary/target.md#the-important-part\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0


def test_reference_without_fragment_does_not_require_headings(
    tmp_path: Path, workspace: Path
) -> None:
    """Existing behavior: file-only refs are validated against file existence."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "no headings at all in this file\n")
    write(repo / "docs.md", "see ~/workspace/primary/target.md\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0


def test_heading_inside_fenced_block_in_target_is_ignored(
    tmp_path: Path, workspace: Path
) -> None:
    """A `## Heading` inside a fenced code block in the target is not real."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "```\n## Fake heading\n```\n")
    write(repo / "docs.md", "see ~/workspace/primary/target.md#fake-heading\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 1


def test_fragment_on_non_markdown_target_is_out_of_scope(
    tmp_path: Path, workspace: Path
) -> None:
    """A fragment on a non-.md target is treated as ok — anchors aren't a thing there."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "script.py", "print('hi')\n")
    write(repo / "docs.md", "see ~/workspace/primary/script.py#some-fragment\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0


def test_fragment_on_directory_target_is_out_of_scope(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    (repo / "subdir").mkdir()
    write(repo / "docs.md", "see ~/workspace/primary/subdir#anything\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0


def test_missing_file_with_fragment_is_broken_not_anchor_check(
    tmp_path: Path, workspace: Path
) -> None:
    """File-missing short-circuits: anchor never evaluated when file is absent."""
    repo = workspace / "primary"
    init_repo(repo)
    write(
        repo / "docs.md",
        "see ~/workspace/primary/nope.md#make-believe-heading\n",
    )

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 1
    assert "1/1 broken" in result.stderr


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
        "see ~/workspace/primary/target.md#top\n"
        "see ~/workspace/primary/target.md#middle\n"
        "see ~/workspace/primary/target.md#inner\n"
        "see ~/workspace/primary/target.md#deepest\n",
    )

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0
    assert "all ok" in result.stderr


def test_worktree_resolves_anchor_against_worktree_target(
    tmp_path: Path, workspace: Path
) -> None:
    """Anchor validation must use the worktree's copy of the target file.

    A heading renamed in the worktree must resolve against the worktree
    state, not the main checkout — otherwise edits within a worktree
    would fail ref-check until merged.
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
    write(wt / "docs.md", "see ~/workspace/primary/target.md#renamed-in-worktree\n")
    assert not (repo / "target.md").exists()

    result = run_ref_check(wt, tmp_path)

    assert result.returncode == 0, result.stderr


def test_same_file_self_anchor_resolves(tmp_path: Path, workspace: Path) -> None:
    """A self-reference (source == target) with an anchor still validates."""
    repo = workspace / "primary"
    init_repo(repo)
    write(
        repo / "foo.md",
        "See [the details below](~/workspace/primary/foo.md#details).\n\n## Details\n",
    )

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0
    assert "all ok" in result.stderr


def test_mixed_pass_and_fail_in_one_run_reports_only_the_broken(
    tmp_path: Path, workspace: Path
) -> None:
    """Default-mode output contains the broken ref only; summary counts both."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "## Real heading\n")
    write(
        repo / "docs.md",
        "ok ref:     ~/workspace/primary/target.md#real-heading\n"
        "broken ref: ~/workspace/primary/target.md#missing-heading\n",
    )

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 1
    assert "1/2 broken" in result.stderr
    assert "#missing-heading" in result.stdout
    assert "#real-heading" not in result.stdout


# --- Link class: root-absolute `/path` targets inside markdown link syntax ---


def test_root_link_to_existing_file_is_ok(tmp_path: Path, workspace: Path) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "standards" / "target.md", "x")
    write(repo / "docs.md", "see [target](/standards/target.md)\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0, result.stderr
    assert "all ok" in result.stderr


def test_root_link_to_missing_file_is_broken(tmp_path: Path, workspace: Path) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "docs.md", "see [gone](/standards/gone.md)\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 1
    assert "1/1 broken" in result.stderr
    assert "/standards/gone.md" in result.stdout


def test_root_link_anchor_matching_heading_is_ok(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "## Real heading\n")
    write(repo / "docs.md", "see [x](/target.md#real-heading)\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0, result.stderr


def test_root_link_anchor_missing_is_broken(tmp_path: Path, workspace: Path) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "## Real heading\n")
    write(repo / "docs.md", "see [x](/target.md#no-such-heading)\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 1
    assert "1/1 broken" in result.stderr


def test_bare_slash_token_is_prose_not_a_link(tmp_path: Path, workspace: Path) -> None:
    """`/commit` and other bare slash tokens are slash-skills/prose, not Links —
    a `/` target is only checked inside markdown link syntax."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "docs.md", "run /commit then /open-pr to finish /nonexistent\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0
    assert "no cross-references found" in result.stderr


def test_root_link_inside_inline_code_is_skipped(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "docs.md", "the linter lives at `/tools/bin/ref-check`\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0
    assert "no cross-references found" in result.stderr


def test_root_link_inside_fenced_block_is_skipped(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "docs.md", "intro\n```\n[x](/gone.md)\n```\nend\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0
    assert "no cross-references found" in result.stderr


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

    result = run_ref_check(wt, tmp_path)

    assert result.returncode == 0, result.stderr


def test_root_link_to_directory_with_fragment_is_out_of_scope(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    (repo / "standards").mkdir()
    write(repo / "docs.md", "see [dir](/standards#anything)\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0


def test_both_link_classes_counted_in_one_run(tmp_path: Path, workspace: Path) -> None:
    """A Link and a Citation on the same file both count toward the total."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "x")
    write(
        repo / "docs.md",
        "a [link](/target.md) and a citation ~/workspace/primary/target.md\n",
    )

    result = run_ref_check(repo, tmp_path, "--all")

    assert result.returncode == 0, result.stderr
    assert "2 references, all ok" in result.stderr


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
        "[see ~/workspace/primary/missing.md now](https://example.com)\n",
    )

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 1
    assert "1/1 broken" in result.stderr
    assert "~/workspace/primary/missing.md" in result.stdout


def test_citation_inside_link_text_resolving_is_ok(
    tmp_path: Path, workspace: Path
) -> None:
    """The happy path of the above: an existing citation in link text passes."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "x")
    write(
        repo / "docs.md",
        "[see ~/workspace/primary/target.md](https://example.com)\n",
    )

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0, result.stderr
    assert "all ok" in result.stderr
