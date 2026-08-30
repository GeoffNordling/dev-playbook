"""Behavioral tests for dev_playbook.filegraph — assert on the built graph.

Each test stands up a throwaway git repo (files are left untracked;
``gitrepo.git_files`` lists untracked files via ``--others``) and asserts
on the document ``build_graph`` returns: node buckets, edge records, the
ignored census, and the query results. The taxonomy under test is the
file-graph instrument spec (instruments/file-graph.md).
"""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from dev_playbook.filegraph import graph


def graph_repo(tmp_path: Path, files: dict[str, str]) -> Path:
    """Write a {relpath: contents} map into a fresh git repo named 'repo'."""
    repo = tmp_path / "repo"
    subprocess.run(
        ["git", "init", "-q", "-b", "main", str(repo)],
        check=True,
        capture_output=True,
    )
    for relpath, contents in files.items():
        path = repo / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents)
    return repo


def edge(doc: dict, form: str) -> dict:
    """The single edge of the given form; fails the test when not exactly one."""
    matches: list[dict] = [e for e in doc["edges"] if e["form"] == form]
    assert len(matches) == 1, f"expected one {form} edge, got {matches}"
    return matches[0]


def test_every_file_gets_exactly_one_bucket(tmp_path: Path) -> None:
    repo = graph_repo(
        tmp_path,
        {
            "CLAUDE.md": "hello",
            "index.md": "# index",
            "docs/guide.md": "---\ntype: Guide\n---\nbody",
            "src/app.py": "print(1)",
            "settings.json": "{}",
            "mystery.xyz": "?",
        },
    )

    doc = graph.build_graph(repo)

    assert doc["nodes"] == {
        "CLAUDE.md": "harness-session",
        "index.md": "index",
        "docs/guide.md": "concept",
        "src/app.py": "code",
        "settings.json": "config",
        "mystery.xyz": "unclassified",
    }
    assert doc["queries"]["census"]["nodes_by_bucket"]["unclassified"] == 1


def test_readings_artifacts_bucket_as_reading_not_config_or_code(
    tmp_path: Path,
) -> None:
    # Instrument outputs under readings/ are their own bucket, tested ahead of
    # the suffix rules that would otherwise claim .html/.json as config — the
    # misbucket the reading bucket exists to fix.
    repo = graph_repo(
        tmp_path,
        {
            "readings/datasheet/x.html": "<html></html>",
            "readings/file-graph/dev-playbook.json": "{}",
        },
    )

    doc = graph.build_graph(repo)

    assert doc["nodes"] == {
        "readings/datasheet/x.html": "reading",
        "readings/file-graph/dev-playbook.json": "reading",
    }


def test_skill_bundle_members_bucket_as_harness_skill(tmp_path: Path) -> None:
    repo = graph_repo(
        tmp_path,
        {"dotfiles/dot-claude/skills/fmt/SKILL.md": "a skill"},
    )

    doc = graph.build_graph(repo)

    assert doc["nodes"]["dotfiles/dot-claude/skills/fmt/SKILL.md"] == "harness-skill"


def test_gitignored_files_counted_per_pattern_not_as_nodes(
    tmp_path: Path,
) -> None:
    repo = graph_repo(
        tmp_path,
        {
            ".gitignore": "*.pyc\n.venv/\n",
            "a.pyc": "",
            "b.pyc": "",
            ".venv/lib.py": "",
        },
    )

    doc = graph.build_graph(repo)

    assert set(doc["nodes"]) == {".gitignore"}
    assert doc["ignored"][".gitignore:*.pyc"] == 2
    assert doc["ignored"][".gitignore:.venv/"] == 1


def test_root_absolute_link_is_an_ok_link_edge(tmp_path: Path) -> None:
    repo = graph_repo(
        tmp_path,
        {
            "a.md": "see [b](/docs/b.md)",
            "docs/b.md": "target",
        },
    )

    doc = graph.build_graph(repo)

    assert edge(doc, "link") == {
        "source": "a.md",
        "target": "docs/b.md",
        "kind": "internal",
        "form": "link",
        "line": 1,
        "status": "ok",
    }


def test_link_to_missing_file_lands_in_defects(tmp_path: Path) -> None:
    repo = graph_repo(tmp_path, {"a.md": "see [gone](/docs/gone.md)"})

    doc = graph.build_graph(repo)

    assert doc["queries"]["defects"] == [
        {
            "source": "a.md",
            "target": "docs/gone.md",
            "kind": "internal",
            "form": "link",
            "line": 1,
            "status": "broken",
        }
    ]


def test_same_repo_citation_from_fixed_root_source_is_wrong_form(
    tmp_path: Path,
) -> None:
    repo = graph_repo(
        tmp_path,
        {
            "a.md": "see [b](~/workspace/repo/b.md)",
            "b.md": "target",
        },
    )

    doc = graph.build_graph(repo)

    assert edge(doc, "citation")["status"] == "wrong-form"


def test_same_repo_citation_from_skill_is_ok(tmp_path: Path) -> None:
    repo = graph_repo(
        tmp_path,
        {
            "skills/fmt/SKILL.md": "see ~/workspace/repo/b.md",
            "b.md": "target",
        },
    )

    doc = graph.build_graph(repo)

    assert edge(doc, "citation") == {
        "source": "skills/fmt/SKILL.md",
        "target": "b.md",
        "kind": "internal",
        "form": "citation",
        "line": 1,
        "status": "ok",
    }


def test_same_repo_citation_from_agent_definition_is_ok(tmp_path: Path) -> None:
    """An agent definition stows into ~/.claude/agents/, so it has no fixed
    repo root and a same-repo Citation is the correct form."""
    repo = graph_repo(
        tmp_path,
        {
            "agents/build.md": "see ~/workspace/repo/b.md",
            "b.md": "target",
        },
    )

    doc = graph.build_graph(repo)

    assert edge(doc, "citation")["status"] == "ok"


def test_cross_repo_citation_is_an_external_edge(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    other = tmp_path / "workspace" / "other" / "README.md"
    other.parent.mkdir(parents=True)
    other.write_text("elsewhere")
    repo = graph_repo(
        tmp_path,
        {
            "a.md": "see [it](~/workspace/other/README.md)",
        },
    )

    doc = graph.build_graph(repo)

    assert edge(doc, "citation") == {
        "source": "a.md",
        "target": "~/workspace/other/README.md",
        "kind": "external",
        "form": "citation",
        "line": 1,
        "status": "ok",
    }


def test_backticked_path_is_a_prose_path_edge(tmp_path: Path) -> None:
    repo = graph_repo(
        tmp_path,
        {
            "CLAUDE.md": "Read `~/workspace/repo/docs/b.md` now.",
            "docs/b.md": "target",
        },
    )

    doc = graph.build_graph(repo)

    assert edge(doc, "prose-path") == {
        "source": "CLAUDE.md",
        "target": "docs/b.md",
        "kind": "internal",
        "form": "prose-path",
        "line": 1,
        "status": "ok",
    }


def test_prose_path_deduplicates_against_grammar_edges(tmp_path: Path) -> None:
    repo = graph_repo(
        tmp_path,
        {
            "a.md": "[b](/docs/b.md) and also /docs/b.md in prose",
            "docs/b.md": "target",
        },
    )

    doc = graph.build_graph(repo)

    assert [e["form"] for e in doc["edges"]] == ["link"]


def test_code_path_token_resolving_in_repo_is_a_code_ref(
    tmp_path: Path,
) -> None:
    repo = graph_repo(
        tmp_path,
        {
            "tool.py": "# reads /docs/b.md at startup\n",
            "docs/b.md": "target",
        },
    )

    doc = graph.build_graph(repo)

    assert edge(doc, "code-ref") == {
        "source": "tool.py",
        "target": "docs/b.md",
        "kind": "internal",
        "form": "code-ref",
        "line": 1,
        "status": "ok",
    }


def test_code_path_token_with_no_target_is_not_an_edge(tmp_path: Path) -> None:
    repo = graph_repo(tmp_path, {"tool.py": "# see /docs/gone.md\n"})

    doc = graph.build_graph(repo)

    assert doc["edges"] == []


def test_skill_bundle_members_attach_to_their_skill_md(tmp_path: Path) -> None:
    repo = graph_repo(
        tmp_path,
        {
            "skills/fmt/SKILL.md": "the skill",
            "skills/fmt/references/notes.md": "depth",
            "skills/fmt/scripts/run.py": "print(1)",
            "skills/other/SKILL.md": "unrelated",
        },
    )

    doc = graph.build_graph(repo)

    bundle = sorted(
        (e["source"], e["target"]) for e in doc["edges"] if e["form"] == "bundle"
    )
    assert bundle == [
        ("skills/fmt/SKILL.md", "skills/fmt/references/notes.md"),
        ("skills/fmt/SKILL.md", "skills/fmt/scripts/run.py"),
    ]


def test_reachability_walks_from_harness_session_with_distances(
    tmp_path: Path,
) -> None:
    repo = graph_repo(
        tmp_path,
        {
            "CLAUDE.md": "start at [a](/a.md)",
            "a.md": "then [b](/b.md)",
            "b.md": "the end",
            "island.md": "never linked",
        },
    )

    doc = graph.build_graph(repo)

    reach = doc["queries"]["reachability"]
    assert reach["seeds"] == ["CLAUDE.md"]
    assert reach["reached"] == {"CLAUDE.md": 0, "a.md": 1, "b.md": 2}
    assert reach["unreached"] == ["island.md"]


def test_fragmented_concept_docs_split_into_components(tmp_path: Path) -> None:
    repo = graph_repo(
        tmp_path,
        {
            "index.md": "- [a](/a.md)",
            "a.md": "---\ntype: Guide\n---\nlinked",
            "b.md": "---\ntype: Guide\n---\nnot linked",
        },
    )

    doc = graph.build_graph(repo)

    assert doc["queries"]["components"] == [["a.md", "index.md"], ["b.md"]]


def test_files_with_no_edges_are_orphans_by_bucket(tmp_path: Path) -> None:
    repo = graph_repo(
        tmp_path,
        {
            "a.md": "see [b](/b.md)",
            "b.md": "target",
            "lonely.py": "print(1)",
        },
    )

    doc = graph.build_graph(repo)

    assert doc["queries"]["orphans"] == {"lonely.py": "code"}


def test_frontmatter_resource_is_not_also_a_phantom_citation(
    tmp_path: Path,
) -> None:
    repo = graph_repo(
        tmp_path,
        {
            "a.md": "---\nresource: ~/workspace/repo/b.md\n---\nbody\n",
            "b.md": "target",
        },
    )

    doc = graph.build_graph(repo)

    # The resource declaration is one edge, not a resource edge plus a phantom
    # ``wrong-form`` citation re-scanned out of the YAML frontmatter.
    assert [e["form"] for e in doc["edges"]] == ["resource"]
    assert edge(doc, "resource") == {
        "source": "a.md",
        "target": "b.md",
        "kind": "internal",
        "form": "resource",
        "line": 0,
        "status": "ok",
    }
    assert doc["queries"]["defects"] == []


def test_executable_bit_only_buckets_extensionless_files_as_code(
    tmp_path: Path,
) -> None:
    repo = graph_repo(
        tmp_path,
        {
            "deploy.yaml": "steps: []\n",  # +x with a config extension stays config
            "hook": "#!/bin/sh\necho hi\n",  # +x extensionless is a script entry point
        },
    )
    (repo / "deploy.yaml").chmod(0o755)
    (repo / "hook").chmod(0o755)

    doc = graph.build_graph(repo)

    assert doc["nodes"]["deploy.yaml"] == "config"
    assert doc["nodes"]["hook"] == "code"


def test_nested_bundle_files_attach_only_to_the_nearest_skill(
    tmp_path: Path,
) -> None:
    repo = graph_repo(
        tmp_path,
        {
            "skills/a/SKILL.md": "outer",
            "skills/a/notes.md": "outer's own file",
            "skills/a/b/SKILL.md": "inner",
            "skills/a/b/deep.md": "inner's file",
        },
    )

    doc = graph.build_graph(repo)

    bundle = sorted(
        (e["source"], e["target"]) for e in doc["edges"] if e["form"] == "bundle"
    )
    # deep.md attaches only to the inner SKILL.md, never doubly to the outer.
    assert bundle == [
        ("skills/a/SKILL.md", "skills/a/b/SKILL.md"),
        ("skills/a/SKILL.md", "skills/a/notes.md"),
        ("skills/a/b/SKILL.md", "skills/a/b/deep.md"),
    ]


def test_compute_queries_matches_build_graph_queries(tmp_path: Path) -> None:
    repo = graph_repo(
        tmp_path,
        {
            "CLAUDE.md": "start at [a](/a.md)",
            "a.md": "then [b](/b.md)",
            "b.md": "the end",
        },
    )

    doc = graph.build_graph(repo)
    seeds = sorted(r for r, b in doc["nodes"].items() if b == "harness-session")

    # build_graph assembles its queries through this helper, so the shapes
    # cannot drift: the same (nodes, edges, seeds) reproduce build_graph's
    # queries.
    assert graph.compute_queries(doc["nodes"], doc["edges"], seeds) == doc["queries"]


def test_ambient_git_dir_does_not_redirect_ignored_census(
    tmp_path: Path, ambient_git_dir: Callable[[str], Path]
) -> None:
    repo = graph_repo(
        tmp_path,
        {".gitignore": "*.pyc\n", "a.pyc": "", "b.pyc": ""},
    )
    ambient_git_dir("a.pyc")

    assert graph.ignored_census(repo) == {".gitignore:*.pyc": 2}
