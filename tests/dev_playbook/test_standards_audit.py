"""Behavioral tests for the standards-audit detector (the meta-standard's rules).

standards-audit is dev-playbook-local: it audits the ``standards/`` tree that
only this repo carries. Each check function takes a repo root and returns
findings; discovery goes through ``git ls-files``, so every fixture is a git
repo. The rule-matrix check's ``--list-rules`` boundary is injected as a plain
callable, so the matrix logic is exercised without subprocessing real detectors.
"""

import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from dev_playbook import standards_audit as sa


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
    type_: str = "Standard Card",
    cells: tuple[str, ...] = ("Define", "Audit", "Enforce", "Adopt"),
) -> str:
    """A standard card with the given title, type, and cell sections."""
    front = (
        f"---\ntype: {type_}\ntitle: {title}\n"
        f"description: Card for the {title} standard\n---\n\n"
        f"# {title}\n\nGoverns {title}.\n"
    )
    return front + "".join(f"\n## {cell}\n\n- none\n" for cell in cells)


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
    """The card + contract files a well-ordered catalog references."""
    return {
        "standards/README.md": (
            "---\ntype: README\ntitle: Standards\ndescription: s\n---\n\n# Standards\n"
        ),
        "standards/standard.md": card("Meta-Standard"),
        "standards/build.md": card("Build"),
        "standards/python.md": card("Python"),
        "standards/standard/format.md": (
            "---\ntype: Standard\ntitle: Standards and Standard Cards\n"
            "description: d\n---\n\n# Standards and Standard Cards\n"
        ),
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

    assert sa.check_catalog_order(repo) == []


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

    findings = sa.check_catalog_order(repo)

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

    findings = sa.check_catalog_order(repo)

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

    findings = sa.check_catalog_order(repo)

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
        f"---\ntype: Standard Card\ntitle: {title}\n"
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
        tmp_path, {"standards/build.md": card_citing("Build", [cite("repo-audit")])}
    )

    findings = sa.check_rule_matrix(repo, fake_list_rules({"repo-audit": ["build.x"]}))

    assert findings == []


def test_uncited_emitted_prefix_fails_direction_one(tmp_path: Path) -> None:
    # repo-audit emits docs.y, but the docs card does not cite repo-audit.
    repo = make_repo(
        tmp_path,
        {
            "standards/build.md": card_citing("Build", [cite("repo-audit")]),
            "standards/docs.md": card_citing("Docs", ["- none"]),
        },
    )

    findings = sa.check_rule_matrix(
        repo, fake_list_rules({"repo-audit": ["build.x", "docs.y"]})
    )

    assert [f.rule for f in findings] == [sa.RULE_MATRIX]
    assert "docs.md" in findings[0].file


def test_unbacked_citation_fails_direction_two(tmp_path: Path) -> None:
    # The build card cites repo-audit, but repo-audit emits no build.* rule --
    # only docs.*, which the docs card legitimately cites.
    repo = make_repo(
        tmp_path,
        {
            "standards/build.md": card_citing("Build", [cite("repo-audit")]),
            "standards/docs.md": card_citing("Docs", [cite("repo-audit")]),
        },
    )

    findings = sa.check_rule_matrix(repo, fake_list_rules({"repo-audit": ["docs.y"]}))

    assert [f.rule for f in findings] == [sa.RULE_MATRIX]
    assert findings[0].file == "standards/build.md"


def test_cited_detector_without_list_rules_fails_membership(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path, {"standards/build.md": card_citing("Build", [cite("repo-audit")])}
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


def _manifest(ids: list[str]) -> str:
    return "".join(
        f"- id: {i}\n  name: {i}\n  entry: scripts/{i}\n  language: script\n"
        for i in ids
    )


def _local_block(ids: list[str]) -> str:
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
) -> Path:
    """Assemble a repo with the four hook surfaces and citing cards."""
    files = {
        ".pre-commit-hooks.yaml": _manifest(manifest_ids),
        ".pre-commit-config.yaml": _local_block(local_ids),
        "standards/build/canonical/.pre-commit-config.yaml": _canonical(canonical_ids),
        "scripts/README.md": _readme_table(readme_ids),
    }
    for i, name in enumerate(cited_ids):
        files[f"standards/c{i}.md"] = card_citing(f"C{i}", [cite(name)])
    return make_repo(tmp_path, files)


ALL = ["repo-audit", "okf-audit"]


def test_agreeing_hook_surfaces_pass(tmp_path: Path) -> None:
    repo = surfaces_repo(
        tmp_path,
        manifest_ids=ALL,
        local_ids=[*ALL, "standards-audit"],
        canonical_ids=ALL,
        readme_ids=[*ALL, "standards-audit"],
        cited_ids=[*ALL, "standards-audit"],
    )

    assert sa.check_hook_surfaces(repo) == []


def test_manifest_hook_missing_from_local_is_flagged(tmp_path: Path) -> None:
    repo = surfaces_repo(
        tmp_path,
        manifest_ids=ALL,
        local_ids=["repo-audit", "standards-audit"],  # okf-audit dropped
        canonical_ids=ALL,
        readme_ids=[*ALL, "standards-audit"],
        cited_ids=[*ALL, "standards-audit"],
    )

    findings = sa.check_hook_surfaces(repo)

    assert sa.HOOK_SURFACES in {f.rule for f in findings}
    assert any("okf-audit" in f.message for f in findings)


def test_manifest_hook_missing_from_canonical_is_flagged(tmp_path: Path) -> None:
    # The skill-audit-style violation: published, but not offered to consumers.
    repo = surfaces_repo(
        tmp_path,
        manifest_ids=ALL,
        local_ids=[*ALL, "standards-audit"],
        canonical_ids=["repo-audit"],  # okf-audit missing from the template
        readme_ids=[*ALL, "standards-audit"],
        cited_ids=[*ALL, "standards-audit"],
    )

    findings = sa.check_hook_surfaces(repo)

    assert any(
        "okf-audit" in f.message and f.rule == sa.HOOK_SURFACES for f in findings
    )


def test_local_only_detector_absent_elsewhere_is_not_flagged(tmp_path: Path) -> None:
    # standards-audit is local-only: absent from manifest and canonical by design.
    repo = surfaces_repo(
        tmp_path,
        manifest_ids=ALL,
        local_ids=[*ALL, "standards-audit"],
        canonical_ids=ALL,
        readme_ids=[*ALL, "standards-audit"],
        cited_ids=[*ALL, "standards-audit"],
    )

    findings = sa.check_hook_surfaces(repo)

    assert not any("standards-audit" in f.message for f in findings)


def test_detector_hook_missing_from_readme_table_is_flagged(tmp_path: Path) -> None:
    repo = surfaces_repo(
        tmp_path,
        manifest_ids=ALL,
        local_ids=[*ALL, "standards-audit"],
        canonical_ids=ALL,
        readme_ids=["repo-audit", "standards-audit"],  # okf-audit missing
        cited_ids=[*ALL, "standards-audit"],
    )

    findings = sa.check_hook_surfaces(repo)

    assert any("okf-audit" in f.message and "README" in f.message for f in findings)


def test_stray_id_in_canonical_dev_block_is_flagged(tmp_path: Path) -> None:
    # An id in the pinned dev-playbook block that the manifest never publishes
    # (a typo or a stale entry) must fail -- the reverse direction.
    repo = surfaces_repo(
        tmp_path,
        manifest_ids=ALL,
        local_ids=[*ALL, "standards-audit"],
        canonical_ids=[*ALL, "stray-audit"],  # not in the manifest
        readme_ids=[*ALL, "standards-audit"],
        cited_ids=[*ALL, "standards-audit"],
    )

    findings = sa.check_hook_surfaces(repo)

    assert any(
        "stray-audit" in f.message and f.rule == sa.HOOK_SURFACES for f in findings
    )


def test_manifest_detector_in_canonical_local_block_is_flagged(tmp_path: Path) -> None:
    # okf-audit sits in canonical's repo:local block, not the pinned dev-playbook
    # block, so a consumer would never get it wired -- it must fail as missing.
    canonical = (
        "repos:\n"
        "  - repo: https://github.com/GeoffNordling/dev-playbook\n"
        "    rev: <pinned-sha>\n    hooks:\n"
        "      - id: repo-audit\n"
        "  - repo: local\n    hooks:\n"
        "      - id: okf-audit\n        name: okf-audit\n"
        "        entry: scripts/okf-audit\n        language: script\n"
    )
    cited = [*ALL, "standards-audit"]
    files = {
        ".pre-commit-hooks.yaml": _manifest(ALL),
        ".pre-commit-config.yaml": _local_block([*ALL, "standards-audit"]),
        "standards/build/canonical/.pre-commit-config.yaml": canonical,
        "scripts/README.md": _readme_table([*ALL, "standards-audit"]),
    }
    for i, name in enumerate(cited):
        files[f"standards/c{i}.md"] = card_citing(f"C{i}", [cite(name)])
    repo = make_repo(tmp_path, files)

    findings = sa.check_hook_surfaces(repo)

    assert any(
        "okf-audit" in f.message and "canonical" in f.message.lower() for f in findings
    )


def test_detector_hook_cited_by_no_card_is_flagged(tmp_path: Path) -> None:
    repo = surfaces_repo(
        tmp_path,
        manifest_ids=ALL,
        local_ids=[*ALL, "standards-audit"],
        canonical_ids=ALL,
        readme_ids=[*ALL, "standards-audit"],
        cited_ids=["repo-audit", "standards-audit"],  # okf-audit cited by no card
    )

    findings = sa.check_hook_surfaces(repo)

    assert any("okf-audit" in f.message and "Audit cell" in f.message for f in findings)


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
        sa.check_catalog_order(repo)


def test_missing_catalog_cannot_run(tmp_path: Path) -> None:
    # An absent catalog is a can't-run condition, not silently clean.
    repo = make_repo(tmp_path, {"standards/build.md": card("Build")})

    with pytest.raises(sa.CannotRun):
        sa.check_catalog_order(repo)


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
    # Consistent hook surfaces so hook-surfaces does not can't-run and mask the
    # matrix finding the timeout produces.
    files[".pre-commit-hooks.yaml"] = _manifest([])
    files[".pre-commit-config.yaml"] = _local_block(["standards-audit"])
    files["standards/build/canonical/.pre-commit-config.yaml"] = _canonical([])
    files["scripts/README.md"] = _readme_table(["standards-audit"])
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
    files = ordered_repo_files({"standards/docs/index.md": "# docs\n"})
    files["standards/index.md"] = catalog(
        [
            bullet("standards/README.md", "Standards"),
            bullet("standards/standard.md", "Meta-Standard"),
            bullet("standards/docs/index.md", "docs/"),
            bullet("standards/build.md", "Build"),
            bullet("standards/python.md", "Python"),
            bullet("standards/standard/format.md", "Standards and Standard Cards"),
        ]
    )
    repo = make_repo(tmp_path, files)

    findings = sa.check_catalog_order(repo)

    assert [f.rule for f in findings] == [sa.CATALOG_ORDER]
