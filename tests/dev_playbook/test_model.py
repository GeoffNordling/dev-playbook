"""Unit tests for the repo model, src/dev_playbook/model.py."""

import os
import subprocess
from pathlib import Path

import pytest
from conftest import commit_all, init_repo

from dev_playbook import sources
from dev_playbook.model import (
    ModelError,
    Repo,
    parse_markdown,
    parse_python,
    shipped_canonical,
)

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

    def test_frontmatter_that_is_yaml_but_not_a_mapping_names_the_file(
        self,
    ) -> None:
        with pytest.raises(ModelError, match="x.md: frontmatter is not a mapping"):
            parse_markdown("x.md", "---\n- a\n---\n")

    def test_link_text_wraps_across_several_breaks_not_a_blank_line(self) -> None:
        text = "A [one\ntwo\nthree](/a.md) and [x\n\ny](/b.md)\n"
        got = [(k.text, k.target, k.line) for k in parse_markdown("l.md", text).links]
        assert got == [("one\ntwo\nthree", "/a.md", 1)]

    def test_bare_path_in_a_links_text_is_read(self) -> None:
        doc = parse_markdown(
            "d.md", "See [~/workspace/o/a.md](/x.md) and ~/workspace/o/b.md\n"
        )
        got = [(b.target, b.line, b.in_link) for b in doc.bare_paths]
        assert got == [
            ("~/workspace/o/a.md", 1, True),
            ("~/workspace/o/b.md", 1, False),
        ]

    def test_bare_path_drops_a_trailing_sentence_mark(self) -> None:
        doc = parse_markdown(
            "d.md", "Read ~/workspace/demo/a.md. Then ~/workspace/d/b;\n"
        )
        assert [b.target for b in doc.bare_paths] == [
            "~/workspace/demo/a.md",
            "~/workspace/d/b",
        ]

    def test_bare_path_drops_one_trailing_mark_at_most(self) -> None:
        doc = parse_markdown("d.md", "See ~/workspace/demo/x/..\n")
        assert [b.target for b in doc.bare_paths] == ["~/workspace/demo/x/."]

    def test_bare_path_skips_code(self) -> None:
        doc = parse_markdown(
            "d.md", "Text.\n\n    ~/workspace/o/a.md\n\n`~/workspace/o/b.md`\n"
        )
        assert doc.bare_paths == ()

    def test_list_continuation_is_not_indented_code(self) -> None:
        text = "1. Item.\n\n    More [a](/a.md).\n\n       code\n\nText.\n\n    code\n"
        assert parse_markdown("d.md", text).indented_code == frozenset({5, 9})


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

    def test_name_defaults_to_the_root_directory(self, tmp_path: Path) -> None:
        root = tmp_path / "My-Repo"
        assert Repo.from_files(root, {}).name == "My-Repo"
        assert Repo.from_files(root, {}, name="other").name == "other"

    def test_canonical_defaults_to_the_shipped_copy(self, tmp_path: Path) -> None:
        repo = Repo.from_files(tmp_path, {})
        assert set(repo.canonical) == sources.CANONICAL_FILES
        assert repo.canonical == shipped_canonical()
        pinned = Repo.from_files(tmp_path, {}, canonical={"ci.yml": b"x\n"})
        assert pinned.canonical == {"ci.yml": b"x\n"}

    def test_is_dev_playbook_where_the_canonical_directory_is_tracked(
        self, tmp_path: Path
    ) -> None:
        canonical = f"{sources.CANONICAL_DIR}/.gitignore"
        assert Repo.from_files(tmp_path, {canonical: b"x\n"}).is_dev_playbook
        assert not Repo.from_files(tmp_path, {"a.md": b"# A\n"}).is_dev_playbook

    def test_slugs_on_disk_are_held_for_one_model(self, tmp_path: Path) -> None:
        target = tmp_path / "t.md"
        target.write_text("# One\n")
        first = Repo.from_files(tmp_path, {})
        assert first.slugs_on_disk(str(target)) == frozenset({"one"})
        target.write_text("# Two\n")
        assert first.slugs_on_disk(str(target)) == frozenset({"one"})
        second = Repo.from_files(tmp_path, {})
        assert second.slugs_on_disk(str(target)) == frozenset({"two"})

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
        assert repo.canonical == shipped_canonical()

    def test_name_is_the_repository_from_a_worktree(self, tmp_path: Path) -> None:
        root = tmp_path / "My-Repo"
        init_repo(root)
        (root / "doc.md").write_text("# Doc\n")
        commit_all(root)
        worktree = tmp_path / "elsewhere"
        subprocess.run(
            ["git", "-C", str(root), "worktree", "add", "-q", str(worktree)],
            check=True,
            capture_output=True,
        )
        assert Repo.from_git(root).name == "My-Repo"
        assert Repo.from_git(worktree).name == "My-Repo"

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
