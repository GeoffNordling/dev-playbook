"""Behavioral tests for the standards-lint detector (the meta-standard's rules).

standards-lint is a published hook: it audits the ``standards/`` tree of any
repo, in dev-playbook mode (keyed by the canonical consumer template) or
consumer mode (everything else). Each check function takes a repo root and
returns findings; discovery goes through ``git ls-files``, so every fixture is
a git repo. Consumer-mode fixtures pass a synthetic upstream root, so the shadow
rule is exercised without a second checkout.
"""

import subprocess
from pathlib import Path

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


def remit_of(title: str) -> str:
    """The opening sentence ``std_index`` gives a directory by default, less its period."""
    return f"{title} governs how {title.lower()} is done"


def standard(
    title: str,
    *,
    type_: str = "Standard",
    population: str | None = "every member",
) -> str:
    """A file typed ``Standard`` (by default) with one rule.

    ``population=None`` omits the key, which ``standard.the-population`` flags.
    """
    pop = "" if population is None else f'population: "{population}"\n'
    return (
        f"---\ntype: {type_}\ntitle: {title}\ndescription: {title}\n{pop}---\n\n"
        f"# {title}\n\n## One rule\n\nEvery member is so.\n\n"
        f"`{title.lower()}.one-rule` · deterministic\n"
    )


def explanation(title: str) -> str:
    """A file typed ``Explanation``."""
    return (
        f"---\ntype: Explanation\ntitle: {title} Explanation\ndescription: why\n---\n\n"
        f"# {title} Explanation\n\nBecause.\n"
    )


def std_index(name: str, title: str, *, intro: str | None = None) -> str:
    """A Standard directory's index: an opening sentence, then its members."""
    intro = intro if intro is not None else f"{remit_of(title)}."
    return (
        f"# standards/{name}/ — index\n\n{intro}\n\n"
        f"- [{title}](/standards/{name}/rules.md) — {title}\n"
    )


def std_dir(
    name: str, title: str, *, population: str | None = "every member"
) -> dict[str, str]:
    """A conformant Standard directory: one Standard and its ``index.md``."""
    return {
        f"standards/{name}/rules.md": standard(title, population=population),
        f"standards/{name}/index.md": std_index(name, title),
    }


def readme() -> str:
    """A conformant standards/README.md fixture."""
    return "---\ntype: README\ntitle: Standards\ndescription: s\n---\n\n# Standards\n"


# --- standard.directory-layout and standard.the-population -----------------------


def test_well_formed_directory_passes_directory_layout(tmp_path: Path) -> None:
    files = std_dir("build", "Build")
    files["standards/build/explanation.md"] = explanation("Build")
    repo = make_repo(tmp_path, files)

    assert sa.check_directory_layout(repo) == []


def test_unadmitted_member_of_a_standard_directory_is_flagged(tmp_path: Path) -> None:
    # A Standard directory admits a Standard or an Explanation, and nothing else.
    files = std_dir("build", "Build")
    files["standards/build/notes.md"] = (
        "---\ntype: General-Sheet\ntitle: Notes\ndescription: n\n---\n\n# Notes\n"
    )
    repo = make_repo(tmp_path, files)

    findings = sa.check_directory_layout(repo)

    assert [f.rule for f in findings] == [sa.DIRECTORY_LAYOUT]
    assert findings[0].file == "standards/build/notes.md"
    assert "General-Sheet" in findings[0].message


def test_a_leftover_card_is_an_unadmitted_member(tmp_path: Path) -> None:
    # The retired card, typed Standard-Card, is no longer admitted anywhere.
    files = std_dir("build", "Build")
    files["standards/build/card.md"] = (
        "---\ntype: Standard-Card\ntitle: Build\ndescription: b\n---\n\n# Build\n"
    )
    repo = make_repo(tmp_path, files)

    findings = sa.check_directory_layout(repo)

    assert [f.rule for f in findings] == [sa.DIRECTORY_LAYOUT]
    assert findings[0].file == "standards/build/card.md"


def test_flat_standards_file_is_flagged_as_a_stray(tmp_path: Path) -> None:
    # A Standard is standards/<name>/<topic>.md; a flat standards/<name>.md is
    # the old layout.
    repo = make_repo(tmp_path, {"standards/build.md": standard("Build")})

    findings = sa.check_directory_layout(repo)

    assert [f.rule for f in findings] == [sa.DIRECTORY_LAYOUT]
    assert findings[0].file == "standards/build.md"
    assert "flat" in findings[0].message


def test_readme_and_index_are_not_strays(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "standards/README.md": readme(),
            "standards/index.md": "# index\n\n- x\n",
        },
    )

    assert sa.check_directory_layout(repo) == []


def test_directory_without_a_standard_is_flagged(tmp_path: Path) -> None:
    # One directory, one Standard: a directory under standards/ holds one.
    repo = make_repo(
        tmp_path,
        {
            "standards/build/index.md": "# build\n",
            "standards/build/explanation.md": explanation("Build"),
        },
    )

    findings = sa.check_directory_layout(repo)

    assert [f.rule for f in findings] == [sa.DIRECTORY_LAYOUT]
    assert findings[0].file == "standards/build"
    assert "Standard" in findings[0].message


def test_standard_without_a_population_is_flagged(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, std_dir("build", "Build", population=None))

    findings = sa.check_directory_layout(repo)

    assert [f.rule for f in findings] == [sa.THE_POPULATION]
    assert findings[0].file == "standards/build/rules.md"


def test_nested_standard_counts_for_its_directory(tmp_path: Path) -> None:
    # A Standard's special cases may sit in a subdirectory; the directory still
    # holds a Standard.
    repo = make_repo(
        tmp_path,
        {
            "standards/build/index.md": "# build\n",
            "standards/build/sets/sets.md": standard("Sets"),
        },
    )

    assert sa.check_directory_layout(repo) == []


# --- standard.the-catalog -------------------------------------------------


def catalog(dir_bullets: list[str], *, readme_first: bool = True) -> str:
    """A standards/index.md: README, then the given directory bullets."""
    intro = "# standards\n\nOrdering: README, meta, directories by name.\n\n"
    readme_row = "- [Standards](/standards/README.md) — s\n"
    dirs = "\n## Directories\n\n" + "\n".join(dir_bullets) + "\n"
    if readme_first:
        return intro + readme_row + dirs
    return intro + dirs + "\n" + readme_row


def dir_bullet(name: str, title: str, description: str | None = None) -> str:
    """One catalog row for a Standard directory, carrying its index's opening sentence."""
    description = description if description is not None else remit_of(title)
    return f"- [{name}/](/standards/{name}/index.md) — {description}"


def bullet(target: str, title: str) -> str:
    """One index bullet linking title to a root-absolute target."""
    return f"- [{title}](/{target}) — desc"


def ordered_repo_files(extra: dict[str, str]) -> dict[str, str]:
    """The Standard directories a well-ordered dev-playbook catalog references.

    Carries the canonical template so full audits over these files run in
    dev-playbook mode -- the template is the mode marker.
    """
    return {
        "standards/README.md": readme(),
        **std_dir("standard", "Meta-Standard"),
        **std_dir("build", "Build"),
        **std_dir("python", "Python"),
        "standards/build/canonical/.pre-commit-config.yaml": _canonical([]),
        **extra,
    }


def dev_catalog() -> str:
    """The well-ordered catalog over ``ordered_repo_files``."""
    return catalog(
        [
            dir_bullet("standard", "Meta-Standard"),
            dir_bullet("build", "Build"),
            dir_bullet("python", "Python"),
        ]
    )


def test_catalog_in_declared_order_passes(tmp_path: Path) -> None:
    files = ordered_repo_files({"standards/index.md": dev_catalog()})
    repo = make_repo(tmp_path, files)

    assert sa.check_catalog_order(repo, dev_playbook_mode=True) == []


def test_readme_not_first_is_flagged(tmp_path: Path) -> None:
    files = ordered_repo_files({})
    files["standards/index.md"] = catalog(
        [
            dir_bullet("standard", "Meta-Standard"),
            dir_bullet("build", "Build"),
            dir_bullet("python", "Python"),
        ],
        readme_first=False,
    )
    repo = make_repo(tmp_path, files)

    findings = sa.check_catalog_order(repo, dev_playbook_mode=True)

    assert [f.rule for f in findings] == [sa.THE_CATALOG]


def test_directories_out_of_alphabetical_order_flagged(tmp_path: Path) -> None:
    files = ordered_repo_files({})
    files["standards/index.md"] = catalog(
        [
            dir_bullet("standard", "Meta-Standard"),
            dir_bullet("python", "Python"),
            dir_bullet("build", "Build"),
        ]
    )
    repo = make_repo(tmp_path, files)

    findings = sa.check_catalog_order(repo, dev_playbook_mode=True)

    assert [f.rule for f in findings] == [sa.THE_CATALOG]


def test_meta_standard_not_leading_is_flagged(tmp_path: Path) -> None:
    files = ordered_repo_files({})
    files["standards/index.md"] = catalog(
        [
            dir_bullet("build", "Build"),
            dir_bullet("python", "Python"),
            dir_bullet("standard", "Meta-Standard"),
        ]
    )
    repo = make_repo(tmp_path, files)

    findings = sa.check_catalog_order(repo, dev_playbook_mode=True)

    assert [f.rule for f in findings] == [sa.THE_CATALOG]


def test_document_row_in_the_catalog_is_flagged(tmp_path: Path) -> None:
    # The catalog lists README and directories only: a Standard listed flat
    # is the old layout's contract row.
    files = ordered_repo_files({})
    files["standards/index.md"] = catalog(
        [
            dir_bullet("standard", "Meta-Standard"),
            bullet("standards/standard/rules.md", "Meta-Standard"),
            dir_bullet("build", "Build"),
            dir_bullet("python", "Python"),
        ]
    )
    repo = make_repo(tmp_path, files)

    findings = sa.check_catalog_order(repo, dev_playbook_mode=True)

    assert [f.rule for f in findings] == [sa.THE_CATALOG]
    assert "rules.md" in findings[0].message


def test_row_not_carrying_the_opening_sentence_is_flagged(tmp_path: Path) -> None:
    files = ordered_repo_files({})
    files["standards/index.md"] = catalog(
        [
            dir_bullet("standard", "Meta-Standard"),
            dir_bullet("build", "Build", description="The build standard"),
            dir_bullet("python", "Python"),
        ]
    )
    repo = make_repo(tmp_path, files)

    findings = sa.check_catalog_order(repo, dev_playbook_mode=True)

    assert [f.rule for f in findings] == [sa.THE_CATALOG]
    assert "verbatim" in findings[0].message
    assert "build/" in findings[0].message


def test_index_opening_sentence_wrapped_across_lines_is_flattened(
    tmp_path: Path,
) -> None:
    files = ordered_repo_files({"standards/index.md": dev_catalog()})
    files["standards/build/index.md"] = std_index(
        "build", "Build", intro="Build governs how build\nis done. Start here."
    )
    repo = make_repo(tmp_path, files)

    assert sa.check_catalog_order(repo, dev_playbook_mode=True) == []


def test_a_dotted_filename_does_not_end_the_opening_sentence(tmp_path: Path) -> None:
    # `CLAUDE.md` carries a period with no space after it, so the sentence runs
    # past it to the real terminator.
    files = ordered_repo_files({})
    files["standards/build/index.md"] = std_index(
        "build", "Build", intro="Build governs how CLAUDE.md is written."
    )
    files["standards/index.md"] = catalog(
        [
            dir_bullet("standard", "Meta-Standard"),
            dir_bullet("build", "Build", "Build governs how CLAUDE.md is written"),
            dir_bullet("python", "Python"),
        ]
    )
    repo = make_repo(tmp_path, files)

    assert sa.check_catalog_order(repo, dev_playbook_mode=True) == []


def test_index_with_no_opening_sentence_is_flagged(tmp_path: Path) -> None:
    files = ordered_repo_files({"standards/index.md": dev_catalog()})
    files["standards/build/index.md"] = "# standards/build/ — index\n"
    repo = make_repo(tmp_path, files)

    findings = sa.check_catalog_order(repo, dev_playbook_mode=True)

    assert [f.rule for f in findings] == [sa.THE_CATALOG]
    assert findings[0].file == "standards/build/index.md"


def consumer_catalog_files(dir_bullets: list[str]) -> dict[str, str]:
    """A consumer standards/ tree: README + own directories, no meta-standard."""
    return {
        "standards/README.md": readme(),
        **std_dir("alpha", "Alpha"),
        **std_dir("beta", "Beta"),
        "standards/index.md": catalog(dir_bullets),
    }


def test_consumer_catalog_readme_then_own_directories_passes(tmp_path: Path) -> None:
    # No meta-standard: the catalog leads with README, then its own directories
    # by name. The meta row is data-driven, so its absence is not a defect.
    repo = make_repo(
        tmp_path,
        consumer_catalog_files(
            [dir_bullet("alpha", "Alpha"), dir_bullet("beta", "Beta")]
        ),
    )

    assert sa.check_catalog_order(repo, dev_playbook_mode=False) == []


def test_consumer_catalog_directories_out_of_order_flagged(tmp_path: Path) -> None:
    # README-first and alphabetical still bind in consumer mode; only the
    # meta row is optional.
    repo = make_repo(
        tmp_path,
        consumer_catalog_files(
            [dir_bullet("beta", "Beta"), dir_bullet("alpha", "Alpha")]
        ),
    )

    findings = sa.check_catalog_order(repo, dev_playbook_mode=False)

    assert [f.rule for f in findings] == [sa.THE_CATALOG]


# --- standard.the-hosting-pattern -------------------------------------------------


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
    manifest_system_ids: list[str] | None = None,
) -> Path:
    """Assemble a repo with the published-hook surfaces."""
    files = {
        ".pre-commit-hooks.yaml": _manifest(manifest_ids, manifest_system_ids),
        ".pre-commit-config.yaml": _local_block(local_ids),
        "standards/build/canonical/.pre-commit-config.yaml": _canonical(canonical_ids),
        "scripts/README.md": _readme_table(readme_ids),
    }
    return make_repo(tmp_path, files)


# The published world: standards-lint is now a published detector, and
# validate-manifest a published non-detector (language: system).
ALL = ["repo-lint", "okf-lint", "standards-lint"]
SYSTEM = ["validate-manifest"]


def test_agreeing_hook_surfaces_pass(tmp_path: Path) -> None:
    # Every published detector sits in the manifest, the local block, the
    # canonical pinned block, and the README table; the published non-detector
    # sits in the manifest and the pinned block.
    repo = surfaces_repo(
        tmp_path,
        manifest_ids=ALL,
        manifest_system_ids=SYSTEM,
        local_ids=ALL,
        canonical_ids=[*ALL, *SYSTEM],
        readme_ids=ALL,
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
    )

    findings = sa.check_hook_surfaces(repo, dev_playbook_mode=True, roster=tuple(ALL))

    assert sa.THE_HOSTING_PATTERN in {f.rule for f in findings}
    assert any("okf-lint" in f.message for f in findings)


def test_local_detector_not_in_manifest_is_flagged(tmp_path: Path) -> None:
    # A local detector absent from the manifest is a defect in both directions.
    repo = surfaces_repo(
        tmp_path,
        manifest_ids=["repo-lint", "okf-lint"],  # standards-lint unpublished
        manifest_system_ids=SYSTEM,
        local_ids=ALL,  # but present in the local block
        canonical_ids=["repo-lint", "okf-lint", *SYSTEM],
        readme_ids=ALL,
    )

    findings = sa.check_hook_surfaces(repo, dev_playbook_mode=True, roster=tuple(ALL))

    assert any(
        "standards-lint" in f.message and f.rule == sa.THE_HOSTING_PATTERN
        for f in findings
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
    )

    findings = sa.check_hook_surfaces(repo, dev_playbook_mode=True, roster=tuple(ALL))

    assert any(
        "okf-lint" in f.message and f.rule == sa.OFFERED_BY_THE_CANONICAL_TEMPLATE
        for f in findings
    )


def test_detector_hook_missing_from_readme_table_is_flagged(tmp_path: Path) -> None:
    repo = surfaces_repo(
        tmp_path,
        manifest_ids=ALL,
        manifest_system_ids=SYSTEM,
        local_ids=ALL,
        canonical_ids=[*ALL, *SYSTEM],
        readme_ids=["repo-lint", "standards-lint"],  # okf-lint missing
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
    )

    findings = sa.check_hook_surfaces(repo, dev_playbook_mode=True, roster=tuple(ALL))

    assert any(
        "stray-lint" in f.message and f.rule == sa.OFFERED_BY_THE_CANONICAL_TEMPLATE
        for f in findings
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
    repo = make_repo(tmp_path, files)

    findings = sa.check_hook_surfaces(repo, dev_playbook_mode=True, roster=tuple(ALL))

    assert any(
        "okf-lint" in f.message and "canonical" in f.message.lower() for f in findings
    )


def test_aggregate_hook_shape_passes(tmp_path: Path) -> None:
    # The published world: one aggregate hook in the manifest, the local block,
    # and the canonical pinned block; the roster detectors are rowed. The
    # aggregate hook itself owes no README row.
    repo = surfaces_repo(
        tmp_path,
        manifest_ids=["agg-lint"],
        local_ids=["agg-lint"],
        canonical_ids=["agg-lint"],
        readme_ids=ALL,
    )

    assert sa.check_hook_surfaces(repo, dev_playbook_mode=True, roster=tuple(ALL)) == []


# --- hook-surfaces: consumer mode ---


def _consumer_surfaces_files(
    *, manifest_ids: list[str], local_ids: list[str]
) -> dict[str, str]:
    """A consumer's own manifest + local block, no canonical/README."""
    return {
        ".pre-commit-hooks.yaml": _manifest(manifest_ids),
        ".pre-commit-config.yaml": _local_block(local_ids),
    }


def test_consumer_mode_agreeing_surfaces_pass(tmp_path: Path) -> None:
    # A consumer with its own manifest + local block, no canonical template and
    # no scripts/README.md: the mirror runs and passes; the canonical and README
    # sub-checks are silent.
    repo = make_repo(
        tmp_path,
        _consumer_surfaces_files(manifest_ids=["own-lint"], local_ids=["own-lint"]),
    )

    assert sa.check_hook_surfaces(repo, dev_playbook_mode=False) == []


def test_consumer_mode_mirror_still_flags_local_not_in_manifest(tmp_path: Path) -> None:
    # The manifest <-> local mirror runs uniformly in both modes.
    repo = make_repo(
        tmp_path,
        _consumer_surfaces_files(
            manifest_ids=["own-lint"],
            local_ids=["own-lint", "extra-lint"],  # extra-lint unpublished
        ),
    )

    findings = sa.check_hook_surfaces(repo, dev_playbook_mode=False)

    assert any(
        "extra-lint" in f.message and f.rule == sa.THE_HOSTING_PATTERN for f in findings
    )


def test_consumer_mode_ignores_a_canonical_template(tmp_path: Path) -> None:
    # A consumer that happens to carry a canonical template gets no canonical
    # findings: the canonical leg is dev-playbook-only.
    files = _consumer_surfaces_files(manifest_ids=["own-lint"], local_ids=["own-lint"])
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
    # Own directories + catalog, no .pre-commit-hooks.yaml and no
    # .pre-commit-config.yaml: both absent surface files read as empty, so a
    # consumer that publishes no hooks of its own audits clean rather than
    # bricking its gate at exit 2.
    upstream = make_repo(tmp_path / "up", {"README.md": "# up\n"})
    consumer = make_repo(
        tmp_path,
        consumer_catalog_files(
            [dir_bullet("alpha", "Alpha"), dir_bullet("beta", "Beta")]
        ),
    )

    assert sa.audit(consumer, hook_repo_root=upstream) == []


# --- standard.no-shadowing -----------------------------------------


def test_local_directory_shadowing_an_upstream_one_is_flagged(tmp_path: Path) -> None:
    # The consumer's standards/build/ reuses an upstream directory name,
    # silently overriding dev-playbook's Standard of that name.
    upstream = make_repo(tmp_path / "up", std_dir("build", "Build"))
    consumer = make_repo(tmp_path, std_dir("build", "Build"))

    findings = sa.check_shadows_upstream(consumer, upstream)

    assert [f.rule for f in findings] == [sa.NO_SHADOWING]
    assert findings[0].file == "standards/build"


def test_local_directory_with_a_fresh_name_is_not_flagged(tmp_path: Path) -> None:
    upstream = make_repo(tmp_path / "up", std_dir("build", "Build"))
    consumer = make_repo(tmp_path, std_dir("widget", "Widget"))

    assert sa.check_shadows_upstream(consumer, upstream) == []


def test_shadow_scan_non_git_hook_repo_root_cannot_run(tmp_path: Path) -> None:
    # If the clone the hook ships in is not a git checkout, the upstream scan's
    # git ls-files fails; that funnels into CannotRun (exit 2), not an uncaught
    # CalledProcessError traceback.
    non_git = tmp_path / "not-a-checkout"
    non_git.mkdir()
    consumer = make_repo(tmp_path, std_dir("build", "Build"))

    with pytest.raises(sa.CannotRun):
        sa.check_shadows_upstream(consumer, non_git)


def test_audit_non_git_root_cannot_run(tmp_path: Path) -> None:
    # The optional-surface guard scans the audited root via git ls-files; a
    # non-git root funnels into CannotRun (exit 2) at the same _tracked
    # chokepoint as the upstream scan, never an uncaught CalledProcessError.
    non_git = tmp_path / "not-a-checkout"
    non_git.mkdir()

    with pytest.raises(sa.CannotRun):
        sa.audit(non_git)


def _clean_bundle(tmp_path: Path, *, dev_playbook_mode: bool) -> Path:
    """A conformant standards/ bundle carrying a 'build' directory, clean on its own.

    In dev-playbook mode it also carries the meta-standard's directory and a
    canonical template, so hook-surfaces' dev-playbook-only leg has files to
    read; in consumer mode it omits both. The bundle is clean under every rule
    but the shadow rule.
    """
    files = {
        "standards/README.md": readme(),
        **std_dir("build", "Build"),
        ".pre-commit-hooks.yaml": "",
        ".pre-commit-config.yaml": _local_block([]),
    }
    dir_bullets = []
    if dev_playbook_mode:
        files.update(std_dir("standard", "Meta-Standard"))
        files["standards/build/canonical/.pre-commit-config.yaml"] = _canonical([])
        dir_bullets.append(dir_bullet("standard", "Meta-Standard"))
    dir_bullets.append(dir_bullet("build", "Build"))
    files["standards/index.md"] = catalog(dir_bullets)
    return make_repo(tmp_path, files)


def test_consumer_mode_audit_flags_a_shadowing_directory(tmp_path: Path) -> None:
    # End to end: an otherwise-clean consumer whose only defect is a shadowing
    # directory gets exactly the shadow finding.
    upstream = make_repo(tmp_path / "up", std_dir("build", "Build"))
    consumer = _clean_bundle(tmp_path, dev_playbook_mode=False)

    findings = sa.audit(consumer, hook_repo_root=upstream)

    assert [f.rule for f in findings] == [sa.NO_SHADOWING]


def test_dev_playbook_mode_audit_never_runs_the_shadow_rule(tmp_path: Path) -> None:
    # The same 'build' name in dev-playbook mode is not a shadow: dev-playbook's
    # own directories cannot shadow themselves, so the rule is gated off.
    upstream = make_repo(tmp_path / "up", std_dir("build", "Build"))
    devrepo = _clean_bundle(tmp_path, dev_playbook_mode=True)

    # roster=() keeps the fixture self-contained: it carries no README table.
    findings = sa.audit(devrepo, hook_repo_root=upstream, roster=())

    assert findings == []


def test_consumer_directory_named_standard_is_flagged_as_a_shadow(
    tmp_path: Path,
) -> None:
    # The mode marker is the canonical template, not standards/standard/, so a
    # consumer directory of that name stays in consumer mode and the shadow rule
    # catches it.
    upstream = make_repo(tmp_path / "up", std_dir("standard", "Meta-Standard"))
    consumer = make_repo(
        tmp_path,
        {
            "standards/README.md": readme(),
            **std_dir("alpha", "Alpha"),
            **std_dir("standard", "Standard"),
            "standards/index.md": catalog(
                [dir_bullet("alpha", "Alpha"), dir_bullet("standard", "Standard")]
            ),
        },
    )

    findings = sa.audit(consumer, hook_repo_root=upstream)

    # In consumer mode standards/standard/ sorts among the others by name, so
    # the sole finding is the shadow, never a catalog-order complaint.
    assert [f.rule for f in findings] == [sa.NO_SHADOWING]
    assert findings[0].file == "standards/standard"


def test_canonical_template_alone_puts_repo_in_dev_playbook_mode(
    tmp_path: Path,
) -> None:
    # The canonical template is the sole mode marker: a tree carrying it -- but
    # no standards/standard/ -- is in dev-playbook mode, so a directory matching
    # an upstream name is not treated as a shadow (the rule stays gated off).
    upstream = make_repo(tmp_path / "up", std_dir("build", "Build"))
    devrepo = make_repo(
        tmp_path,
        {
            "standards/README.md": readme(),
            **std_dir("build", "Build"),
            "standards/build/canonical/.pre-commit-config.yaml": _canonical([]),
            "standards/index.md": catalog([dir_bullet("build", "Build")]),
        },
    )

    findings = sa.audit(devrepo, hook_repo_root=upstream, roster=())

    assert findings == []


def test_list_rules_prints_every_rule(capsys: pytest.CaptureFixture[str]) -> None:
    assert sa.main(["--list-rules"]) == 0

    lines = [line for line in capsys.readouterr().out.splitlines() if line.strip()]

    assert sorted(lines) == sorted(sa.RULES)
    assert sa.NO_SHADOWING in lines


def test_dev_playbook_scans_itself_clean(capsys: pytest.CaptureFixture[str]) -> None:
    # dev-playbook mode on dev-playbook itself: the real standards/ tree and the
    # promoted hook config agree across every surface.
    repo = Path(sa.__file__).resolve().parents[2]

    code = sa.main([str(repo)])

    assert code == 0, capsys.readouterr().out


def test_malformed_frontmatter_cannot_run(tmp_path: Path) -> None:
    # Unreadable frontmatter is a can't-run condition (exit 2), not a crash.
    repo = make_repo(
        tmp_path,
        {"standards/build/rules.md": "---\ntype: [unterminated\n---\n\n# Build\n"},
    )

    with pytest.raises(sa.CannotRun):
        sa.check_directory_layout(repo)


def test_dangling_catalog_target_cannot_run(tmp_path: Path) -> None:
    # A catalog bullet pointing at a nonexistent directory must surface as
    # CannotRun, not an uncaught FileNotFoundError.
    files = ordered_repo_files({})
    files["standards/index.md"] = catalog(
        [
            dir_bullet("standard", "Meta-Standard"),
            dir_bullet("build", "Build"),
            dir_bullet("ghost", "Ghost"),  # no such directory
            dir_bullet("python", "Python"),
        ]
    )
    repo = make_repo(tmp_path, files)

    with pytest.raises(sa.CannotRun):
        sa.check_catalog_order(repo, dev_playbook_mode=True)


def test_missing_catalog_cannot_run(tmp_path: Path) -> None:
    # An absent catalog is a can't-run condition, not silently clean.
    repo = make_repo(tmp_path, std_dir("build", "Build"))

    with pytest.raises(sa.CannotRun):
        sa.check_catalog_order(repo, dev_playbook_mode=False)


# --- the optional standards/ surface ----------------------------------------


def test_repo_with_no_standards_surface_exits_clean(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # No catalog and no Standard directory: nothing to police, so exit 0 with
    # no findings rather than can't-run on the absent catalog.
    repo = make_repo(tmp_path, {"README.md": "# root\n"})

    assert sa.main([str(repo)]) == 0
    assert capsys.readouterr().out == ""


def test_repo_with_directories_but_no_catalog_exits_two(tmp_path: Path) -> None:
    # A Standard directory without a catalog is a malformed surface, never a
    # silent skip.
    repo = make_repo(tmp_path, std_dir("build", "Build"))

    assert sa.main([str(repo)]) == 2


def test_main_exits_two_on_a_dangling_catalog_link(tmp_path: Path) -> None:
    files = ordered_repo_files({})
    files["standards/index.md"] = catalog(
        [
            dir_bullet("standard", "Meta-Standard"),
            dir_bullet("build", "Build"),
            dir_bullet("ghost", "Ghost"),  # no such directory
            dir_bullet("python", "Python"),
        ]
    )
    repo = make_repo(tmp_path, files)

    assert sa.main([str(repo)]) == 2
