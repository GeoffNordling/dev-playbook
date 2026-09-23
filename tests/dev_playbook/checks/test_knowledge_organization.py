"""Unit tests for the knowledge-organization family's checks."""

from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

from dev_playbook.check_registry import Finding
from dev_playbook.checks.knowledge_organization import (
    add_never_shadow,
    alphabetical_unless_declared_otherwise,
    an_index_in_every_directory,
    fragment_anchor_matches_the_slug,
    frontmatter_a_yaml_mapping,
    frontmatter_declares_type_vocabulary,
    guide_lives_under_guides,
    headings_slugify_distinctly,
    introduction_between_h1_and_listing,
    keys_in_alphabetical_order,
    language_section_present,
    loop_lives_under_loops,
    no_okf_type,
    no_tags_or_timestamp,
    non_empty_description_no_closing_period,
    non_empty_title,
    okf_version_declared,
    one_directory_under_working_docs,
    one_entry_per_concept_document_and_child_directory,
    one_list_of_items_state_by_section,
    readme_holds_an_h1,
    readmemd_is_typed_readme,
    recipe_description_carries_a_resource,
    reference_resolves,
    relative_path_inside_the_bundle,
    resource_a_repo_root_path_or_a_uri,
    root_absolute_path_in_the_same_repo,
    stable_named_anchor,
    standard_lives_under_standards,
    term_definition_avoid_line,
    type_name_to_description,
    type_names_a_registered_type,
    working_docs_holds_only_sets,
    workspace_path_for_a_stable_location,
    workspace_path_for_another_repo,
)
from dev_playbook.model import Repo

SKILL = "dotfiles/dot-claude/skills/demo"
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


def test_workspace_path_for_another_repo() -> None:
    good = "[x](~/workspace/other/a.md)\n\n    ~/workspace/other/in-code.md\n"
    assert found(workspace_path_for_another_repo, {"a.md": good}) == []
    bad = "see ~/workspace/other/a.md here\n[x](../../outside.md)\n"
    assert found(workspace_path_for_another_repo, {"d/a.md": bad}) == [
        ("d/a.md", 1),
        ("d/a.md", 2),
    ]


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


# --- document-types.md ---


def test_frontmatter_a_yaml_mapping() -> None:
    assert found(frontmatter_a_yaml_mapping, {"a.md": concept()}) == []
    assert found(
        frontmatter_a_yaml_mapping, {"a.md": "# A\n", "index.md": "# I\n"}
    ) == [("a.md", None)]


def test_type_names_a_registered_type() -> None:
    assert found(type_names_a_registered_type, {"a.md": concept("Guide")}) == []
    files = {"a.md": concept("Bogus"), "b.md": doc("title: B\ndescription: D\n")}
    assert found(type_names_a_registered_type, files) == [
        ("a.md", None),
        ("b.md", None),
    ]


def test_type_names_a_registered_type_reads_local_types() -> None:
    index = doc("okf_version: '0.1'\nokf_types:\n  Resume: A resume\n", "# I\n")
    files = {"index.md": index, "a.md": concept("Resume")}
    assert found(type_names_a_registered_type, files) == []
    files[CANONICAL] = "x\n"
    assert found(type_names_a_registered_type, files) == [("a.md", None)]


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


def test_no_tags_or_timestamp() -> None:
    assert found(no_tags_or_timestamp, {"a.md": concept()}) == []
    bad = concept(extra="tags: [x]\ntimestamp: now\n")
    assert found(no_tags_or_timestamp, {"a.md": bad}) == [
        ("a.md", None),
        ("a.md", None),
    ]


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


def test_guide_lives_under_guides() -> None:
    assert found(guide_lives_under_guides, {"guides/a.md": concept("Guide")}) == []
    assert found(guide_lives_under_guides, {"a.md": concept("Guide")}) == [
        ("a.md", None)
    ]


def test_readmemd_is_typed_readme() -> None:
    good = {"README.md": concept("README"), "a.md": concept()}
    assert found(readmemd_is_typed_readme, good) == []
    bad = {"README.md": concept(), "a.md": concept("README")}
    assert found(readmemd_is_typed_readme, bad) == [("README.md", None), ("a.md", None)]


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
    declared = "# I\n\nHolds.\n\nOrdering: reading order.\n\n- [B](/b.md) — B\n- [Readme](/README.md) — R\n"
    assert found(alphabetical_unless_declared_otherwise, {"index.md": declared}) == [
        ("index.md", 8)
    ]


def test_okf_version_declared() -> None:
    good = {"index.md": doc("okf_version: '0.1'\n", "# I\n")}
    assert found(okf_version_declared, good) == []
    assert found(okf_version_declared, {"index.md": "# I\n"}) == [("index.md", None)]


# --- readme-content.md ---


def test_readme_holds_an_h1() -> None:
    assert found(readme_holds_an_h1, {"d/README.md": concept("README")}) == []
    no_h1 = doc("type: README\ntitle: R\ndescription: D\n", "## Only an H2\n")
    assert found(readme_holds_an_h1, {"d/README.md": no_h1}) == [("d/README.md", None)]


# --- type-registry.md ---


def local(types: str) -> dict[str, str]:
    return {"index.md": doc(f"okf_version: '0.1'\nokf_types:\n{types}", "# I\n")}


def test_type_name_to_description() -> None:
    assert found(type_name_to_description, local("  Resume: A resume\n")) == []
    bad = local("  bad name: A thing\n  Story: ''\n")
    assert found(type_name_to_description, bad) == [
        ("index.md", None),
        ("index.md", None),
    ]
    apex = bad | {CANONICAL: "x\n"}
    assert found(type_name_to_description, apex) == []


def test_keys_in_alphabetical_order() -> None:
    assert (
        found(keys_in_alphabetical_order, local("  Alpha: A\n  beta-x: B\n  Zed: Z\n"))
        == []
    )
    assert found(keys_in_alphabetical_order, local("  Zed: Z\n  Alpha: A\n")) == [
        ("index.md", None)
    ]


def test_add_never_shadow() -> None:
    assert found(add_never_shadow, local("  Resume: A resume\n")) == []
    bad = local("  Api: A\n  Readme: R\n  API: B\n")
    assert found(add_never_shadow, bad) == [("index.md", None), ("index.md", None)]


# --- working-documentation-sets.md ---


def test_working_docs_holds_only_sets() -> None:
    good = {"working-docs/index.md": "# I\n", "working-docs/w/ROOT.md": "# R\n"}
    assert found(working_docs_holds_only_sets, good) == []
    bad = good | {"working-docs/notes.md": "# N\n"}
    assert found(working_docs_holds_only_sets, bad) == [("working-docs/notes.md", None)]


def test_one_directory_under_working_docs() -> None:
    good = {
        "working-docs/w/index.md": "# I\n",
        "working-docs/w/ROOT.md": "# R\n",
        "working-docs/w/sub/detector-fixes.md": "# D\n",
        "working-docs/w/code/My_Module.py": "x = 1\n",
    }
    assert found(one_directory_under_working_docs, good) == []
    bad = {"working-docs/v/Notes.md": "# N\n"}
    assert found(one_directory_under_working_docs, bad) == [
        ("working-docs/v/Notes.md", None),
        ("working-docs/v/ROOT.md", None),
        ("working-docs/v/index.md", None),
    ]


def test_one_list_of_items_state_by_section() -> None:
    leaf = "# R\n\n## Planned\n\nLead-in.\n\n- **Item** body\n\n## Completed\n\n- **Done** body\n"
    good = {
        "working-docs/w/ROOT.md": "# R\n\nThe set.\n",
        "working-docs/w/s/ROOT.md": leaf,
        "working-docs/w/s/note.md": "# N\n",
    }
    assert found(one_list_of_items_state_by_section, good) == []
    bad = {
        "working-docs/w/ROOT.md": "# R\n\n## Planned\n\n- plain item\n",
        "working-docs/w/note.md": "# N\n\n## Completed\n",
    }
    assert found(one_list_of_items_state_by_section, bad) == [
        ("working-docs/w/ROOT.md", None),
        ("working-docs/w/ROOT.md", 5),
        ("working-docs/w/note.md", 3),
    ]
