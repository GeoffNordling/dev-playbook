"""Unit tests for the shared markdown library, src/dev_playbook/md.py."""

from pathlib import Path

import pytest

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
            ("dotfiles/.dhub/whatever.md", "excluded"),
            ("index.md", "index"),
            ("standards/index.md", "index"),
            ("README.md", "concept"),
            ("standards/prose/conventions.md", "concept"),
            ("CONTEXT.md", "concept"),
            ("docs/adr/0001-x.md", "concept"),
            ("harness-recipes/recipes/ralph-loop.md", "concept"),
            ("protocols/align-map-execute/formulation.md", "concept"),
            ("CLAUDE.md", "harness"),
            ("dotfiles/dot-claude/CLAUDE.md", "harness"),
            ("protocols/align-map-execute/SKILL.md", "harness"),
            ("dotfiles/dot-claude/rules/bash-commands.md", "harness"),
            ("dotfiles/dot-claude/skills/prototype/references/logic.md", "harness"),
            (
                "standards/agentic-box/templates/greenfield-cli/box/contract.md",
                "concept",
            ),
            ("standards/agentic-box/templates/greenfield-cli/box/README.md", "concept"),
            ("standards/agentic-box/templates/greenfield-cli/index.md", "index"),
            (".pre-commit-config.yaml", "harness"),
            ("tools/bin/ref-audit", "harness"),
        ],
    )
    def test_classify(self, relpath: str, kind: str) -> None:
        assert md.classify(relpath) == kind


class TestHeadingSlugs:
    def test_collects_all_levels_skips_fenced(self, tmp_path: Path) -> None:
        f = tmp_path / "t.md"
        f.write_text("# Top\n## Mid\n```\n## Fake\n```\n### Deep\n")
        assert md.heading_slugs(f) == frozenset({"top", "mid", "deep"})
