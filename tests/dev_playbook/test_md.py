"""Unit tests for the shared markdown library, src/dev_playbook/md.py."""

from collections.abc import Callable
from pathlib import Path

import pytest
from conftest import init_repo

from dev_playbook import md


class TestGithubSlug:
    @pytest.mark.parametrize(
        "heading, slug",
        [
            ("Branch and worktree", "branch-and-worktree"),
            ("2.2.3 revision", "223-revision"),
            ("Step 1 — See the shape", "step-1--see-the-shape"),
            (
                "Issue body format (the brief is the body)",
                "issue-body-format-the-brief-is-the-body",
            ),
            ("load_issue helper", "load_issue-helper"),
            ("the _important_ part", "the-important-part"),
            ("Without `fast` (default staging)", "without-fast-default-staging"),
        ],
    )
    def test_slug(self, heading: str, slug: str) -> None:
        assert md.github_slug(heading) == slug


class TestLinesOutsideFences:
    def test_skips_fenced_block(self) -> None:
        text = "a\n```\nhidden\n```\nb\n"
        got = [line.rstrip("\n") for _, line in md.lines_outside_fences(text)]
        assert got == ["a", "b"]

    def test_line_numbers_count_fence_lines(self) -> None:
        text = "a\n```\nhidden\n```\nb\n"
        nums = [n for n, _ in md.lines_outside_fences(text)]
        assert nums == [1, 5]

    def test_tilde_fence(self) -> None:
        text = "a\n~~~\nhidden\n~~~\nb\n"
        got = [line.rstrip("\n") for _, line in md.lines_outside_fences(text)]
        assert got == ["a", "b"]

    def test_longer_fence_wraps_shorter_fenced_content(self) -> None:
        # A four-backtick fence exists to wrap content that carries its own
        # triple-backtick fences — the form issue-authoring.md mandates for
        # artifact blocks. The inner fence must not close the outer block.
        text = "a\n````\n```\nhidden\n```\n````\nb\n"
        got = [line.rstrip("\n") for _, line in md.lines_outside_fences(text)]
        assert got == ["a", "b"]

    def test_other_fence_character_does_not_close_a_block(self) -> None:
        # A tilde run inside a backtick block is content, not a delimiter.
        text = "a\n```\n~~~\nhidden\n~~~\n```\nb\n"
        got = [line.rstrip("\n") for _, line in md.lines_outside_fences(text)]
        assert got == ["a", "b"]

    def test_fence_carrying_an_info_string_does_not_close_a_block(self) -> None:
        # A closing fence carries no info string, so a same-length run that
        # names a language is content — the form a quoted example takes.
        text = "a\n```markdown\n```python\nhidden\n```\nb\n"
        got = [line.rstrip("\n") for _, line in md.lines_outside_fences(text)]
        assert got == ["a", "b"]

    def test_a_longer_run_closes_a_shorter_block(self) -> None:
        # The closing rule is "at least as long as the opener", not "equal":
        # a four-backtick run legally ends a three-backtick block, so the
        # block must not run on to the end of the text.
        text = "a\n```\ninner\n````\nb\n"
        got = [line.rstrip("\n") for _, line in md.lines_outside_fences(text)]
        assert got == ["a", "b"]

    def test_tilde_fences_nest_by_length(self) -> None:
        # The nesting rule is the fence character's, not the backtick's: a
        # four-tilde block wraps three-tilde content the same way.
        text = "a\n~~~~\n~~~\nhidden\n~~~\n~~~~\nb\n"
        got = [line.rstrip("\n") for _, line in md.lines_outside_fences(text)]
        assert got == ["a", "b"]

    def test_a_run_indented_past_three_spaces_does_not_open_a_block(self) -> None:
        # CommonMark caps an opening fence at three spaces of indentation;
        # past that the backticks are literal text inside an indented code
        # block. An indented transcript carrying a stray backtick run must
        # stay content rather than opening a block that swallows the rest.
        text = "a\n    ```\nb\n"
        got = [line.rstrip("\n") for _, line in md.lines_outside_fences(text)]
        assert got == ["a", "    ```", "b"]

    def test_a_block_left_open_at_the_end_is_reported(self) -> None:
        # A closer carrying an info string does not close, so this block runs
        # to the end of the text and every line after it drops out of the
        # scanned view. That silence blinds every consumer for the rest of the
        # document, so the parser names the defect rather than truncating.
        text = "intro\n```markdown\ncode\n```markdown\nafter\ntail\n"

        with pytest.raises(md.UnclosedFence) as raised:
            list(md.lines_outside_fences(text))

        assert "line 2" in str(raised.value)


class TestContentLines:
    def test_an_open_block_is_reported_against_its_file(self, tmp_path: Path) -> None:
        # Reading from a file, the report names the file too: the consumers
        # scan whole checkouts, so the defect has to be locatable.
        path = tmp_path / "doc.md"
        path.write_text("intro\n```markdown\ncode\n```markdown\ntail\n")

        with pytest.raises(md.UnclosedFence) as raised:
            list(md.content_lines(path))

        assert f"{path}:2" in str(raised.value)


class TestMarkdownLinks:
    def test_extracts_text_and_target(self) -> None:
        assert md.markdown_links("see [Doc](/standards/doc.md) now") == [
            ("Doc", "/standards/doc.md")
        ]

    def test_multiple_links(self) -> None:
        line = "[a](/x.md) and [b](~/workspace/r/y.md#h)"
        assert md.markdown_links(line) == [
            ("a", "/x.md"),
            ("b", "~/workspace/r/y.md#h"),
        ]

    def test_link_inside_inline_code_is_skipped(self) -> None:
        assert md.markdown_links("`[x](/y.md)`") == []

    def test_backticked_link_text_survives_as_target(self) -> None:
        # `[`code`](/target)` -> the link text is inline code; target survives.
        assert md.markdown_links("[`code`](/t.md)") == [("", "/t.md")]

    def test_double_backtick_span_is_stripped_whole(self) -> None:
        # A CommonMark code span of arbitrary delimiter length: a double-backtick
        # span is stripped as one unit, so link syntax inside it is not extracted
        # as a phantom link. Only the real link outside the span survives.
        assert md.markdown_links("``[x](/y.md)`` and [real](/r.md)") == [
            ("real", "/r.md")
        ]


class TestParseFrontmatter:
    def test_reads_mapping_and_body(self) -> None:
        fm, body = md.parse_frontmatter("---\ntype: README\n---\n# Title\n")
        assert fm == {"type": "README"}
        assert body == "# Title\n"

    def test_no_frontmatter(self) -> None:
        fm, body = md.parse_frontmatter("# Title\n")
        assert fm is None
        assert body == "# Title\n"

    def test_non_mapping_frontmatter_is_none(self) -> None:
        fm, _ = md.parse_frontmatter("---\n- a\n- b\n---\nbody\n")
        assert fm is None


class TestClassify:
    @pytest.mark.parametrize(
        "relpath, kind",
        [
            ("PLAN.md", "excluded"),
            ("PROGRESS.md", "excluded"),
            ("tmp/SCRATCH.md", "excluded"),
            ("dotfiles/.agents/skills/x/SKILL.md", "excluded"),
            ("index.md", "index"),
            ("standards/index.md", "index"),
            ("README.md", "concept"),
            ("standards/prose/conventions.md", "concept"),
            ("CONTEXT.md", "concept"),
            ("docs/decisions/0001-x.md", "concept"),
            ("harness-recipes/recipes/ralph-loop.md", "concept"),
            ("docs/sandboxing.md", "concept"),
            ("CLAUDE.md", "harness"),
            ("dotfiles/dot-claude/CLAUDE.md", "harness"),
            ("dotfiles/dot-claude/skills/commit/SKILL.md", "harness"),
            ("dotfiles/dot-claude/rules/bash-commands.md", "harness"),
            ("dotfiles/dot-claude/agents/build.md", "harness"),
            ("dotfiles/dot-claude/skills/prototype/references/logic.md", "harness"),
            (".pre-commit-config.yaml", "harness"),
            ("tools/bin/ref-lint", "harness"),
            ("tests/x.md", "harness"),
            ("tests/fixtures/specs/feat-01.md", "harness"),
            ("tests/spec_files/broken.md", "harness"),
            ("tests/anything/index.md", "harness"),
            ("specs/feat-01.md", "concept"),
            ("specs/index.md", "index"),
        ],
    )
    def test_classify(self, relpath: str, kind: str) -> None:
        assert md.classify(relpath) == kind


class TestHeadingSlugs:
    def test_collects_all_levels_skips_fenced(self, tmp_path: Path) -> None:
        f = tmp_path / "t.md"
        f.write_text("# Top\n## Mid\n```\n## Fake\n```\n### Deep\n")
        assert md.heading_slugs(f) == frozenset({"top", "mid", "deep"})


class TestFindMdFiles:
    def test_ambient_git_dir_does_not_redirect_discovery(
        self, tmp_path: Path, ambient_git_dir: Callable[[str], Path]
    ) -> None:
        target = tmp_path / "target"
        init_repo(target)
        (target / "real.md").write_text("# belongs to the target\n")
        (target / ".gitignore").write_text("leaked.md\n")
        (target / "leaked.md").write_text("# the target ignores its own copy\n")
        ambient_git_dir("leaked.md")

        assert md.find_md_files(target) == [target / "real.md"]
