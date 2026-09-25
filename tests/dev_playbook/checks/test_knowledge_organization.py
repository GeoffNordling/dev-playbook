"""Unit tests for the knowledge-organization family's checks."""

from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

from dev_playbook.check_registry import Finding
from dev_playbook.checks.knowledge_organization import (
    add_never_shadow,
    alphabetical_unless_declared_otherwise,
    an_index_in_every_directory,
    atx_headings_only,
    every_file_reached_from_its_head_file,
    fragment_anchor_matches_the_slug,
    frontmatter_a_yaml_mapping,
    frontmatter_declares_type_vocabulary,
    guide_lives_under_guides,
    headings_slugify_distinctly,
    introduction_between_h1_and_listing,
    language_section_present,
    loop_lives_under_loops,
    no_okf_type,
    non_empty_description_no_closing_period,
    non_empty_title,
    okf_type_name_to_description,
    okf_version_declared,
    one_directory_under_workstreams,
    one_entry_per_concept_document_and_child_directory,
    readme_holds_an_h1,
    readmemd_is_typed_readme,
    recipe_description_carries_a_resource,
    reference_resolves,
    registry_lives_under_registries,
    relative_path_inside_the_bundle,
    resource_a_repo_root_path_or_a_uri,
    root_absolute_path_in_the_same_repo,
    rows_in_alphabetical_order,
    stable_named_anchor,
    standard_lives_under_standards,
    term_definition_avoid_line,
    the_worklist_in_the_head_file_only,
    type_is_a_registered_okf_type,
    workspace_path_for_a_stable_location,
    workspace_path_for_another_repo,
    workstreams_holds_only_workstreams,
)
from dev_playbook.model import Repo

SKILL = "dotfiles/dot-claude/skills/demo"
CLAUDE_RULE = "dotfiles/dot-claude/rules/r.md"
CANONICAL = "standards/build/canonical/.gitignore"


def found(
    check: Callable[[Repo], Iterator[Finding]], contents: dict[str, str]
) -> list[tuple[str, int | None]]:
    encoded = {path: text.encode() for path, text in contents.items()}
    repo = Repo.from_files(Path("/r"), encoded, name="demo")
    pairs = [(f.path, f.line) for f in check(repo)]
    return sorted(pairs, key=lambda pair: (pair[0], pair[1] or 0))


def doc(front: str, body: str = "# Doc\n") -> str:
    return f"---\n{front}---\n\n{body}"


def concept(doc_type: str = "General-Sheet", extra: str = "") -> str:
    return doc(f"type: {doc_type}\ntitle: A\ndescription: One doc\n{extra}")


def context(
    body: str, front: str = "type: Vocabulary\ntitle: C\ndescription: D\n"
) -> str:
    return doc(front, "# C\n\n" + body)


# --- context-content.md ---


def test_frontmatter_declares_type_vocabulary() -> None:
    assert (
        found(frontmatter_declares_type_vocabulary, {"CONTEXT.md": context("")}) == []
    )
    wrong = context("", "type: General-Sheet\ntitle: C\ndescription: D\n")
    assert found(frontmatter_declares_type_vocabulary, {"CONTEXT.md": wrong}) == [
        ("CONTEXT.md", None)
    ]


def test_language_section_present() -> None:
    assert (
        found(language_section_present, {"CONTEXT.md": context("## Language\n")}) == []
    )
    assert found(language_section_present, {"CONTEXT.md": context("## Terms\n")}) == [
        ("CONTEXT.md", None)
    ]


def test_term_definition_avoid_line() -> None:
    good = (
        "## Language\n\n### Group\n\nIntro to the group.\n\n"
        "**Order**\nA thing ordered.\n_Avoid_: Purchase\n"
    )
    assert found(term_definition_avoid_line, {"CONTEXT.md": context(good)}) == []
    bad = (
        "## Language\n\n"
        "**Order** is a thing\nA thing.\n\n"
        "**Bill**\n_Avoid_: X\nA definition after.\n\n"
        "A stray line.\n_Avoid_: Y\n"
    )
    assert found(term_definition_avoid_line, {"CONTEXT.md": context(bad)}) == [
        ("CONTEXT.md", 11),
        ("CONTEXT.md", 15),
        ("CONTEXT.md", 19),
    ]


def test_term_definition_avoid_line_counts_definitions_and_avoid_lines() -> None:
    bad = "## Language\n\n**Order**\n_Avoid_: X\n\n**Bill**\nA bill.\n_Avoid_: Y\n_Avoid_: Z\n"
    assert found(term_definition_avoid_line, {"CONTEXT.md": context(bad)}) == [
        ("CONTEXT.md", 11),
        ("CONTEXT.md", 17),
    ]


def test_term_definition_avoid_line_reads_the_h2_not_an_h1_of_its_slug() -> None:
    body = "# Language\n\n**Loose** words\n\n## Language\n\n**Order**\nA thing.\n"
    assert (
        found(
            term_definition_avoid_line, {"CONTEXT.md": doc("type: Vocabulary\n", body)}
        )
        == []
    )


# --- cross-references.md ---


def test_reference_resolves(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / "workspace" / "other").mkdir(parents=True)
    (tmp_path / "workspace" / "other" / "a.md").write_text("# A\n")
    good = (
        "[a](/b.md) [dir](/sub/) [rel](sub/c.md) [self](~/workspace/demo/b.md)\n"
        "[other](~/workspace/other/a.md) [web](https://example.com)\n"
    )
    files = {"a.md": good, "b.md": "# B\n", "sub/c.md": "# C\n"}
    assert found(reference_resolves, files) == []
    bad = "[a](/gone.md)\n[b](gone.md)\n[c](~/workspace/other/gone.md)\n"
    assert found(reference_resolves, {"a.md": bad}) == [
        ("a.md", 1),
        ("a.md", 2),
        ("a.md", 3),
    ]


def test_reference_resolves_reads_claude_targets_where_tracked() -> None:
    link = "[r](~/.claude/rules/r.md)\n[g](~/.claude/rules/gone.md)\n"
    files = {"a.md": link, CLAUDE_RULE: "# R\n"}
    assert found(reference_resolves, files) == [("a.md", 2)]
    assert found(reference_resolves, {"a.md": link}) == []


def test_reference_resolves_skips_a_numbered_decision_record() -> None:
    record = "docs/decisions/0001-a.md"
    assert found(reference_resolves, {record: "[a](/gone.md)\n"}) == []


def test_fragment_anchor_matches_the_slug(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / "workspace" / "other").mkdir(parents=True)
    (tmp_path / "workspace" / "other" / "a.md").write_text("# A\n\n## Far part\n")
    good = (
        "# Top\n\n[a](/b.md#the-part) [b](#top) [c](b.md#the-part)\n"
        "[d](~/workspace/other/a.md#far-part) [e](/dir#anything)\n"
    )
    files = {"a.md": good, "b.md": "# B\n\n## The part\n", "dir/x.md": "# X\n"}
    assert found(fragment_anchor_matches_the_slug, files) == []
    bad = "# Top\n\n[a](/b.md#nope)\n[b](#nope)\n[c](~/workspace/other/a.md#nope)\n"
    assert found(fragment_anchor_matches_the_slug, {"a.md": bad, "b.md": "# B\n"}) == [
        ("a.md", 3),
        ("a.md", 4),
        ("a.md", 5),
    ]


def test_fragment_anchor_matches_the_slug_reads_claude_targets() -> None:
    links = "[a](~/.claude/rules/r.md#part)\n[b](~/.claude/rules/r.md#nope)\n"
    files = {"a.md": links, CLAUDE_RULE: "# R\n\n## Part\n"}
    assert found(fragment_anchor_matches_the_slug, files) == [("a.md", 2)]


def test_headings_slugify_distinctly() -> None:
    assert found(headings_slugify_distinctly, {"a.md": "# A\n\n## B\n"}) == []
    assert found(headings_slugify_distinctly, {"a.md": "# A\n\n## B\n\n## `B`\n"}) == [
        ("a.md", 5)
    ]
    record = "docs/decisions/0001-a.md"
    assert found(headings_slugify_distinctly, {record: "# A\n\n# A\n"}) == []


def test_stable_named_anchor() -> None:
    target = "# T\n\n## 3. Bundle\n\n## Named\n"
    good = "[a](/t.md#named)\n"
    assert found(stable_named_anchor, {"a.md": good, "t.md": target}) == []
    bad = "[a](/t.md#3-bundle)\n"
    assert found(stable_named_anchor, {"a.md": bad, "t.md": target}) == [("a.md", 1)]


def test_stable_named_anchor_reads_the_form_of_any_md_target() -> None:
    good = "[a](~/workspace/other/t.md#named) [b](/dir#2-x) [c](#top)\n"
    assert found(stable_named_anchor, {"a.md": good}) == []
    bad = "[a](~/workspace/other/t.md#223-revision)\n[b](#3-bundle)\n"
    assert found(stable_named_anchor, {"a.md": bad}) == [("a.md", 1), ("a.md", 2)]


def test_workspace_path_for_another_repo() -> None:
    good = "[x](~/workspace/other/a.md)\n\n    ~/workspace/other/in-code.md\n"
    assert found(workspace_path_for_another_repo, {"a.md": good}) == []
    bad = "see ~/workspace/other/a.md here\n[x](../../outside.md)\n"
    assert found(workspace_path_for_another_repo, {"d/a.md": bad}) == [
        ("d/a.md", 1),
        ("d/a.md", 2),
    ]


def test_workspace_path_for_another_repo_accepts_a_path_in_link_text() -> None:
    good = "[~/workspace/other/a.md](~/workspace/other/a.md)\n"
    assert found(workspace_path_for_another_repo, {"a.md": good}) == []
    bad = "Read ~/workspace/other/a.md.\n"
    assert found(workspace_path_for_another_repo, {"a.md": bad}) == [("a.md", 1)]


def test_root_absolute_path_in_the_same_repo() -> None:
    good = "[a](/b.md) and [s](/dotfiles/x.md)\n"
    assert found(root_absolute_path_in_the_same_repo, {"d/a.md": good}) == []
    bad = "[a](~/workspace/demo/b.md)\n[b](b.md)\nbare ~/workspace/demo/b.md\n"
    assert found(root_absolute_path_in_the_same_repo, {"d/a.md": bad}) == [
        ("d/a.md", 1),
        ("d/a.md", 2),
        ("d/a.md", 3),
    ]
    rootless = f"{SKILL}/SKILL.md"
    assert found(root_absolute_path_in_the_same_repo, {rootless: bad}) == []


def test_root_absolute_path_in_the_same_repo_reads_link_text_and_passes_claude() -> (
    None
):
    good = "[r](~/.claude/rules/r.md)\n"
    assert found(root_absolute_path_in_the_same_repo, {"d/a.md": good}) == []
    bad = "[~/workspace/demo/b.md](/b.md)\n"
    assert found(root_absolute_path_in_the_same_repo, {"d/a.md": bad}) == [
        ("d/a.md", 1)
    ]


def test_workspace_path_for_a_stable_location() -> None:
    good = "[a](~/workspace/demo/README.md) [b](references/x.md)\n"
    assert (
        found(workspace_path_for_a_stable_location, {f"{SKILL}/SKILL.md": good}) == []
    )
    bad = "[a](/README.md)\n[b](../other/SKILL.md)\n"
    assert found(workspace_path_for_a_stable_location, {f"{SKILL}/SKILL.md": bad}) == [
        (f"{SKILL}/SKILL.md", 1),
        (f"{SKILL}/SKILL.md", 2),
    ]
    rule = "dotfiles/dot-claude/rules/r.md"
    assert found(workspace_path_for_a_stable_location, {rule: "[a](x.md)\n"}) == [
        (rule, 1)
    ]


def test_relative_path_inside_the_bundle() -> None:
    good = "[a](references/x.md) [b](~/workspace/demo/README.md)\n"
    assert found(relative_path_inside_the_bundle, {f"{SKILL}/SKILL.md": good}) == []
    bad = (
        f"[a](/{SKILL}/references/x.md)\n"
        f"[b](~/workspace/demo/{SKILL}/references/x.md)\n"
        "[c](~/.claude/skills/demo/references/x.md)\n"
    )
    assert found(relative_path_inside_the_bundle, {f"{SKILL}/SKILL.md": bad}) == [
        (f"{SKILL}/SKILL.md", 1),
        (f"{SKILL}/SKILL.md", 2),
        (f"{SKILL}/SKILL.md", 3),
    ]


def test_relative_path_inside_the_bundle_reads_claude_only_for_its_copy() -> None:
    link = "[c](~/.claude/skills/demo/references/x.md)\n"
    consumer = ".claude/skills/demo/SKILL.md"
    assert found(relative_path_inside_the_bundle, {consumer: link}) == []
    files = {f"{SKILL}/SKILL.md": link, f"{SKILL}/references/x.md": "# X\n"}
    assert found(relative_path_inside_the_bundle, files) == [(f"{SKILL}/SKILL.md", 1)]


# --- okf-frontmatter.md ---


def test_frontmatter_a_yaml_mapping() -> None:
    assert found(frontmatter_a_yaml_mapping, {"a.md": concept()}) == []
    assert found(
        frontmatter_a_yaml_mapping, {"a.md": "# A\n", "index.md": "# I\n"}
    ) == [("a.md", None)]


def test_atx_headings_only() -> None:
    assert found(atx_headings_only, {"a.md": "# A\n\nText\n---\n"}) == [("a.md", 4)]
    assert found(atx_headings_only, {"a.md": "# A\n\nText\n\n---\n"}) == []
    table = "# A\n\n| a | b |\n| --- | --- |\n| 1 | 2 |\n"
    assert found(atx_headings_only, {"a.md": table}) == []
    record = {"docs/decisions/0001-x.md": "# A\n\nText\n---\n"}
    assert found(atx_headings_only, record) == []


def test_type_is_a_registered_okf_type_reports_a_list_type() -> None:
    files = {"a.md": concept("[Guide, Standard]"), "b.md": concept("Guide")}
    assert found(type_is_a_registered_okf_type, files) == [("a.md", None)]


def test_type_is_a_registered_okf_type() -> None:
    assert found(type_is_a_registered_okf_type, {"a.md": concept("Guide")}) == []
    files = {"a.md": concept("Bogus"), "b.md": doc("title: B\ndescription: D\n")}
    assert found(type_is_a_registered_okf_type, files) == [
        ("a.md", None),
        ("b.md", None),
    ]


def test_type_is_a_registered_okf_type_reads_local_types() -> None:
    files = local("| `Resume` | A resume |\n") | {"a.md": concept("Resume")}
    assert found(type_is_a_registered_okf_type, files) == []
    files[CANONICAL] = "x\n"
    assert found(type_is_a_registered_okf_type, files) == [("a.md", None)]


def test_non_empty_title() -> None:
    assert found(non_empty_title, {"a.md": concept()}) == []
    no_title = doc("type: Guide\ntitle: ''\ndescription: D\n")
    assert found(non_empty_title, {"a.md": no_title}) == [("a.md", None)]


def test_non_empty_description_no_closing_period() -> None:
    assert found(non_empty_description_no_closing_period, {"a.md": concept()}) == []
    files = {
        "a.md": doc("type: Guide\ntitle: A\n"),
        "b.md": doc("type: Guide\ntitle: B\ndescription: Ends.\n"),
    }
    assert found(non_empty_description_no_closing_period, files) == [
        ("a.md", None),
        ("b.md", None),
    ]


def test_resource_a_repo_root_path_or_a_uri() -> None:
    files = {
        "a.md": concept(extra="resource: /src/x.py\n"),
        "b.md": concept(extra="resource: https://example.com\n"),
    }
    assert found(resource_a_repo_root_path_or_a_uri, files) == []
    assert found(
        resource_a_repo_root_path_or_a_uri,
        {"a.md": concept(extra="resource: src/x.py\n")},
    ) == [("a.md", None)]


def test_recipe_description_carries_a_resource() -> None:
    good = concept("Recipe-Description", "resource: /x\n")
    assert found(recipe_description_carries_a_resource, {"a.md": good}) == []
    bad = concept("Recipe-Description")
    assert found(recipe_description_carries_a_resource, {"a.md": bad}) == [
        ("a.md", None)
    ]


def test_standard_lives_under_standards() -> None:
    good = {"standards/x/a.md": concept("Standard")}
    assert found(standard_lives_under_standards, good) == []
    assert found(standard_lives_under_standards, {"a.md": concept("Standard")}) == [
        ("a.md", None)
    ]


def test_loop_lives_under_loops() -> None:
    assert found(loop_lives_under_loops, {"loops/a.md": concept("Loop")}) == []
    assert found(loop_lives_under_loops, {"a.md": concept("Loop")}) == [("a.md", None)]


def test_registry_lives_under_registries() -> None:
    home = {"registries/a.md": concept("Registry")}
    assert found(registry_lives_under_registries, home) == []
    stray = {"a.md": concept("Registry")}
    assert found(registry_lives_under_registries, stray) == [("a.md", None)]
    in_set = {"workstreams/w/a.md": concept("Registry")}
    assert found(registry_lives_under_registries, in_set) == []


def test_guide_lives_under_guides() -> None:
    assert found(guide_lives_under_guides, {"guides/a.md": concept("Guide")}) == []
    assert found(guide_lives_under_guides, {"a.md": concept("Guide")}) == [
        ("a.md", None)
    ]
    in_set = {"workstreams/w/a.md": concept("Guide")}
    assert found(guide_lives_under_guides, in_set) == []


def test_readmemd_is_typed_readme() -> None:
    good = {"README.md": concept("README"), "a.md": concept()}
    assert found(readmemd_is_typed_readme, good) == []
    bad = {"README.md": concept(), "a.md": concept("README")}
    assert found(readmemd_is_typed_readme, bad) == [("README.md", None), ("a.md", None)]


def test_readmemd_is_typed_readme_reports_a_readme_with_no_type() -> None:
    untyped = {"d/README.md": doc("title: R\ndescription: D\n")}
    assert found(readmemd_is_typed_readme, untyped) == [("d/README.md", None)]


# --- documentation-sets.md ---


def test_an_index_in_every_directory() -> None:
    good = {"index.md": "# I\n", "a/b.md": concept(), "a/index.md": "# I\n"}
    assert found(an_index_in_every_directory, good) == []
    bad = {
        "index.md": "# I\n",
        "a/b.md": concept(),
        "docs/decisions/0001-x.md": "# X\n",
    }
    assert found(an_index_in_every_directory, bad) == [
        ("a/index.md", None),
        ("docs/decisions/index.md", None),
    ]


# --- indexes.md ---


def test_no_okf_type() -> None:
    assert found(no_okf_type, {"index.md": doc("okf_version: '0.1'\n")}) == []
    assert found(no_okf_type, {"d/index.md": doc("type: Guide\n")}) == [
        ("d/index.md", None)
    ]


def test_introduction_between_h1_and_listing() -> None:
    good = "# I\n\nWhat this holds.\n\nOrdering: none.\n\n- [A](/a.md) — One doc\n"
    assert found(introduction_between_h1_and_listing, {"index.md": good}) == []
    bad = "# I\n\nOrdering: none.\n\n## Docs\n\n- [A](/a.md) — One doc\n"
    assert found(introduction_between_h1_and_listing, {"index.md": bad}) == [
        ("index.md", None)
    ]


def test_introduction_between_h1_and_listing_reports_no_h1() -> None:
    no_h1 = "What this holds.\n\n- [A](/a.md) — One doc\n"
    assert found(introduction_between_h1_and_listing, {"index.md": no_h1}) == [
        ("index.md", None)
    ]


def test_one_entry_per_concept_document_and_child_directory() -> None:
    good = "# I\n\nHolds.\n\n- [A](/a.md) — One doc\n- [d/](/d/index.md) — the d set\n"
    files = {"index.md": good, "a.md": concept(), "d/index.md": "# D\n"}
    assert found(one_entry_per_concept_document_and_child_directory, files) == []
    bad = (
        "# I\n\nHolds.\n\n"
        "- [A](/a.md) -- One doc\n"
        "- [d/](/d/index.md)\n"
        "- [d/](/d/index.md)\n"
        "- a bullet with no link\n"
        "- [X](/x.md) — gone\n"
    )
    files = {
        "index.md": bad,
        "a.md": concept(),
        "b.md": concept(),
        "d/index.md": "# D\n",
    }
    assert found(one_entry_per_concept_document_and_child_directory, files) == [
        ("index.md", None),
        ("index.md", 5),
        ("index.md", 7),
        ("index.md", 8),
        ("index.md", 9),
    ]


def test_one_entry_per_concept_document_and_child_directory_in_a_working_set() -> None:
    listing = "# I\n\nHolds.\n\n- [A](/workstreams/w/a.md) — One doc\n- `setup.sh` — makes the lab\n- [run](/workstreams/w/run.mjs) — runs it\n"
    files = {"workstreams/w/index.md": listing, "workstreams/w/a.md": concept()}
    assert found(one_entry_per_concept_document_and_child_directory, files) == []
    files = {
        "workstreams/w/index.md": listing,
        "workstreams/w/a.md": concept(),
        "workstreams/w/b.md": concept(),
    }
    assert found(one_entry_per_concept_document_and_child_directory, files) == [
        ("workstreams/w/index.md", None)
    ]


def test_one_entry_per_concept_document_and_child_directory_reads_the_ending() -> None:
    good = "# I\n\nHolds.\n\n- [A](/a.md) (draft) — One doc\n"
    files = {"index.md": good, "a.md": concept(), "tests/x/index.md": "# T\n"}
    assert found(one_entry_per_concept_document_and_child_directory, files) == []
    bad = "# I\n\nHolds.\n\n- [A](/a.md) — One doc, more\n"
    files = {"index.md": bad, "a.md": concept()}
    assert found(one_entry_per_concept_document_and_child_directory, files) == [
        ("index.md", 5)
    ]


def test_one_entry_per_concept_document_and_child_directory_reads_every_heading() -> (
    None
):
    good = (
        "# I\n\nHolds.\n\n- [A](/a.md) — One doc\n\n"
        "## Directories\n\n- [d/](/d/index.md)\n"
    )
    files = {"index.md": good, "a.md": concept(), "d/index.md": "# D\n"}
    assert found(one_entry_per_concept_document_and_child_directory, files) == []
    stray = good + "\n## Notes\n\n- a stray note\n"
    files = {"index.md": stray, "a.md": concept(), "d/index.md": "# D\n"}
    assert found(one_entry_per_concept_document_and_child_directory, files) == [
        ("index.md", 13)
    ]


def test_alphabetical_unless_declared_otherwise_sorts_bullets_under_any_heading() -> (
    None
):
    good = "# I\n\nHolds.\n\n- [a](/a.md) — A\n\n## Directories\n\n- [b/](/b/index.md)\n- [c/](/c/index.md)\n"
    assert found(alphabetical_unless_declared_otherwise, {"index.md": good}) == []
    bad = "# I\n\nHolds.\n\n- [a](/a.md) — A\n\n## Directories\n\n- [c/](/c/index.md)\n- [b/](/b/index.md)\n"
    assert found(alphabetical_unless_declared_otherwise, {"index.md": bad}) == [
        ("index.md", None)
    ]


def test_alphabetical_unless_declared_otherwise() -> None:
    good = (
        "# I\n\nHolds.\n\n- [Readme](/README.md) — R\n- [a](/a.md) — A\n"
        "- [B](/b.md) — B\n- [c/](/c/index.md)\n"
    )
    assert found(alphabetical_unless_declared_otherwise, {"index.md": good}) == []
    bad = "# I\n\nHolds.\n\n- [c/](/c/index.md)\n- [B](/b.md) — B\n- [a](/a.md) — A\n"
    assert found(alphabetical_unless_declared_otherwise, {"index.md": bad}) == [
        ("index.md", None),
        ("index.md", None),
    ]
    declared = (
        "# I\n\nHolds.\n\nOrdering: reading order.\n\n- [c/](/c/index.md)\n"
        "- [B](/b.md) — B\n- [Readme](/README.md) — R\n"
    )
    assert found(alphabetical_unless_declared_otherwise, {"index.md": declared}) == [
        ("index.md", 9)
    ]


def test_alphabetical_unless_declared_otherwise_reads_ordering_above_any_bullet() -> (
    None
):
    late = "# I\n\nHolds.\n\n- a note\n\nOrdering: late.\n\n- [B](/b.md) — B\n- [a](/a.md) — A\n"
    assert found(alphabetical_unless_declared_otherwise, {"index.md": late}) == [
        ("index.md", None)
    ]


def test_okf_version_declared() -> None:
    good = {"index.md": doc("okf_version: '0.1'\n", "# I\n")}
    assert found(okf_version_declared, good) == []
    assert found(okf_version_declared, {"index.md": "# I\n"}) == [("index.md", None)]
    assert found(okf_version_declared, {"a.md": concept()}) == [("index.md", None)]


# --- readme-content.md ---


def test_readme_holds_an_h1() -> None:
    assert found(readme_holds_an_h1, {"d/README.md": concept("README")}) == []
    no_h1 = doc("type: README\ntitle: R\ndescription: D\n", "## Only an H2\n")
    assert found(readme_holds_an_h1, {"d/README.md": no_h1}) == [("d/README.md", None)]


# --- local-okf-types.md ---


LOCAL = "registries/okf-types.md"


def local(rows: str) -> dict[str, str]:
    """A consumer's local OKF types table; its first row is on line 11."""
    table = f"## OKF types\n\n| OKF type | What it is |\n|---|---|\n{rows}"
    return {LOCAL: doc("type: Registry\ntitle: T\ndescription: D\n", table)}


def test_okf_type_name_to_description() -> None:
    good = local("| `Resume` | A resume |\n")
    assert found(okf_type_name_to_description, good) == []
    bad = local("| bad name | A thing |\n| `Story` |  |\n")
    assert found(okf_type_name_to_description, bad) == [(LOCAL, 11), (LOCAL, 12)]
    apex = bad | {CANONICAL: "x\n"}
    assert found(okf_type_name_to_description, apex) == []
    no_table = {LOCAL: doc("type: Registry\ntitle: T\ndescription: D\n")}
    assert found(okf_type_name_to_description, no_table) == [(LOCAL, None)]


def test_rows_in_alphabetical_order() -> None:
    good = local("| `Alpha` | A |\n| `Beta-X` | B |\n| `Zed` | Z |\n")
    assert found(rows_in_alphabetical_order, good) == []
    bad = local("| `Zed` | Z |\n| `Alpha` | A |\n")
    assert found(rows_in_alphabetical_order, bad) == [(LOCAL, 11)]


def test_add_never_shadow() -> None:
    assert found(add_never_shadow, local("| `Resume` | A resume |\n")) == []
    bad = local("| `Api` | A |\n| `Readme` | R |\n| `API` | B |\n")
    assert found(add_never_shadow, bad) == [(LOCAL, 12), (LOCAL, 13)]


# --- workstream-files.md ---


def test_workstreams_holds_only_workstreams() -> None:
    good = {"workstreams/index.md": "# I\n", "workstreams/w/WORKSTREAM.md": "# R\n"}
    assert found(workstreams_holds_only_workstreams, good) == []
    bad = good | {"workstreams/notes.md": "# N\n"}
    assert found(workstreams_holds_only_workstreams, bad) == [
        ("workstreams/notes.md", None)
    ]


def test_one_directory_under_workstreams() -> None:
    good = {
        "workstreams/w/index.md": "# I\n",
        "workstreams/w/WORKSTREAM.md": "# R\n",
        "workstreams/w/sub/check-fixes.md": "# D\n",
        "workstreams/w/code/My_Module.py": "x = 1\n",
        "workstreams/w/image/Containerfile": "FROM fedora\n",
        "workstreams/w/.gitignore": "node_modules\n",
    }
    assert found(one_directory_under_workstreams, good) == []
    bad = {"workstreams/v/Notes.md": "# N\n", "workstreams/v/good.Draft.md": "# D\n"}
    assert found(one_directory_under_workstreams, bad) == [
        ("workstreams/v/Notes.md", None),
        ("workstreams/v/WORKSTREAM.md", None),
        ("workstreams/v/good.Draft.md", None),
        ("workstreams/v/index.md", None),
    ]


def test_the_worklist_in_the_head_file_only() -> None:
    worklist = "# R\n\n## Planned\n\n- **Item** body\n\n## Completed\n"
    good = {
        "workstreams/w/WORKSTREAM.md": worklist,
        "workstreams/w/s/WORKSTREAM.md": worklist,
        "workstreams/w/note.md": "# N\n\n## Notes\n\n### Planned\n",
        "guides/g.md": worklist,
    }
    assert found(the_worklist_in_the_head_file_only, good) == []
    bad = {"workstreams/w/note.md": "# N\n\n## Completed\n\n## Planned\n"}
    assert found(the_worklist_in_the_head_file_only, bad) == [
        ("workstreams/w/note.md", 3),
        ("workstreams/w/note.md", 5),
    ]


def test_every_file_reached_from_its_head_file() -> None:
    good = {
        "workstreams/w/index.md": "# I\n\n- [N](/workstreams/w/note.md) — N\n",
        "workstreams/w/WORKSTREAM.md": "# R\n\n[Note](note.md)\n",
        "workstreams/w/note.md": "# N\n",
        "workstreams/w/s/WORKSTREAM.md": "# S\n\n[Deep](deep.md)\n",
        "workstreams/w/s/deep.md": "# D\n",
    }
    assert found(every_file_reached_from_its_head_file, good) == []
    bad = {
        "workstreams/w/index.md": "# I\n\n[Lost](/workstreams/w/lost.md)\n",
        "workstreams/w/WORKSTREAM.md": "# R\n",
        "workstreams/w/lost.md": "# L\n",
        "workstreams/w/s/WORKSTREAM.md": "# S\n",
        "workstreams/w/s/leaf.md": "# F\n",
    }
    assert found(every_file_reached_from_its_head_file, bad) == [
        ("workstreams/w/lost.md", None),
        ("workstreams/w/s/leaf.md", None),
    ]
