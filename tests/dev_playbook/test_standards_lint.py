"""Behavioral tests for the standards-lint detector (the meta-standard's rules).

standards-lint is a published hook: it audits the ``standards/`` tree of any
repo, in dev-playbook mode (keyed by the canonical consumer template) or
consumer mode (everything else). Each check function takes a repo root and
returns findings; discovery goes through ``git ls-files``, so every fixture is
a git repo. The
rule-matrix check's ``--list-rules`` boundary is injected as a plain callable,
and consumer-mode fixtures pass a synthetic upstream root, so both are exercised
without subprocessing real detectors.
"""

import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from dev_playbook import standards_lint as sa


def make_repo(tmp_path: Path, files: dict[str, str]) -> Path:
    """Write files into a fresh git repo and return its root."""
    repo = tmp_path / "repo"
    for rel, content in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    return repo


def card(
    title: str,
    *,
    type_: str = "Standard-Card",
    cells: tuple[str, ...] = ("Define", "Audit", "Enforce", "Adopt"),
    question: str | None = None,
    description: str | None = None,
    body: str | None = None,
) -> str:
    """A standard card with the given title, type, and cell sections.

    The question sentence and the description default to the same text, as
    ``standard.card-question`` requires; either can be overridden to break the
    pairing, and ``body`` replaces the opening paragraph outright.
    """
    question = question or f"Governs how {title} is done"
    opening = body if body is not None else f"{question}."
    front = (
        f"---\ntype: {type_}\ntitle: {title}\n"
        f"description: {description if description is not None else question}\n"
        f"---\n\n# {title}\n\n{opening}\n"
    )
    return front + "".join(f"\n## {cell}\n\n- none\n" for cell in cells)


def readme() -> str:
    """A conformant standards/README.md fixture."""
    return "---\ntype: README\ntitle: Standards\ndescription: s\n---\n\n# Standards\n"


# --- standard.card-layout ---------------------------------------------------


def test_well_formed_card_passes_card_layout(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"standards/build.md": card("Build")})

    assert sa.check_card_layout(repo) == []


def test_flat_standards_file_without_card_type_is_flagged(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"standards/build.md": card("Build", type_="Standard")})

    findings = sa.check_card_layout(repo)

    assert [f.rule for f in findings] == [sa.CARD_LAYOUT]
    assert findings[0].file == "standards/build.md"


def test_card_missing_a_cell_is_flagged(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {"standards/build.md": card("Build", cells=("Define", "Audit", "Enforce"))},
    )

    findings = sa.check_card_layout(repo)

    assert [f.rule for f in findings] == [sa.CARD_LAYOUT]
    assert "Adopt" in findings[0].message


def test_card_with_cells_out_of_order_is_flagged(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "standards/build.md": card(
                "Build", cells=("Define", "Enforce", "Audit", "Adopt")
            )
        },
    )

    findings = sa.check_card_layout(repo)

    assert [f.rule for f in findings] == [sa.CARD_LAYOUT]


def test_card_with_a_duplicated_cell_is_flagged_as_duplicate(tmp_path: Path) -> None:
    # All four cells present but one repeated: reported as a duplicate, not as
    # "out of order" (the real defect the message must name).
    repo = make_repo(
        tmp_path,
        {
            "standards/build.md": card(
                "Build", cells=("Define", "Define", "Audit", "Enforce", "Adopt")
            )
        },
    )

    findings = sa.check_card_layout(repo)

    assert [f.rule for f in findings] == [sa.CARD_LAYOUT]
    assert "duplicate" in findings[0].message.lower()


def test_readme_and_index_are_not_treated_as_cards(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "standards/README.md": "---\ntype: README\ntitle: S\ndescription: s\n---\n\n# S\n",
            "standards/index.md": "# index\n\n- x\n",
        },
    )

    assert sa.check_card_layout(repo) == []


def test_subdirectory_contract_doc_is_not_treated_as_a_card(tmp_path: Path) -> None:
    # A contract lives in a sub-directory and is not a card, so card-layout
    # never demands the four cells of it (the flat=card layout).
    repo = make_repo(
        tmp_path,
        {
            "standards/build/index.md": "# build\n",
            "standards/build/layers.md": (
                "---\ntype: Standard\ntitle: Layers\ndescription: layers\n---\n\n# Layers\n"
            ),
        },
    )

    assert sa.check_card_layout(repo) == []


# --- standard.card-question -------------------------------------------------


def test_matching_question_and_description_pass(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"standards/build.md": card("Build")})

    assert sa.check_card_question(repo) == []


def test_description_differing_from_the_question_is_flagged(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "standards/build.md": card(
                "Build", description="Card for the build standard"
            )
        },
    )

    findings = sa.check_card_question(repo)

    assert [f.rule for f in findings] == [sa.CARD_QUESTION]
    assert "verbatim" in findings[0].message


def test_description_keeping_the_period_is_flagged(tmp_path: Path) -> None:
    # The description repeats the sentence *less* its period; okf-lint forbids a
    # trailing period in a description, so keeping it fails both rules.
    repo = make_repo(
        tmp_path,
        {"standards/build.md": card("Build", description="Governs how Build is done.")},
    )

    findings = sa.check_card_question(repo)

    assert [f.rule for f in findings] == [sa.CARD_QUESTION]


def test_question_not_opening_governs_how_is_flagged(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {"standards/build.md": card("Build", question="Covers the build of a repo")},
    )

    findings = sa.check_card_question(repo)

    assert [f.rule for f in findings] == [sa.CARD_QUESTION]
    assert "Governs how" in findings[0].message


def test_question_wrapped_across_lines_is_flattened(tmp_path: Path) -> None:
    # Cards wrap at the prose margin, so the sentence is read with its line
    # breaks flattened to spaces before the description is compared to it.
    repo = make_repo(
        tmp_path,
        {
            "standards/build.md": card(
                "Build",
                description="Governs how a repository is laid out, built, and checked",
                body="Governs how a repository is laid out, built, and\nchecked.",
            )
        },
    )

    assert sa.check_card_question(repo) == []


def test_prose_after_the_question_sentence_is_ignored(tmp_path: Path) -> None:
    # A card may carry boundary prose after its question; only the first
    # sentence is the question.
    repo = make_repo(
        tmp_path,
        {
            "standards/build.md": card(
                "Build",
                description="Governs how Build is done",
                body="Governs how Build is done. This card owns the shapes.",
            )
        },
    )

    assert sa.check_card_question(repo) == []


def test_a_dotted_filename_does_not_end_the_question(tmp_path: Path) -> None:
    # `CLAUDE.md` carries a period with no space after it, so the sentence runs
    # past it to the real terminator.
    repo = make_repo(
        tmp_path,
        {
            "standards/harness.md": card(
                "Harness",
                description="Governs how CLAUDE.md is written",
                body="Governs how CLAUDE.md is written.",
            )
        },
    )

    assert sa.check_card_question(repo) == []


def test_card_with_no_paragraph_after_its_h1_is_flagged(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "standards/build.md": card("Build", body="").replace(
                "# Build\n\n\n", "# Build\n\n"
            )
        },
    )

    findings = sa.check_card_question(repo)

    assert [f.rule for f in findings] == [sa.CARD_QUESTION]
    assert "no question sentence" in findings[0].message


def test_mistyped_flat_file_is_left_to_card_layout(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"standards/build.md": card("Build", type_="Standard")})

    assert sa.check_card_question(repo) == []


# --- standard.catalog-order -------------------------------------------------


def catalog(doc_bullets: list[str], dir_bullets: list[str] | None = None) -> str:
    """A standards/index.md with the given document and directory bullets."""
    intro = "# standards\n\nOrdering: README, meta, cards, contracts, dirs.\n\n"
    docs = "\n".join(doc_bullets) + "\n"
    dirs = ""
    if dir_bullets:
        dirs = "\n## Directories\n\n" + "\n".join(dir_bullets) + "\n"
    return intro + docs + dirs


def bullet(target: str, title: str) -> str:
    """One index bullet linking title to a root-absolute target."""
    return f"- [{title}](/{target}) — desc"


def ordered_repo_files(extra: dict[str, str]) -> dict[str, str]:
    """The card + contract files a well-ordered catalog references.

    Carries the canonical template so full audits over these files run in
    dev-playbook mode -- the template is the mode marker.
    """
    return {
        "standards/README.md": readme(),
        "standards/standard.md": card("Meta-Standard"),
        "standards/build.md": card("Build"),
        "standards/python.md": card("Python"),
        "standards/standard/format.md": (
            "---\ntype: Standard\ntitle: Standards and Standard Cards\n"
            "description: d\n---\n\n# Standards and Standard Cards\n"
        ),
        "standards/build/canonical/.pre-commit-config.yaml": _canonical([]),
        **extra,
    }


def test_catalog_in_declared_order_passes(tmp_path: Path) -> None:
    files = ordered_repo_files({})
    files["standards/index.md"] = catalog(
        [
            bullet("standards/README.md", "Standards"),
            bullet("standards/standard.md", "Meta-Standard"),
            bullet("standards/build.md", "Build"),
            bullet("standards/python.md", "Python"),
            bullet("standards/standard/format.md", "Standards and Standard Cards"),
        ]
    )
    repo = make_repo(tmp_path, files)

    assert sa.check_catalog_order(repo, dev_playbook_mode=True) == []


def test_readme_not_first_is_flagged(tmp_path: Path) -> None:
    files = ordered_repo_files({})
    files["standards/index.md"] = catalog(
        [
            bullet("standards/standard.md", "Meta-Standard"),
            bullet("standards/README.md", "Standards"),
            bullet("standards/build.md", "Build"),
            bullet("standards/python.md", "Python"),
            bullet("standards/standard/format.md", "Standards and Standard Cards"),
        ]
    )
    repo = make_repo(tmp_path, files)

    findings = sa.check_catalog_order(repo, dev_playbook_mode=True)

    assert [f.rule for f in findings] == [sa.CATALOG_ORDER]


def test_cards_out_of_alphabetical_order_flagged(tmp_path: Path) -> None:
    files = ordered_repo_files({})
    files["standards/index.md"] = catalog(
        [
            bullet("standards/README.md", "Standards"),
            bullet("standards/standard.md", "Meta-Standard"),
            bullet("standards/python.md", "Python"),
            bullet("standards/build.md", "Build"),
            bullet("standards/standard/format.md", "Standards and Standard Cards"),
        ]
    )
    repo = make_repo(tmp_path, files)

    findings = sa.check_catalog_order(repo, dev_playbook_mode=True)

    assert [f.rule for f in findings] == [sa.CATALOG_ORDER]


def test_contract_doc_before_a_card_flagged(tmp_path: Path) -> None:
    files = ordered_repo_files({})
    files["standards/index.md"] = catalog(
        [
            bullet("standards/README.md", "Standards"),
            bullet("standards/standard.md", "Meta-Standard"),
            bullet("standards/standard/format.md", "Standards and Standard Cards"),
            bullet("standards/build.md", "Build"),
            bullet("standards/python.md", "Python"),
        ]
    )
    repo = make_repo(tmp_path, files)

    findings = sa.check_catalog_order(repo, dev_playbook_mode=True)

    assert [f.rule for f in findings] == [sa.CATALOG_ORDER]


def consumer_catalog_files(doc_bullets: list[str]) -> dict[str, str]:
    """A consumer standards/ tree: README + own cards, no meta-standard card."""
    return {
        "standards/README.md": readme(),
        "standards/alpha.md": card("Alpha"),
        "standards/beta.md": card("Beta"),
        "standards/index.md": catalog(doc_bullets),
    }


def test_consumer_catalog_readme_then_own_cards_passes(tmp_path: Path) -> None:
    # No meta-standard card: the catalog leads with README, then its own cards
    # by title. The meta-card row is data-driven, so its absence is not a defect.
    repo = make_repo(
        tmp_path,
        consumer_catalog_files(
            [
                bullet("standards/README.md", "Standards"),
                bullet("standards/alpha.md", "Alpha"),
                bullet("standards/beta.md", "Beta"),
            ]
        ),
    )

    assert sa.check_catalog_order(repo, dev_playbook_mode=False) == []


def test_consumer_catalog_cards_out_of_order_flagged(tmp_path: Path) -> None:
    # README-first and alphabetical still bind in consumer mode; only the
    # meta-card row is optional.
    repo = make_repo(
        tmp_path,
        consumer_catalog_files(
            [
                bullet("standards/README.md", "Standards"),
                bullet("standards/beta.md", "Beta"),
                bullet("standards/alpha.md", "Alpha"),
            ]
        ),
    )

    findings = sa.check_catalog_order(repo, dev_playbook_mode=False)

    assert [f.rule for f in findings] == [sa.CATALOG_ORDER]


# --- standard.rule-matrix ---------------------------------------------------


def card_citing(title: str, audit: list[str]) -> str:
    """A card whose Audit cell holds the given annotated pointer bullets."""
    cells = {
        "Define": ["- [x](/x) — d"],
        "Audit": audit,
        "Enforce": ["- none"],
        "Adopt": ["- none"],
    }
    front = (
        f"---\ntype: Standard-Card\ntitle: {title}\n"
        f"description: Card for the {title} standard\n---\n\n# {title}\n\nGoverns it.\n"
    )
    body = ""
    for cell, lines in cells.items():
        body += f"\n## {cell}\n\n" + "\n".join(lines) + "\n"
    return front + body


def cite(name: str) -> str:
    """An Audit-cell bullet citing a first-party detector by its scripts/ link."""
    return f"- [{name}](/scripts/{name}) — a detector"


def fake_list_rules(
    mapping: dict[str, list[str]],
) -> Callable[[str, Path], list[str]]:
    """A --list-rules stand-in; an absent name models a script that won't answer."""

    def _list(name: str, root: Path) -> list[str]:
        if name not in mapping:
            raise sa.CannotRun(f"scripts/{name} does not answer --list-rules")
        return mapping[name]

    return _list


def test_consistent_matrix_passes(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path, {"standards/build.md": card_citing("Build", [cite("repo-lint")])}
    )

    findings = sa.check_rule_matrix(repo, fake_list_rules({"repo-lint": ["build.x"]}))

    assert findings == []


def test_uncited_emitted_prefix_fails_direction_one(tmp_path: Path) -> None:
    # repo-lint emits knowledge-organization.y, but that card does not cite
    # repo-lint.
    repo = make_repo(
        tmp_path,
        {
            "standards/build.md": card_citing("Build", [cite("repo-lint")]),
            "standards/knowledge-organization.md": card_citing(
                "Knowledge Organization", ["- none"]
            ),
        },
    )

    findings = sa.check_rule_matrix(
        repo, fake_list_rules({"repo-lint": ["build.x", "knowledge-organization.y"]})
    )

    assert [f.rule for f in findings] == [sa.RULE_MATRIX]
    assert "knowledge-organization.md" in findings[0].file


def test_unbacked_citation_fails_direction_two(tmp_path: Path) -> None:
    # The build card cites repo-lint, but repo-lint emits no build.* rule --
    # only knowledge-organization.*, which that card legitimately cites.
    repo = make_repo(
        tmp_path,
        {
            "standards/build.md": card_citing("Build", [cite("repo-lint")]),
            "standards/knowledge-organization.md": card_citing(
                "Knowledge Organization", [cite("repo-lint")]
            ),
        },
    )

    findings = sa.check_rule_matrix(
        repo, fake_list_rules({"repo-lint": ["knowledge-organization.y"]})
    )

    assert [f.rule for f in findings] == [sa.RULE_MATRIX]
    assert findings[0].file == "standards/build.md"


def test_cited_detector_without_list_rules_fails_membership(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path, {"standards/build.md": card_citing("Build", [cite("repo-lint")])}
    )

    findings = sa.check_rule_matrix(repo, fake_list_rules({}))

    assert [f.rule for f in findings] == [sa.RULE_MATRIX]
    assert "--list-rules" in findings[0].message


def test_third_party_and_judgment_pointers_are_outside_the_matrix(
    tmp_path: Path,
) -> None:
    # ruff (name + pin, no scripts/ link) and a judgment-file pointer are not
    # detector citations, so an empty rule map still passes.
    repo = make_repo(
        tmp_path,
        {
            "standards/shell.md": card_citing(
                "Shell",
                [
                    "- shellcheck — third-party lint",
                    "- [j](/judgments/x.yaml) — a judgment",
                ],
            )
        },
    )

    assert sa.check_rule_matrix(repo, fake_list_rules({})) == []


# --- standard.hook-surfaces -------------------------------------------------


def _manifest(ids: list[str], system_ids: list[str] | None = None) -> str:
    """A .pre-commit-hooks.yaml: scripts/ detector hooks + language:system hooks.

    ``system_ids`` publish non-detector hooks (the validate-manifest shape).
    They join the full published set but not the detector subset the mirror uses.
    """
    detectors = "".join(
        f"- id: {i}\n  name: {i}\n  entry: scripts/{i}\n  language: script\n"
        for i in ids
    )
    systems = "".join(
        f"- id: {i}\n  name: {i}\n  entry: {i} --run\n  language: system\n"
        for i in (system_ids or [])
    )
    return detectors + systems


def _local_block(ids: list[str]) -> str:
    """A .pre-commit-config.yaml whose repo:local block holds make-check + ids."""
    system = (
        "      - id: make-check\n        name: make check\n"
        "        entry: make check\n        language: system\n"
    )
    hooks = "".join(
        f"      - id: {i}\n        name: {i}\n"
        f"        entry: scripts/{i}\n        language: script\n"
        for i in ids
    )
    return "repos:\n  - repo: local\n    hooks:\n" + system + hooks


def _canonical(ids: list[str]) -> str:
    """A canonical template whose pinned dev-playbook block lists the given ids."""
    dev = (
        "  - repo: https://github.com/GeoffNordling/dev-playbook\n"
        "    rev: <pinned-sha>\n    hooks:\n"
        + "".join(f"      - id: {i}\n" for i in ids)
    )
    local = (
        "  - repo: local\n    hooks:\n      - id: make-check\n        name: make check\n"
        "        entry: make check\n        language: system\n"
    )
    return "repos:\n" + dev + local


def _readme_table(ids: list[str]) -> str:
    """A scripts/README.md whose validation table has one backticked row per id."""
    rows = "".join(f"| `{i}` | s | p |\n" for i in ids)
    return (
        "---\ntype: README\ntitle: Scripts\ndescription: s\n---\n\n# Scripts\n\n"
        "| Script | Standard | Purpose |\n|---|---|---|\n" + rows
    )


def surfaces_repo(
    tmp_path: Path,
    *,
    manifest_ids: list[str],
    local_ids: list[str],
    canonical_ids: list[str],
    readme_ids: list[str],
    cited_ids: list[str],
    manifest_system_ids: list[str] | None = None,
) -> Path:
    """Assemble a repo with the published-hook surfaces and citing cards."""
    files = {
        ".pre-commit-hooks.yaml": _manifest(manifest_ids, manifest_system_ids),
        ".pre-commit-config.yaml": _local_block(local_ids),
        "standards/build/canonical/.pre-commit-config.yaml": _canonical(canonical_ids),
        "scripts/README.md": _readme_table(readme_ids),
    }
    for i, name in enumerate(cited_ids):
        files[f"standards/c{i}.md"] = card_citing(f"C{i}", [cite(name)])
    return make_repo(tmp_path, files)


# The published world: standards-lint is now a published detector, and
# validate-manifest a published non-detector (language: system).
ALL = ["repo-lint", "okf-lint", "standards-lint"]
SYSTEM = ["validate-manifest"]


def test_agreeing_hook_surfaces_pass(tmp_path: Path) -> None:
    # Every published detector sits in the manifest, the local block, the
    # canonical pinned block, the README table, and is cited by a card; the
    # published non-detector sits in the manifest and the pinned block.
    repo = surfaces_repo(
        tmp_path,
        manifest_ids=ALL,
        manifest_system_ids=SYSTEM,
        local_ids=ALL,
        canonical_ids=[*ALL, *SYSTEM],
        readme_ids=ALL,
        cited_ids=ALL,
    )

    assert sa.check_hook_surfaces(repo, dev_playbook_mode=True, roster=tuple(ALL)) == []


def test_published_non_detector_in_canonical_is_not_a_stray(tmp_path: Path) -> None:
    # The canonical leg compares against ALL published ids, so validate-manifest
    # (published, language: system, listed in the pinned block) is covered, not
    # flagged as a stray -- and it never enters the detector mirror.
    repo = surfaces_repo(
        tmp_path,
        manifest_ids=ALL,
        manifest_system_ids=SYSTEM,
        local_ids=ALL,
        canonical_ids=[*ALL, *SYSTEM],
        readme_ids=ALL,
        cited_ids=ALL,
    )

    findings = sa.check_hook_surfaces(repo, dev_playbook_mode=True, roster=tuple(ALL))

    assert not any("validate-manifest" in f.message for f in findings)


def test_manifest_hook_missing_from_local_is_flagged(tmp_path: Path) -> None:
    repo = surfaces_repo(
        tmp_path,
        manifest_ids=ALL,
        manifest_system_ids=SYSTEM,
        local_ids=["repo-lint", "standards-lint"],  # okf-lint dropped
        canonical_ids=[*ALL, *SYSTEM],
        readme_ids=ALL,
        cited_ids=ALL,
    )

    findings = sa.check_hook_surfaces(repo, dev_playbook_mode=True, roster=tuple(ALL))

    assert sa.HOOK_SURFACES in {f.rule for f in findings}
    assert any("okf-lint" in f.message for f in findings)


def test_local_detector_not_in_manifest_is_flagged(tmp_path: Path) -> None:
    # No local-only exemption survives the deletion of LOCAL_ONLY: a local
    # detector absent from the manifest is a defect in both directions.
    repo = surfaces_repo(
        tmp_path,
        manifest_ids=["repo-lint", "okf-lint"],  # standards-lint unpublished
        manifest_system_ids=SYSTEM,
        local_ids=ALL,  # but present in the local block
        canonical_ids=["repo-lint", "okf-lint", *SYSTEM],
        readme_ids=ALL,
        cited_ids=ALL,
    )

    findings = sa.check_hook_surfaces(repo, dev_playbook_mode=True, roster=tuple(ALL))

    assert any(
        "standards-lint" in f.message and f.rule == sa.HOOK_SURFACES for f in findings
    )


def test_manifest_hook_missing_from_canonical_is_flagged(tmp_path: Path) -> None:
    # Published, but not offered to consumers through the pinned block.
    repo = surfaces_repo(
        tmp_path,
        manifest_ids=ALL,
        manifest_system_ids=SYSTEM,
        local_ids=ALL,
        canonical_ids=["repo-lint", *SYSTEM],  # okf-lint, standards-lint dropped
        readme_ids=ALL,
        cited_ids=ALL,
    )

    findings = sa.check_hook_surfaces(repo, dev_playbook_mode=True, roster=tuple(ALL))

    assert any("okf-lint" in f.message and f.rule == sa.HOOK_SURFACES for f in findings)


def test_detector_hook_missing_from_readme_table_is_flagged(tmp_path: Path) -> None:
    repo = surfaces_repo(
        tmp_path,
        manifest_ids=ALL,
        manifest_system_ids=SYSTEM,
        local_ids=ALL,
        canonical_ids=[*ALL, *SYSTEM],
        readme_ids=["repo-lint", "standards-lint"],  # okf-lint missing
        cited_ids=ALL,
    )

    findings = sa.check_hook_surfaces(repo, dev_playbook_mode=True, roster=tuple(ALL))

    assert any("okf-lint" in f.message and "README" in f.message for f in findings)


def test_stray_id_in_canonical_dev_block_is_flagged(tmp_path: Path) -> None:
    # An id in the pinned dev-playbook block that the manifest never publishes
    # (a typo or a stale entry) must fail -- the reverse direction.
    repo = surfaces_repo(
        tmp_path,
        manifest_ids=ALL,
        manifest_system_ids=SYSTEM,
        local_ids=ALL,
        canonical_ids=[*ALL, *SYSTEM, "stray-lint"],  # published nowhere
        readme_ids=ALL,
        cited_ids=ALL,
    )

    findings = sa.check_hook_surfaces(repo, dev_playbook_mode=True, roster=tuple(ALL))

    assert any(
        "stray-lint" in f.message and f.rule == sa.HOOK_SURFACES for f in findings
    )


def test_manifest_detector_in_canonical_local_block_is_flagged(tmp_path: Path) -> None:
    # okf-lint sits in canonical's repo:local block, not the pinned dev-playbook
    # block, so a consumer would never get it wired -- it must fail as missing.
    canonical = (
        "repos:\n"
        "  - repo: https://github.com/GeoffNordling/dev-playbook\n"
        "    rev: <pinned-sha>\n    hooks:\n"
        "      - id: repo-lint\n      - id: standards-lint\n"
        "      - id: validate-manifest\n"
        "  - repo: local\n    hooks:\n"
        "      - id: okf-lint\n        name: okf-lint\n"
        "        entry: scripts/okf-lint\n        language: script\n"
    )
    files = {
        ".pre-commit-hooks.yaml": _manifest(ALL, SYSTEM),
        ".pre-commit-config.yaml": _local_block(ALL),
        "standards/build/canonical/.pre-commit-config.yaml": canonical,
        "scripts/README.md": _readme_table(ALL),
    }
    for i, name in enumerate(ALL):
        files[f"standards/c{i}.md"] = card_citing(f"C{i}", [cite(name)])
    repo = make_repo(tmp_path, files)

    findings = sa.check_hook_surfaces(repo, dev_playbook_mode=True, roster=tuple(ALL))

    assert any(
        "okf-lint" in f.message and "canonical" in f.message.lower() for f in findings
    )


def test_detector_hook_cited_by_no_card_is_flagged(tmp_path: Path) -> None:
    repo = surfaces_repo(
        tmp_path,
        manifest_ids=ALL,
        manifest_system_ids=SYSTEM,
        local_ids=ALL,
        canonical_ids=[*ALL, *SYSTEM],
        readme_ids=ALL,
        cited_ids=["repo-lint", "standards-lint"],  # okf-lint cited by no card
    )

    findings = sa.check_hook_surfaces(repo, dev_playbook_mode=True, roster=tuple(ALL))

    assert any("okf-lint" in f.message and "Audit cell" in f.message for f in findings)


def test_aggregate_hook_shape_passes(tmp_path: Path) -> None:
    # The published world: one aggregate hook in the manifest, the local block,
    # and the canonical pinned block; the roster detectors are cited and rowed.
    # The aggregate hook itself owes no card citation and no README row.
    repo = surfaces_repo(
        tmp_path,
        manifest_ids=["agg-lint"],
        local_ids=["agg-lint"],
        canonical_ids=["agg-lint"],
        readme_ids=ALL,
        cited_ids=ALL,
    )

    assert sa.check_hook_surfaces(repo, dev_playbook_mode=True, roster=tuple(ALL)) == []


def test_cited_but_unenrolled_detector_is_flagged(tmp_path: Path) -> None:
    # The closure leg: a card's Audit cell cites a script that is neither in
    # the roster nor a registered ungated audit -- a detector card authored
    # without gating its detector.
    repo = surfaces_repo(
        tmp_path,
        manifest_ids=["agg-lint"],
        local_ids=["agg-lint"],
        canonical_ids=["agg-lint"],
        readme_ids=ALL,
        cited_ids=[*ALL, "rogue-lint"],
    )

    findings = sa.check_hook_surfaces(repo, dev_playbook_mode=True, roster=tuple(ALL))

    assert any("rogue-lint" in f.message and "roster" in f.message for f in findings)


def test_cited_ungated_audit_is_not_an_enrollment_hole(tmp_path: Path) -> None:
    # workspace-lint's shape: cited by a card, absent from the roster, but
    # registered as an ungated audit -- deliberate, not an enrollment hole.
    repo = surfaces_repo(
        tmp_path,
        manifest_ids=["agg-lint"],
        local_ids=["agg-lint"],
        canonical_ids=["agg-lint"],
        readme_ids=ALL,
        cited_ids=[*ALL, "workspace-lint"],
    )

    findings = sa.check_hook_surfaces(repo, dev_playbook_mode=True, roster=tuple(ALL))

    assert findings == []


# --- hook-surfaces: consumer mode ---


def _consumer_surfaces_files(
    *, manifest_ids: list[str], local_ids: list[str], cited_ids: list[str]
) -> dict[str, str]:
    """A consumer's own manifest + local block + citing cards, no canonical/README."""
    files = {
        ".pre-commit-hooks.yaml": _manifest(manifest_ids),
        ".pre-commit-config.yaml": _local_block(local_ids),
    }
    for i, name in enumerate(cited_ids):
        files[f"standards/c{i}.md"] = card_citing(f"C{i}", [cite(name)])
    return files


def test_consumer_mode_agreeing_surfaces_pass(tmp_path: Path) -> None:
    # A consumer with its own manifest + local block, no canonical template and
    # no scripts/README.md: the mirror and cited-by-a-card checks run and pass;
    # the canonical and README sub-checks are silent.
    repo = make_repo(
        tmp_path,
        _consumer_surfaces_files(
            manifest_ids=["own-lint"], local_ids=["own-lint"], cited_ids=["own-lint"]
        ),
    )

    assert sa.check_hook_surfaces(repo, dev_playbook_mode=False) == []


def test_consumer_mode_mirror_still_flags_local_not_in_manifest(tmp_path: Path) -> None:
    # The manifest <-> local mirror runs uniformly in both modes.
    repo = make_repo(
        tmp_path,
        _consumer_surfaces_files(
            manifest_ids=["own-lint"],
            local_ids=["own-lint", "extra-lint"],  # extra-lint unpublished
            cited_ids=["own-lint", "extra-lint"],
        ),
    )

    findings = sa.check_hook_surfaces(repo, dev_playbook_mode=False)

    assert any(
        "extra-lint" in f.message and f.rule == sa.HOOK_SURFACES for f in findings
    )


def test_consumer_mode_ignores_a_canonical_template(tmp_path: Path) -> None:
    # A consumer that happens to carry a canonical template gets no canonical
    # findings: the canonical leg is dev-playbook-only.
    files = _consumer_surfaces_files(
        manifest_ids=["own-lint"], local_ids=["own-lint"], cited_ids=["own-lint"]
    )
    files["standards/build/canonical/.pre-commit-config.yaml"] = _canonical(
        ["stray-lint"]
    )
    repo = make_repo(tmp_path, files)

    assert sa.check_hook_surfaces(repo, dev_playbook_mode=False) == []


def test_hook_surfaces_absent_manifest_reads_as_empty(tmp_path: Path) -> None:
    # A consumer that wires only dev-playbook's pinned block has a local config
    # but no .pre-commit-hooks.yaml of its own: the absent manifest publishes
    # nothing, read as empty rather than surfacing as CannotRun.
    repo = make_repo(tmp_path, {".pre-commit-config.yaml": _local_block([])})

    assert sa.check_hook_surfaces(repo, dev_playbook_mode=False) == []


def test_hook_surfaces_absent_local_config_reads_as_empty(tmp_path: Path) -> None:
    # A repo carrying a manifest but no .pre-commit-config.yaml wires nothing
    # locally: the absent config reads as empty, not CannotRun.
    repo = make_repo(tmp_path, {".pre-commit-hooks.yaml": _manifest([])})

    assert sa.check_hook_surfaces(repo, dev_playbook_mode=False) == []


def test_publisher_less_consumer_passes_clean(tmp_path: Path) -> None:
    # Own cards + catalog, no .pre-commit-hooks.yaml and no .pre-commit-config.yaml:
    # both absent surface files read as empty, so a consumer that publishes no
    # hooks of its own audits clean rather than bricking its gate at exit 2.
    upstream = make_repo(tmp_path / "up", {"README.md": "# up\n"})
    consumer = make_repo(
        tmp_path,
        consumer_catalog_files(
            [
                bullet("standards/README.md", "Standards"),
                bullet("standards/alpha.md", "Alpha"),
                bullet("standards/beta.md", "Beta"),
            ]
        ),
    )

    assert sa.audit(consumer, fake_list_rules({}), hook_repo_root=upstream) == []


# --- standard.card-shadows-upstream -----------------------------------------


def test_local_card_shadowing_an_upstream_card_is_flagged(tmp_path: Path) -> None:
    # The consumer's standards/build.md reuses an upstream card stem, silently
    # overriding dev-playbook's standard of that name.
    upstream = make_repo(tmp_path / "up", {"standards/build.md": card("Build")})
    consumer = make_repo(tmp_path, {"standards/build.md": card("Build")})

    findings = sa.check_card_shadows_upstream(consumer, upstream)

    assert [f.rule for f in findings] == [sa.CARD_SHADOWS]
    assert findings[0].file == "standards/build.md"


def test_local_card_with_a_fresh_stem_is_not_flagged(tmp_path: Path) -> None:
    upstream = make_repo(tmp_path / "up", {"standards/build.md": card("Build")})
    consumer = make_repo(tmp_path, {"standards/widget.md": card("Widget")})

    assert sa.check_card_shadows_upstream(consumer, upstream) == []


def test_shadow_scan_non_git_hook_repo_root_cannot_run(tmp_path: Path) -> None:
    # If the clone the hook ships in is not a git checkout, the upstream card
    # scan's git ls-files fails; that funnels into CannotRun (exit 2), not an
    # uncaught CalledProcessError traceback.
    non_git = tmp_path / "not-a-checkout"
    non_git.mkdir()
    consumer = make_repo(tmp_path, {"standards/build.md": card("Build")})

    with pytest.raises(sa.CannotRun):
        sa.check_card_shadows_upstream(consumer, non_git)


def test_audit_non_git_root_cannot_run(tmp_path: Path) -> None:
    # The optional-surface guard scans the audited root via git ls-files; a
    # non-git root funnels into CannotRun (exit 2) at the same _card_paths
    # chokepoint as the upstream scan, never an uncaught CalledProcessError.
    non_git = tmp_path / "not-a-checkout"
    non_git.mkdir()

    with pytest.raises(sa.CannotRun):
        sa.audit(non_git, fake_list_rules({}))


def _clean_bundle(tmp_path: Path, *, dev_playbook_mode: bool) -> Path:
    """A conformant standards/ bundle carrying a 'build' card, clean on its own.

    In dev-playbook mode it also carries the meta card and a canonical template,
    so hook-surfaces' dev-playbook-only leg has files to read; in consumer mode
    it omits both. The bundle is clean under every rule but the shadow rule.
    """
    files = {
        "standards/README.md": readme(),
        "standards/build.md": card("Build"),
        ".pre-commit-hooks.yaml": "",
        ".pre-commit-config.yaml": _local_block([]),
    }
    doc_bullets = [bullet("standards/README.md", "Standards")]
    if dev_playbook_mode:
        files["standards/standard.md"] = card("Meta-Standard")
        files["standards/build/canonical/.pre-commit-config.yaml"] = _canonical([])
        doc_bullets.append(bullet("standards/standard.md", "Meta-Standard"))
    doc_bullets.append(bullet("standards/build.md", "Build"))
    files["standards/index.md"] = catalog(doc_bullets)
    return make_repo(tmp_path, files)


def test_consumer_mode_audit_flags_a_shadowing_card(tmp_path: Path) -> None:
    # End to end: an otherwise-clean consumer whose only defect is a shadowing
    # card gets exactly the shadow finding.
    upstream = make_repo(tmp_path / "up", {"standards/build.md": card("Build")})
    consumer = _clean_bundle(tmp_path, dev_playbook_mode=False)

    findings = sa.audit(consumer, fake_list_rules({}), hook_repo_root=upstream)

    assert [f.rule for f in findings] == [sa.CARD_SHADOWS]


def test_dev_playbook_mode_audit_never_runs_the_shadow_rule(tmp_path: Path) -> None:
    # The same 'build' stem in dev-playbook mode is not a shadow: dev-playbook's
    # own cards cannot shadow themselves, so the rule is gated off.
    upstream = make_repo(tmp_path / "up", {"standards/build.md": card("Build")})
    devrepo = _clean_bundle(tmp_path, dev_playbook_mode=True)

    # roster=() keeps the fixture self-contained: the bundle's cards cite no
    # detectors, so the real playbook-lint roster would read as unenrolled.
    findings = sa.audit(
        devrepo, fake_list_rules({}), hook_repo_root=upstream, roster=()
    )

    assert findings == []


def _consumer_card_bundle(tmp_path: Path, stem: str) -> Path:
    """A clean consumer carrying a single ``standards/<stem>.md`` card.

    No canonical template and no meta card, so the mode marker is absent; no
    manifest or local config, so hook-surfaces reads them as empty. The bundle
    is clean under every rule but the shadow rule.
    """
    title = stem.capitalize()
    return make_repo(
        tmp_path,
        {
            "standards/README.md": readme(),
            f"standards/{stem}.md": card(title),
            "standards/index.md": catalog(
                [
                    bullet("standards/README.md", "Standards"),
                    bullet(f"standards/{stem}.md", title),
                ]
            ),
        },
    )


def test_consumer_card_named_standard_md_is_flagged_as_a_shadow(tmp_path: Path) -> None:
    # The mode marker is the canonical template, not standards/standard.md, so a
    # consumer card at that exact path stays in consumer mode and the shadow rule
    # catches it -- the one stem the marker used to disable.
    upstream = make_repo(
        tmp_path / "up", {"standards/standard.md": card("Meta-Standard")}
    )
    consumer = _consumer_card_bundle(tmp_path, stem="standard")

    findings = sa.audit(consumer, fake_list_rules({}), hook_repo_root=upstream)

    assert [f.rule for f in findings] == [sa.CARD_SHADOWS]
    assert findings[0].file == "standards/standard.md"


def test_consumer_card_named_standard_md_draws_no_catalog_order_finding(
    tmp_path: Path,
) -> None:
    # In consumer mode standards/standard.md is an ordinary card, sorted among the
    # others by title -- not forced into the meta-card lead slot. A catalog ordered
    # [README, alpha, standard] therefore passes catalog-order, so the sole finding
    # is the intended shadow, never a spurious catalog-order complaint about a
    # meta-standard the consumer has no concept of.
    upstream = make_repo(
        tmp_path / "up", {"standards/standard.md": card("Meta-Standard")}
    )
    consumer = make_repo(
        tmp_path,
        {
            "standards/README.md": readme(),
            "standards/alpha.md": card("Alpha"),
            "standards/standard.md": card("Standard"),
            "standards/index.md": catalog(
                [
                    bullet("standards/README.md", "Standards"),
                    bullet("standards/alpha.md", "Alpha"),
                    bullet("standards/standard.md", "Standard"),
                ]
            ),
        },
    )

    findings = sa.audit(consumer, fake_list_rules({}), hook_repo_root=upstream)

    assert [f.rule for f in findings] == [sa.CARD_SHADOWS]


def test_canonical_template_alone_puts_repo_in_dev_playbook_mode(
    tmp_path: Path,
) -> None:
    # The canonical template is the sole mode marker: a tree carrying it -- but no
    # standards/standard.md -- is in dev-playbook mode, so a card matching an
    # upstream stem is not treated as a shadow (the rule stays gated off).
    upstream = make_repo(tmp_path / "up", {"standards/build.md": card("Build")})
    devrepo = make_repo(
        tmp_path,
        {
            "standards/README.md": readme(),
            "standards/build.md": card("Build"),
            "standards/build/canonical/.pre-commit-config.yaml": _canonical([]),
            "standards/index.md": catalog(
                [
                    bullet("standards/README.md", "Standards"),
                    bullet("standards/build.md", "Build"),
                ]
            ),
        },
    )

    # roster=() as in the shadow-rule walk test: the fixture cites no detectors.
    findings = sa.audit(
        devrepo, fake_list_rules({}), hook_repo_root=upstream, roster=()
    )

    assert findings == []


def test_list_rules_prints_every_rule(capsys: pytest.CaptureFixture[str]) -> None:
    assert sa.main(["--list-rules"]) == 0

    lines = [line for line in capsys.readouterr().out.splitlines() if line.strip()]

    assert sorted(lines) == sorted(sa.RULES)
    assert sa.CARD_SHADOWS in lines


def test_dev_playbook_scans_itself_clean(capsys: pytest.CaptureFixture[str]) -> None:
    # dev-playbook mode on dev-playbook itself: the real standards/ tree and the
    # promoted hook config agree across every surface.
    repo = Path(sa.__file__).resolve().parents[2]

    code = sa.main([str(repo)])

    assert code == 0, capsys.readouterr().out


def test_malformed_card_frontmatter_cannot_run(tmp_path: Path) -> None:
    # Unreadable frontmatter is a can't-run condition (exit 2), not a crash.
    repo = make_repo(
        tmp_path, {"standards/build.md": "---\ntype: [unterminated\n---\n\n# Build\n"}
    )

    with pytest.raises(sa.CannotRun):
        sa.check_card_layout(repo)


def test_dangling_catalog_target_cannot_run(tmp_path: Path) -> None:
    # A catalog bullet pointing at a nonexistent card must surface as CannotRun,
    # not an uncaught FileNotFoundError.
    files = ordered_repo_files({})
    files["standards/index.md"] = catalog(
        [
            bullet("standards/README.md", "Standards"),
            bullet("standards/standard.md", "Meta-Standard"),
            bullet("standards/ghost.md", "Ghost"),  # no such file
            bullet("standards/build.md", "Build"),
            bullet("standards/python.md", "Python"),
            bullet("standards/standard/format.md", "Standards and Standard Cards"),
        ]
    )
    repo = make_repo(tmp_path, files)

    with pytest.raises(sa.CannotRun):
        sa.check_catalog_order(repo, dev_playbook_mode=True)


def test_missing_catalog_cannot_run(tmp_path: Path) -> None:
    # An absent catalog is a can't-run condition, not silently clean.
    repo = make_repo(tmp_path, {"standards/build.md": card("Build")})

    with pytest.raises(sa.CannotRun):
        sa.check_catalog_order(repo, dev_playbook_mode=False)


# --- the optional standards/ surface ----------------------------------------


def test_repo_with_no_standards_surface_exits_clean(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # No catalog and no flat card: nothing to police, so exit 0 with no findings
    # rather than can't-run on the absent catalog.
    repo = make_repo(tmp_path, {"README.md": "# root\n"})

    assert sa.main([str(repo)]) == 0
    assert capsys.readouterr().out == ""


def test_repo_with_cards_but_no_catalog_exits_two(tmp_path: Path) -> None:
    # A card without a catalog is a malformed surface, never a silent skip.
    repo = make_repo(tmp_path, {"standards/build.md": card("Build")})

    assert sa.main([str(repo)]) == 2


def test_main_exits_two_on_a_dangling_catalog_link(tmp_path: Path) -> None:
    files = ordered_repo_files({})
    files["standards/index.md"] = catalog(
        [
            bullet("standards/README.md", "Standards"),
            bullet("standards/standard.md", "Meta-Standard"),
            bullet("standards/ghost.md", "Ghost"),  # no such file
            bullet("standards/build.md", "Build"),
            bullet("standards/python.md", "Python"),
            bullet("standards/standard/format.md", "Standards and Standard Cards"),
        ]
    )
    repo = make_repo(tmp_path, files)

    assert sa.main([str(repo)]) == 2


# --- the subprocess boundary ------------------------------------------------


def test_a_spawned_detector_does_not_inherit_the_hook_ambient_git_dir(
    tmp_path: Path, ambient_git_dir: Callable[[str], Path]
) -> None:
    # standards-lint runs at a git gate and can inherit an absolute GIT_DIR the
    # hook exports; a consumer detector it spawns must not receive it, or the
    # detector's own git calls answer for the hook's repo instead of the audited
    # one. A cited detector records the git dir it resolves to; with the
    # redirecting variables scrubbed it names the audited root, not the decoy the
    # ambient GIT_DIR points at.
    files = ordered_repo_files({})
    files["standards/index.md"] = catalog(
        [
            bullet("standards/README.md", "Standards"),
            bullet("standards/standard.md", "Meta-Standard"),
            bullet("standards/build.md", "Build"),
            bullet("standards/python.md", "Python"),
            bullet("standards/standard/format.md", "Standards and Standard Cards"),
        ]
    )
    files["standards/foo.md"] = card_citing("Foo", [cite("foo")])
    files["scripts/foo"] = (
        "#!/usr/bin/env bash\ngit rev-parse --absolute-git-dir > git-dir-seen\n"
    )
    files[".pre-commit-hooks.yaml"] = _manifest([])
    files[".pre-commit-config.yaml"] = _local_block([])
    files["standards/build/canonical/.pre-commit-config.yaml"] = _canonical([])
    files["scripts/README.md"] = _readme_table([])
    repo = make_repo(tmp_path, files)
    (repo / "scripts" / "foo").chmod(0o755)
    decoy = ambient_git_dir("leaked.txt")

    sa.main([str(repo)])

    seen = Path((repo / "git-dir-seen").read_text().strip()).resolve()
    assert seen == (repo / ".git").resolve()
    assert seen != (decoy / ".git").resolve()


def test_a_hung_detector_fails_the_gate_loudly_without_hanging(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # A detector that hangs on --list-rules must fail the commit gate loudly,
    # not block it forever: the timeout converts to a CannotRun the matrix
    # surfaces as a "does not answer --list-rules" finding.
    files = ordered_repo_files({})
    files["standards/index.md"] = catalog(
        [
            bullet("standards/README.md", "Standards"),
            bullet("standards/standard.md", "Meta-Standard"),
            bullet("standards/build.md", "Build"),
            bullet("standards/python.md", "Python"),
            bullet("standards/standard/format.md", "Standards and Standard Cards"),
        ]
    )
    files["standards/foo.md"] = card_citing("Foo", [cite("foo")])
    files["scripts/foo"] = "#!/usr/bin/env bash\n"
    # Empty, agreeing hook surfaces so hook-surfaces produces no findings and
    # does not mask the matrix finding the timeout produces.
    files[".pre-commit-hooks.yaml"] = _manifest([])
    files[".pre-commit-config.yaml"] = _local_block([])
    files["standards/build/canonical/.pre-commit-config.yaml"] = _canonical([])
    files["scripts/README.md"] = _readme_table([])
    repo = make_repo(tmp_path, files)

    real_run = subprocess.run

    def hang(cmd: Any, *args: Any, **kwargs: Any) -> Any:
        # Only the detector's --list-rules call hangs; git ls-files runs for real.
        if "--list-rules" in cmd:
            raise subprocess.TimeoutExpired(cmd=cmd, timeout=10)
        return real_run(cmd, *args, **kwargs)

    monkeypatch.setattr(sa.subprocess, "run", hang)

    assert sa.main([str(repo)]) == 1
    assert "--list-rules" in capsys.readouterr().out


def test_directory_before_a_document_flagged(tmp_path: Path) -> None:
    files = ordered_repo_files(
        {"standards/knowledge-organization/index.md": "# docs\n"}
    )
    files["standards/index.md"] = catalog(
        [
            bullet("standards/README.md", "Standards"),
            bullet("standards/standard.md", "Meta-Standard"),
            bullet("standards/knowledge-organization/index.md", "docs/"),
            bullet("standards/build.md", "Build"),
            bullet("standards/python.md", "Python"),
            bullet("standards/standard/format.md", "Standards and Standard Cards"),
        ]
    )
    repo = make_repo(tmp_path, files)

    findings = sa.check_catalog_order(repo, dev_playbook_mode=True)

    assert [f.rule for f in findings] == [sa.CATALOG_ORDER]
