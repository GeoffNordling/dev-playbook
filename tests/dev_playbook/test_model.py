"""Unit tests for the repo model, src/dev_playbook/model.py."""

import os
from pathlib import Path

import pytest
from conftest import commit_all, init_repo

from dev_playbook.model import ModelError, Repo, parse_markdown, parse_python

DOC = """---
type: Standard
title: T
---

# Title

Intro with a [link](/a.md) and `[not](a-link)`.

## Rule one

Body.

`fam.rule-one` · deterministic

```
# not a heading
[nor](a-link)
```

## Rule two

A [wrapped
link](/b.md#x) here.

`fam.rule-two` · stochastic
"""


class TestParseMarkdown:
    def test_frontmatter_is_the_mapping(self) -> None:
        assert parse_markdown("d.md", DOC).frontmatter == {
            "type": "Standard",
            "title": "T",
        }

    def test_headings_carry_level_slug_and_line(self) -> None:
        got = [(h.level, h.slug, h.line) for h in parse_markdown("d.md", DOC).headings]
        assert got == [(1, "title", 6), (2, "rule-one", 10), (2, "rule-two", 21)]

    def test_trailers_carry_kind_line_and_heading(self) -> None:
        got = [
            (t.id, t.kind, t.line, t.heading.slug if t.heading else None)
            for t in parse_markdown("d.md", DOC).trailers
        ]
        assert got == [
            ("fam.rule-one", "deterministic", 14, "rule-one"),
            ("fam.rule-two", "stochastic", 26, "rule-two"),
        ]

    def test_links_skip_code_and_find_wrapped_text(self) -> None:
        got = [
            (link.text, link.target, link.line)
            for link in parse_markdown("d.md", DOC).links
        ]
        assert got == [("link", "/a.md", 8), ("wrapped\nlink", "/b.md#x", 23)]

    def test_content_leaves_out_frontmatter_and_fences(self) -> None:
        numbers = [n for n, _ in parse_markdown("d.md", DOC).content]
        assert numbers[0] == 5
        assert 17 not in numbers
        assert 18 not in numbers

    def test_section_runs_to_the_next_heading_of_the_same_level(self) -> None:
        doc = parse_markdown("d.md", DOC)
        assert [n for n, _ in doc.section("rule-one")] == [11, 12, 13, 14, 15, 20]
        assert [n for n, _ in doc.section("rule-two")] == [22, 23, 24, 25, 26]
        with pytest.raises(KeyError):
            doc.section("nope")

    def test_no_frontmatter(self) -> None:
        doc = parse_markdown("x.md", "# A\n")
        assert doc.frontmatter is None
        assert doc.headings[0].line == 1

    def test_unclosed_fence_names_the_file(self) -> None:
        with pytest.raises(ModelError, match="x.md: unclosed"):
            parse_markdown("x.md", "a\n```\nb\n")

    def test_frontmatter_that_is_not_yaml_names_the_file(self) -> None:
        with pytest.raises(ModelError, match="x.md: frontmatter is not YAML"):
            parse_markdown("x.md", "---\na: [\n---\nbody\n")

    def test_frontmatter_that_is_not_a_mapping_names_the_file(self) -> None:
        with pytest.raises(ModelError, match="x.md: frontmatter is not a mapping"):
            parse_markdown("x.md", "---\n- item\n---\nbody\n")


class TestParsePython:
    def test_tree_for_valid_source(self) -> None:
        assert parse_python("a.py", "x = 1\n").tree is not None

    def test_syntax_error_is_recorded_not_raised(self) -> None:
        got = parse_python("a.py", "def (\n")
        assert got.tree is None
        assert got.error is not None


class TestRepoFromFiles:
    def test_sorts_files_and_parses_by_kind(self, tmp_path: Path) -> None:
        repo = Repo.from_files(
            tmp_path,
            {
                "b.md": b"# B\n",
                "a.py": b"x = 1\n",
                "scripts/tool": b"#!/usr/bin/env python3\nprint()\n",
                "Makefile": b"all:\n",
            },
            executable=["scripts/tool"],
        )
        assert repo.files == ("Makefile", "a.py", "b.md", "scripts/tool")
        assert set(repo.markdown) == {"b.md"}
        assert set(repo.python) == {"a.py", "scripts/tool"}
        assert repo.executable == frozenset({"scripts/tool"})
        assert repo.text("Makefile") == "all:\n"

    def test_non_utf8_markdown_names_the_file(self, tmp_path: Path) -> None:
        with pytest.raises(ModelError, match="b.md: not UTF-8"):
            Repo.from_files(tmp_path, {"b.md": b"\xff\xfe"})


class TestRepoFromGit:
    def test_tracked_files_only_with_modes(self, tmp_path: Path) -> None:
        root = tmp_path / "repo"
        init_repo(root)
        (root / "doc.md").write_text("# Doc\n")
        (root / "run").write_text("#!/usr/bin/env bash\n")
        (root / "run").chmod(0o755)
        commit_all(root)
        (root / "untracked.md").write_text("# No\n")
        repo = Repo.from_git(root)
        assert repo.files == ("doc.md", "run")
        assert repo.executable == frozenset({"run"})
        assert repo.markdown["doc.md"].headings[0].slug == "doc"

    def test_tracked_file_deleted_from_the_working_tree_is_skipped(
        self, tmp_path: Path
    ) -> None:
        root = tmp_path / "repo"
        init_repo(root)
        (root / "keep.md").write_text("# K\n")
        (root / "gone.md").write_text("# G\n")
        commit_all(root)
        os.remove(root / "gone.md")
        assert Repo.from_git(root).files == ("keep.md",)
