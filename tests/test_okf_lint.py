"""Behavioral tests for scripts/okf-lint.

okf-lint declares pyyaml via PEP 723 and imports the local dev_playbook package, so it
is invoked exactly the way pre-commit runs it: `uv run --script`.
"""

import os
import re
import subprocess
from pathlib import Path

OKF_LINT = Path(__file__).resolve().parents[1] / "scripts" / "okf-lint"

# A minimal but valid OKF bundle: a registry doc, two concept docs, a root
# index (with okf_version) and a standards index, all internally consistent.
# The canonical consumer template puts the bundle in APEX mode — the registry
# document is read and shape-checked from the audited tree — the same probe
# standards-lint keys its dev-playbook mode on. Every apex fixture rides this one
# line; without it the bundle would flip to consumer mode and its registry doc
# would be read as a local extension whose rows all shadow upstream.
BASE_BUNDLE: dict[str, str] = {
    "standards/build/canonical/.pre-commit-config.yaml": "repos: []\n",
    "README.md": (
        "---\ntype: README\ntitle: Root\ndescription: Root readme desc\n---\n\n# Root\n"
    ),
    "index.md": (
        '---\nokf_version: "0.1"\n---\n\n# bundle index\n\n'
        "- [Root](/README.md) — Root readme desc\n\n"
        "## Directories\n\n"
        "- [standards/](/standards/index.md) — Cross-project standards\n"
    ),
    "standards/README.md": (
        "---\ntype: README\ntitle: Standards\ndescription: Standards desc\n---\n\n"
        "# Standards\n"
    ),
    "standards/docs/document-types.md": (
        "---\ntype: Standard\ntitle: Document Types\n"
        "description: The document type registry\n---\n\n"
        "# Document Types\n\n## Types\n\n"
        "| Type | What it is |\n|------|------------|\n"
        "| `Guide` | teaching |\n| `README` | landing |\n"
        "| `Recipe-Description` | describes code |\n| `Standard` | rules |\n"
    ),
    "standards/index.md": (
        "# standards/ — index\n\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
        "- [Document Types](/standards/docs/document-types.md) — The document type registry\n"
    ),
}


def run_okf_lint(
    repo_root: Path, upstream_root: Path | None = None
) -> subprocess.CompletedProcess:
    """Run okf-lint over ``repo_root``.

    When ``upstream_root`` is given, pin okf-lint's upstream registry to it via
    ``OKF_LINT_UPSTREAM_ROOT`` so a consumer-mode test resolves a synthetic
    registry instead of dev-playbook's live one.
    """
    env = None
    if upstream_root is not None:
        env = {**os.environ, "OKF_LINT_UPSTREAM_ROOT": str(upstream_root)}
    return subprocess.run(
        ["uv", "run", "--script", str(OKF_LINT), str(repo_root)],
        capture_output=True,
        text=True,
        env=env,
    )


# A synthetic upstream registry a consumer-mode test pins via
# OKF_LINT_UPSTREAM_ROOT, so its assertions never depend on dev-playbook's live
# registry contents (which a future type rename or addition would otherwise break
# spuriously). It declares a small fixed vocabulary; the local extension names the
# consumer-extension tests use are chosen to sit outside it.
UPSTREAM_REGISTRY = (
    "---\ntype: Standard\ntitle: Document Types\n"
    "description: The document type registry\n---\n\n"
    "# Document Types\n\n## Types\n\n"
    "| Type | What it is |\n|------|------------|\n"
    "| `Guide` | teaching |\n| `README` | landing |\n"
    "| `Recipe-Description` | describes code |\n| `Standard` | rules |\n"
)


def make_upstream(tmp_path: Path) -> Path:
    """Write the synthetic upstream registry into a tree and return its root."""
    root = tmp_path / "upstream"
    doc = root / "standards" / "docs" / "document-types.md"
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text(UPSTREAM_REGISTRY)
    return root


def _write_bundle(
    tmp_path: Path, base: dict[str, str], overrides: dict[str, str | None]
) -> Path:
    """Write ``base`` into a fresh git repo under ``tmp_path``, applying overrides.

    An override value of None deletes that file; any other value replaces it.
    Every bundle factory (apex, consumer, consumer-extension, instrument) is a
    thin wrapper picking its base dict.
    """
    repo = tmp_path / "repo"
    files = dict(base)
    for path, content in overrides.items():
        if content is None:
            files.pop(path, None)
        else:
            files[path] = content
    for rel, content in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    return repo


def make_bundle(tmp_path: Path, overrides: dict[str, str | None]) -> Path:
    """Write BASE_BUNDLE (apex mode) into a fresh git repo, applying overrides."""
    return _write_bundle(tmp_path, BASE_BUNDLE, overrides)


def test_valid_bundle_is_clean(tmp_path: Path) -> None:
    repo = make_bundle(tmp_path, {})

    result = run_okf_lint(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "clean" in result.stderr


def test_missing_type_is_flagged(tmp_path: Path) -> None:
    repo = make_bundle(
        tmp_path,
        {
            "standards/README.md": "---\ntitle: Standards\ndescription: Standards desc\n---\n\n# S\n"
        },
    )

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert "standards/README.md" in result.stdout
    assert "missing 'type'" in result.stdout


def test_type_outside_registry_is_flagged(tmp_path: Path) -> None:
    repo = make_bundle(
        tmp_path,
        {
            "standards/README.md": "---\ntype: Bogus\ntitle: S\ndescription: Standards desc\n---\n\n# S\n"
        },
    )

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert "not in the registry" in result.stdout


def test_missing_description_is_flagged(tmp_path: Path) -> None:
    repo = make_bundle(
        tmp_path,
        {"standards/README.md": "---\ntype: README\ntitle: Standards\n---\n\n# S\n"},
    )

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert "missing 'description'" in result.stdout


def test_recipe_description_requires_resource(tmp_path: Path) -> None:
    recipe = "---\ntype: Recipe-Description\ntitle: Ralph\ndescription: A loop\n---\n\n# Ralph\n"
    index = (
        "# standards/ — index\n\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
        "- [Document Types](/standards/docs/document-types.md) — The document type registry\n"
        "- [Ralph](/standards/ralph.md) — A loop\n"
    )
    repo = make_bundle(
        tmp_path, {"standards/ralph.md": recipe, "standards/index.md": index}
    )

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert "requires a 'resource'" in result.stdout


def _root_index_listing(*extra: str) -> str:
    """The base root index with ``extra`` bullets added before the Directories section."""
    bullets = "".join(f"{line}\n" for line in extra)
    return (
        '---\nokf_version: "0.1"\n---\n\n# bundle index\n\n'
        "- [Root](/README.md) — Root readme desc\n"
        f"{bullets}\n"
        "## Directories\n\n"
        "- [standards/](/standards/index.md) — Cross-project standards\n"
    )


def test_standard_outside_standards_dir_is_flagged(tmp_path: Path) -> None:
    doc = "---\ntype: Standard\ntitle: Ops\ndescription: How ops runs\n---\n\n# Ops\n"
    repo = make_bundle(
        tmp_path,
        {
            "factory/ops.md": doc,
            "index.md": _root_index_listing("- [Ops](/factory/ops.md) — How ops runs"),
        },
    )

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert "knowledge-organization.type-location" in result.stdout
    assert "factory/ops.md" in result.stdout
    assert "'Standard' lives under standards/" in result.stdout


def test_standard_nested_under_standards_dir_is_clean(tmp_path: Path) -> None:
    doc = "---\ntype: Standard\ntitle: Ops\ndescription: How ops runs\n---\n\n# Ops\n"
    index = (
        "# standards/ — index\n\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
        "- [Document Types](/standards/docs/document-types.md) — The document type registry\n"
        "- [Ops](/standards/factory/ops.md) — How ops runs\n"
    )
    repo = make_bundle(
        tmp_path, {"standards/factory/ops.md": doc, "standards/index.md": index}
    )

    result = run_okf_lint(repo)

    assert result.returncode == 0, result.stdout + result.stderr


def test_non_standard_type_outside_standards_dir_is_clean(tmp_path: Path) -> None:
    """The rule binds the `Standard` label alone — every other type roams free."""
    doc = "---\ntype: Guide\ntitle: Ops\ndescription: How ops runs\n---\n\n# Ops\n"
    repo = make_bundle(
        tmp_path,
        {
            "factory/ops.md": doc,
            "index.md": _root_index_listing("- [Ops](/factory/ops.md) — How ops runs"),
        },
    )

    result = run_okf_lint(repo)

    assert result.returncode == 0, result.stdout + result.stderr


def test_index_omitting_a_concept_is_flagged(tmp_path: Path) -> None:
    index = (
        "# standards/ — index\n\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
    )  # drops the document-types.md line
    repo = make_bundle(tmp_path, {"standards/index.md": index})

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert "omits concept doc standards/docs/document-types.md" in result.stdout


def test_index_listing_missing_file_is_flagged(tmp_path: Path) -> None:
    index = BASE_BUNDLE["standards/index.md"] + "- [Gone](/standards/gone.md) — nope\n"
    repo = make_bundle(tmp_path, {"standards/index.md": index})

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert "standards/gone.md" in result.stdout
    assert "does not exist" in result.stdout


def test_index_description_drift_is_flagged(tmp_path: Path) -> None:
    index = (
        "# standards/ — index\n\n"
        "- [Standards](/standards/README.md) — WRONG description\n"
        "- [Document Types](/standards/docs/document-types.md) — The document type registry\n"
    )
    repo = make_bundle(tmp_path, {"standards/index.md": index})

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert "does not match its frontmatter" in result.stdout


def test_root_index_missing_okf_version_is_flagged(tmp_path: Path) -> None:
    index = (
        "# bundle index\n\n"
        "- [Root](/README.md) — Root readme desc\n\n"
        "## Directories\n\n"
        "- [standards/](/standards/index.md) — Cross-project standards\n"
    )
    repo = make_bundle(tmp_path, {"index.md": index})

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert "okf_version" in result.stdout


def test_root_index_omitting_child_index_is_flagged(tmp_path: Path) -> None:
    index = (
        '---\nokf_version: "0.1"\n---\n\n# bundle index\n\n'
        "- [Root](/README.md) — Root readme desc\n"
    )  # drops the standards/ child-index link
    repo = make_bundle(tmp_path, {"index.md": index})

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert "omits child index standards/index.md" in result.stdout


def test_malformed_frontmatter_is_flagged_and_siblings_still_lint(
    tmp_path: Path,
) -> None:
    """One doc's unparseable YAML yields a finding naming that doc, and the rest
    of the bundle is still validated — no traceback, no silent mass un-linting."""
    malformed = '---\ntitle: "unterminated\n---\n\n# S\n'
    missing_type = "---\ntitle: Root\ndescription: Root readme desc\n---\n\n# Root\n"
    repo = make_bundle(
        tmp_path,
        {"standards/README.md": malformed, "README.md": missing_type},
    )

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert "standards/README.md" in result.stdout
    assert "knowledge-organization.frontmatter" in result.stdout
    # The malformed doc did not abort the scan: the sibling problem is caught too.
    assert "missing 'type'" in result.stdout


def test_index_listing_non_concept_target_is_flagged(tmp_path: Path) -> None:
    """A bullet whose target is harness/excluded is neither a concept nor a
    child index — it is flagged, not silently dropped."""
    index = (
        "# standards/ — index\n\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
        "- [Document Types](/standards/docs/document-types.md) — The document type registry\n"
        "- [Rules](/standards/rules/naming.md) — not a concept doc\n"
    )
    repo = make_bundle(tmp_path, {"standards/index.md": index})

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert "standards/rules/naming.md" in result.stdout
    assert "not a concept document" in result.stdout


def test_index_listing_a_concept_twice_is_flagged(tmp_path: Path) -> None:
    """A concept listed by two bullets is flagged; last-wins collapsing can no
    longer be used to hide a wrong description behind a correct duplicate."""
    index = (
        "# standards/ — index\n\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
        "- [Dupe](/standards/README.md) — Standards desc\n"
        "- [Document Types](/standards/docs/document-types.md) — The document type registry\n"
    )
    repo = make_bundle(tmp_path, {"standards/index.md": index})

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert "standards/README.md" in result.stdout
    assert "more than once" in result.stdout


def test_bullet_inside_a_four_backtick_artifact_fence_is_not_read_as_an_entry(
    tmp_path: Path,
) -> None:
    """A four-backtick fence wrapping three-backtick content stays one block.

    An index illustrating the artifact form issue-authoring.md mandates quotes
    a bullet inside such a fence; the quoted bullet is shown, not listed, so it
    draws no index finding.
    """
    index = (
        "# standards/ — index\n\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
        "- [Document Types](/standards/docs/document-types.md) — The document type registry\n\n"
        "An index entry is written like this:\n\n"
        "````markdown\n"
        "```\n"
        "- [Rules](/standards/rules/naming.md) — not a concept doc\n"
        "```\n"
        "````\n"
    )
    repo = make_bundle(tmp_path, {"standards/index.md": index})

    result = run_okf_lint(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    # The clean marker, not just the exit code: a bundle that stopped being
    # scanned at all would pass on the return code alone while covering nothing.
    assert "clean" in result.stderr


def test_tests_tree_malformed_markdown_is_not_flagged(tmp_path: Path) -> None:
    """Malformed markdown under a top-level tests/ tree is parser fixture data,
    not a concept document — okf-lint emits no findings on it."""
    repo = make_bundle(
        tmp_path,
        {
            "tests/broken.md": '---\ntitle: "unterminated\n---\n\n# Broken\n',
            "tests/fixtures/specs/feat-01.md": "not even frontmatter\n",
            "tests/spec_files/index.md": "# not a real index\n",
        },
    )

    result = run_okf_lint(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "tests/" not in result.stdout


def test_repo_self_scan_is_clean() -> None:
    """The dev-playbook bundle itself passes okf-lint."""
    repo = Path(__file__).resolve().parents[1]
    result = run_okf_lint(repo)
    assert result.returncode == 0, result.stdout + result.stderr


# --- consumer mode: no standards/docs/document-types.md in the audited repo ---

# A minimal bundle with no registry doc at all (no standards/ directory), so
# okf-lint must resolve consumer mode and validate types against the upstream
# registry rather than raising because the audited tree carries none. The
# consumer-mode tests pin a synthetic upstream via make_upstream (which declares
# README among its types), so their assertions never depend on dev-playbook's
# live registry contents.
CONSUMER_BUNDLE: dict[str, str] = {
    "README.md": (
        "---\ntype: README\ntitle: Root\ndescription: Root readme desc\n---\n\n# Root\n"
    ),
    "index.md": (
        '---\nokf_version: "0.1"\n---\n\n# bundle index\n\n'
        "- [Root](/README.md) — Root readme desc\n"
    ),
}


def make_consumer_bundle(tmp_path: Path, overrides: dict[str, str | None]) -> Path:
    """Write CONSUMER_BUNDLE (no registry doc) into a fresh git repo."""
    return _write_bundle(tmp_path, CONSUMER_BUNDLE, overrides)


def test_consumer_mode_conformant_bundle_is_clean(tmp_path: Path) -> None:
    """A repo with no standards/docs/document-types.md is still linted — its
    types are validated against the upstream registry, never treated as
    'cannot run'."""
    repo = make_consumer_bundle(tmp_path, {})

    result = run_okf_lint(repo, upstream_root=make_upstream(tmp_path))

    assert result.returncode == 0, result.stdout + result.stderr
    assert "knowledge-organization.registry-row" not in result.stdout
    assert "knowledge-organization.index-ordering" not in result.stdout


def test_consumer_mode_bogus_type_is_flagged(tmp_path: Path) -> None:
    """A bogus type in a registry-less repo is checked against the upstream
    registry and flagged, and still emits no registry-shape finding — a
    consumer cannot fix the upstream registry from its own commit."""
    repo = make_consumer_bundle(
        tmp_path,
        {
            "README.md": "---\ntype: Bogus\ntitle: Root\ndescription: Root readme desc\n---\n\n# Root\n"
        },
    )

    result = run_okf_lint(repo, upstream_root=make_upstream(tmp_path))

    assert result.returncode == 1
    assert "not in the registry" in result.stdout
    assert "knowledge-organization.registry-row" not in result.stdout
    assert "knowledge-organization.index-ordering" not in result.stdout


def test_consumer_mode_resolves_upstream_from_pinned_root(tmp_path: Path) -> None:
    """Consumer mode reads the upstream registry from OKF_LINT_UPSTREAM_ROOT when
    it is set — a doc typed with a name only the pinned upstream declares
    (Landmark, absent from the live registry) resolves clean. This is the seam
    that lets the consumer-mode tests pin a synthetic registry instead of
    asserting against dev-playbook's live one."""
    upstream_doc = (
        "---\ntype: Standard\ntitle: Document Types\n"
        "description: The document type registry\n---\n\n"
        "# Document Types\n\n## Types\n\n"
        "| Type | What it is |\n|------|------------|\n"
        "| `Landmark` | a bespoke upstream-only type |\n| `README` | landing |\n"
    )
    upstream = tmp_path / "upstream"
    (upstream / "standards" / "docs").mkdir(parents=True)
    (upstream / "standards" / "docs" / "document-types.md").write_text(upstream_doc)
    landmark = (
        "---\ntype: Landmark\ntitle: A Landmark\n"
        "description: A landmark doc\n---\n\n# A Landmark\n"
    )
    index = (
        '---\nokf_version: "0.1"\n---\n\n# bundle index\n\n'
        "- [Root](/README.md) — Root readme desc\n"
        "- [A Landmark](/landmark.md) — A landmark doc\n"
    )
    repo = make_consumer_bundle(tmp_path, {"landmark.md": landmark, "index.md": index})

    result = run_okf_lint(repo, upstream_root=upstream)

    assert result.returncode == 0, result.stdout + result.stderr


# --- consumer mode: the local type extension (union, degradation, shadow) ---

# A conformant consumer bundle that carries its OWN standards/docs/document-types.md
# as a LOCAL EXTENSION. It ships no canonical consumer template, so okf-lint stays
# in consumer mode: it resolves the upstream registry (the pinned synthetic one)
# and unions the extension's valid types on top. The local names (Doohickey,
# Gizmo) are absent from that synthetic upstream, so they neither collide with an
# upstream name nor shadow one.
EXTENSION_DOC = (
    "---\ntype: Standard\ntitle: Local Types\n"
    "description: The local type extension\n---\n\n"
    "# Local Types\n\n## Types\n\n"
    "| Type | What it is |\n|------|------------|\n"
    "| `Doohickey` | a local doohickey |\n| `Gizmo` | a local gizmo |\n"
)
CONSUMER_EXT_BUNDLE: dict[str, str] = {
    "README.md": (
        "---\ntype: README\ntitle: Root\ndescription: Root readme desc\n---\n\n# Root\n"
    ),
    "index.md": (
        '---\nokf_version: "0.1"\n---\n\n# bundle index\n\n'
        "- [Root](/README.md) — Root readme desc\n\n"
        "## Directories\n\n"
        "- [standards/](/standards/index.md) — Local standards\n"
    ),
    "standards/README.md": (
        "---\ntype: README\ntitle: Standards\ndescription: Standards desc\n---\n\n"
        "# Standards\n"
    ),
    "standards/index.md": (
        "# standards/ — index\n\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
        "- [Local Types](/standards/docs/document-types.md) — The local type extension\n"
    ),
    "standards/docs/document-types.md": EXTENSION_DOC,
}


def make_consumer_ext_bundle(tmp_path: Path, overrides: dict[str, str | None]) -> Path:
    """Write CONSUMER_EXT_BUNDLE (a local type extension) into a fresh git repo."""
    return _write_bundle(tmp_path, CONSUMER_EXT_BUNDLE, overrides)


def test_consumer_extension_unions_and_does_not_replace_upstream(
    tmp_path: Path,
) -> None:
    """A consumer's own document-types.md is a local extension, not a replacement:
    upstream types the local table omits (README, Standard) still resolve, so a
    bundle whose only typed docs are upstream types is clean even though the
    extension lists neither."""
    repo = make_consumer_ext_bundle(tmp_path, {})

    result = run_okf_lint(repo, upstream_root=make_upstream(tmp_path))

    assert result.returncode == 0, result.stdout + result.stderr


def test_consumer_extension_local_type_doc_is_accepted(tmp_path: Path) -> None:
    """A doc typed with a name the local extension declares (Gizmo) is legal —
    the extension's valid types are unioned into the effective set."""
    gizmo = (
        "---\ntype: Gizmo\ntitle: A Gizmo\ndescription: A gizmo doc\n---\n\n# A Gizmo\n"
    )
    index = (
        "# standards/ — index\n\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
        "- [A Gizmo](/standards/gizmo.md) — A gizmo doc\n"
        "- [Local Types](/standards/docs/document-types.md) — The local type extension\n"
    )
    repo = make_consumer_ext_bundle(
        tmp_path, {"standards/gizmo.md": gizmo, "standards/index.md": index}
    )

    result = run_okf_lint(repo, upstream_root=make_upstream(tmp_path))

    assert result.returncode == 0, result.stdout + result.stderr


def test_consumer_extension_bogus_type_still_flagged(tmp_path: Path) -> None:
    """A type in neither the upstream registry nor the local extension is still
    flagged — the union widens the legal set, it does not disable the check."""
    bogus = (
        "---\ntype: Bogus\ntitle: A Bogus\ndescription: A bogus doc\n---\n\n# A Bogus\n"
    )
    index = (
        "# standards/ — index\n\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
        "- [A Bogus](/standards/bogus.md) — A bogus doc\n"
        "- [Local Types](/standards/docs/document-types.md) — The local type extension\n"
    )
    repo = make_consumer_ext_bundle(
        tmp_path, {"standards/bogus.md": bogus, "standards/index.md": index}
    )

    result = run_okf_lint(repo, upstream_root=make_upstream(tmp_path))

    assert result.returncode == 1
    assert "standards/bogus.md" in result.stdout
    assert "type 'Bogus' not in the registry" in result.stdout


def test_consumer_extension_malformed_row_is_flagged_and_walk_continues(
    tmp_path: Path,
) -> None:
    """A malformed extension row is a `registry-row` finding at its line, and the
    extension is scanned non-raising — the walk does not abort, so an unrelated
    bogus type elsewhere is still caught."""
    ext = (
        "---\ntype: Standard\ntitle: Local Types\n"
        "description: The local type extension\n---\n\n"
        "# Local Types\n\n## Types\n\n"
        "| Type | What it is |\n|------|------------|\n"
        "| `Gizmo` | a local gizmo |\n"
        "| Bogus row without ticks | nonsense |\n"
    )
    nope = "---\ntype: Nope\ntitle: A Nope\ndescription: A nope doc\n---\n\n# A Nope\n"
    index = (
        "# standards/ — index\n\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
        "- [A Nope](/standards/nope.md) — A nope doc\n"
        "- [Local Types](/standards/docs/document-types.md) — The local type extension\n"
    )
    repo = make_consumer_ext_bundle(
        tmp_path,
        {
            "standards/docs/document-types.md": ext,
            "standards/nope.md": nope,
            "standards/index.md": index,
        },
    )

    result = run_okf_lint(repo, upstream_root=make_upstream(tmp_path))

    assert result.returncode == 1
    assert re.search(
        r"standards/docs/document-types\.md:\d+: knowledge-organization\.registry-row",
        result.stdout,
    ), result.stdout
    # The malformed extension did not abort the scan (exit 2): the sibling bogus
    # type is still caught.
    assert "type 'Nope' not in the registry" in result.stdout


def test_consumer_extension_with_zero_valid_rows_degrades_to_a_finding(
    tmp_path: Path,
) -> None:
    """An extension whose `## Types` table has no valid rows yields a file-level
    `registry-row` finding — never exit 2 — so every other okf-lint check on the
    repo still runs. The raising parse_registry would instead abort the scan."""
    ext = (
        "---\ntype: Standard\ntitle: Local Types\n"
        "description: The local type extension\n---\n\n"
        "# Local Types\n\n## Types\n\n"
        "| Type | What it is |\n|------|------------|\n"
        "| no ticks here | nonsense |\n"
    )
    repo = make_consumer_ext_bundle(tmp_path, {"standards/docs/document-types.md": ext})

    result = run_okf_lint(repo, upstream_root=make_upstream(tmp_path))

    assert result.returncode == 1
    # The finding is file-level (no `:line` after the path) and the run is exit 1,
    # not the exit 2 of a scan abort.
    assert (
        "standards/docs/document-types.md: knowledge-organization.registry-row"
        in result.stdout
    )


def test_consumer_extension_table_out_of_alphabetical_order_is_flagged(
    tmp_path: Path,
) -> None:
    """The extension's `## Types` table is held to the same alphabetical order as
    the apex registry — an out-of-order table is an `index-ordering` finding."""
    ext = (
        "---\ntype: Standard\ntitle: Local Types\n"
        "description: The local type extension\n---\n\n"
        "# Local Types\n\n## Types\n\n"
        "| Type | What it is |\n|------|------------|\n"
        "| `Gizmo` | a local gizmo |\n| `Doohickey` | a local doohickey |\n"
    )
    repo = make_consumer_ext_bundle(tmp_path, {"standards/docs/document-types.md": ext})

    result = run_okf_lint(repo, upstream_root=make_upstream(tmp_path))

    assert result.returncode == 1
    assert (
        "standards/docs/document-types.md: knowledge-organization.index-ordering"
        in result.stdout
    )


def test_consumer_extension_shadowing_upstream_yields_one_shadow_finding(
    tmp_path: Path,
) -> None:
    """A local row whose name case-insensitively equals an upstream type (Readme
    vs upstream README) yields exactly one `type-shadows-upstream` finding — the
    rule that closes the case-alias hole left by exact-case membership."""
    ext = (
        "---\ntype: Standard\ntitle: Local Types\n"
        "description: The local type extension\n---\n\n"
        "# Local Types\n\n## Types\n\n"
        "| Type | What it is |\n|------|------------|\n"
        "| `Readme` | a case variant of upstream README |\n"
    )
    repo = make_consumer_ext_bundle(tmp_path, {"standards/docs/document-types.md": ext})

    result = run_okf_lint(repo, upstream_root=make_upstream(tmp_path))

    assert result.returncode == 1
    shadow_lines = [
        line
        for line in result.stdout.splitlines()
        if "knowledge-organization.type-shadows-upstream" in line
    ]
    assert len(shadow_lines) == 1, result.stdout
    assert "Readme" in shadow_lines[0]


def test_consumer_extension_intra_extension_case_alias_yields_one_shadow_finding(
    tmp_path: Path,
) -> None:
    """Two local rows that are case-aliases of each other (Api / API), neither in
    upstream, still yield exactly one `type-shadows-upstream` finding — on the
    second row. The shadow rule closes the aliasing hole within the extension,
    not only against upstream; otherwise both would union in as distinct legal
    types."""
    ext = (
        "---\ntype: Standard\ntitle: Local Types\n"
        "description: The local type extension\n---\n\n"
        "# Local Types\n\n## Types\n\n"
        "| Type | What it is |\n|------|------------|\n"
        "| `Api` | a local api |\n| `API` | a case variant of Api |\n"
    )
    repo = make_consumer_ext_bundle(tmp_path, {"standards/docs/document-types.md": ext})

    result = run_okf_lint(repo, upstream_root=make_upstream(tmp_path))

    assert result.returncode == 1
    shadow_lines = [
        line
        for line in result.stdout.splitlines()
        if "knowledge-organization.type-shadows-upstream" in line
    ]
    assert len(shadow_lines) == 1, result.stdout
    assert "API" in shadow_lines[0]


def test_consumer_extension_file_unlisted_in_index_is_flagged_by_index_rule(
    tmp_path: Path,
) -> None:
    """The extension file is an ordinary concept doc: leaving it out of its owning
    index is caught by the existing index rule, no extension-specific code."""
    index = (
        "# standards/ — index\n\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
    )  # drops the document-types.md line
    repo = make_consumer_ext_bundle(tmp_path, {"standards/index.md": index})

    result = run_okf_lint(repo, upstream_root=make_upstream(tmp_path))

    assert result.returncode == 1
    assert "omits concept doc standards/docs/document-types.md" in result.stdout


def test_list_rules_includes_type_shadows_upstream(tmp_path: Path) -> None:
    """--list-rules registers the new shadow rule under the knowledge-organization
    namespace."""
    result = subprocess.run(
        ["uv", "run", "--script", str(OKF_LINT), "--list-rules"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "knowledge-organization.type-shadows-upstream" in result.stdout.split()


# --- instrument.employed-by ---

# The overlay a bundle needs to carry a typed Instrument Spec: the registry row
# that admits the type, the standards index that owns the spec doc, and the spec
# itself (its `{body}` slot filled per test).
INSTRUMENT_REGISTRY = (
    "---\ntype: Standard\ntitle: Document Types\n"
    "description: The document type registry\n---\n\n"
    "# Document Types\n\n## Types\n\n"
    "| Type | What it is |\n|------|------------|\n"
    "| `Guide` | teaching |\n| `Instrument-Spec` | a device contract |\n"
    "| `README` | landing |\n| `Recipe-Description` | describes code |\n"
    "| `Standard` | rules |\n"
)
INSTRUMENT_INDEX = (
    "# standards/ — index\n\n"
    "- [Standards](/standards/README.md) — Standards desc\n"
    "- [Document Types](/standards/docs/document-types.md) — The document type registry\n"
    "- [Widget](/standards/widget.md) — The widget instrument\n"
)
WIDGET_SPEC = (
    "---\ntype: Instrument-Spec\ntitle: Widget\n"
    "description: The widget instrument\n---\n\n# Widget\n\n{body}"
)


def make_instrument_bundle(tmp_path: Path, spec_body: str) -> Path:
    """A valid bundle carrying one Instrument Spec whose body is `spec_body`."""
    return make_bundle(
        tmp_path,
        {
            "standards/docs/document-types.md": INSTRUMENT_REGISTRY,
            "standards/index.md": INSTRUMENT_INDEX,
            "standards/widget.md": WIDGET_SPEC.format(body=spec_body),
        },
    )


def test_instrument_spec_without_employed_by_is_flagged(tmp_path: Path) -> None:
    """An Instrument Spec with no `## Employed by` section is flagged."""
    repo = make_instrument_bundle(tmp_path, "A spec with no employed-by heading.\n")

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert "standards/widget.md: instrument.employed-by" in result.stdout


def test_instrument_spec_with_employed_by_is_clean(tmp_path: Path) -> None:
    """An Instrument Spec carrying an `## Employed by` section is not flagged."""
    repo = make_instrument_bundle(
        tmp_path,
        "## Employed by\n\n[System Legibility](/standards/legibility.md).\n",
    )

    result = run_okf_lint(repo)

    assert result.returncode == 0, result.stdout + result.stderr


# --- rule ids and finding format ---


def test_list_rules_prints_card_namespaced_ids_from_any_cwd(tmp_path: Path) -> None:
    result = subprocess.run(
        ["uv", "run", "--script", str(OKF_LINT), "--list-rules"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    ids = result.stdout.split()
    assert "knowledge-organization.type" in ids
    assert "knowledge-organization.registry-row" in ids
    assert "knowledge-organization.description-shape" in ids
    assert "knowledge-organization.index-ordering" in ids
    assert "instrument.employed-by" in ids
    assert all(
        rule.startswith(("knowledge-organization.", "instrument.")) for rule in ids
    ), ids


def test_malformed_registry_row_is_flagged_not_silently_skipped(
    tmp_path: Path,
) -> None:
    """A `## Types` row without a backticked name in its first cell used to drop
    out of the registry silently; now it is a `knowledge-organization.registry-row` finding at the
    row's line."""
    doc = (
        "---\ntype: Standard\ntitle: Document Types\n"
        "description: The document type registry\n---\n\n"
        "# Document Types\n\n## Types\n\n"
        "| Type | What it is |\n|------|------------|\n"
        "| `Standard` | rules |\n| `README` | landing |\n"
        "| `Guide` | teaching |\n| `Recipe-Description` | describes code |\n"
        "| Bogus row without ticks | nonsense |\n"
    )
    repo = make_bundle(tmp_path, {"standards/docs/document-types.md": doc})

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert re.search(
        r"standards/docs/document-types\.md:\d+: knowledge-organization\.registry-row",
        result.stdout,
    ), result.stdout


def test_registry_row_with_non_title_case_name_is_flagged(tmp_path: Path) -> None:
    """A backticked first cell whose name is not Title Case (each whitespace-
    separated word capitalized) is a malformed registry row, not a silently
    accepted type."""
    doc = (
        "---\ntype: Standard\ntitle: Document Types\n"
        "description: The document type registry\n---\n\n"
        "# Document Types\n\n## Types\n\n"
        "| Type | What it is |\n|------|------------|\n"
        "| `Guide` | teaching |\n| `README` | landing |\n"
        "| `Recipe-Description` | describes code |\n| `Standard` | rules |\n"
        "| `bogus name` | nonsense |\n"
    )
    repo = make_bundle(tmp_path, {"standards/docs/document-types.md": doc})

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert re.search(
        r"standards/docs/document-types\.md:\d+: knowledge-organization\.registry-row",
        result.stdout,
    ), result.stdout


def test_ordering_marker_below_the_listing_does_not_exempt(tmp_path: Path) -> None:
    """The `Ordering:` marker exempts only as an intro line; one appearing after
    the first entry is not an exemption, so the out-of-alphabetical concept order
    (README.md still leads) is still flagged."""
    guide = "---\ntype: Guide\ntitle: {t}\ndescription: {d}\n---\n\n# {t}\n"
    index = (
        "# standards/ — index\n\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
        "- [Zebra](/standards/zebra.md) — zebra guide\n"
        "- [Apple](/standards/apple.md) — apple guide\n"
        "- [Document Types](/standards/docs/document-types.md) —"
        " The document type registry\n\n"
        "Ordering: by significance, not alphabetical.\n"
    )
    repo = make_bundle(
        tmp_path,
        {
            "standards/zebra.md": guide.format(t="Zebra", d="zebra guide"),
            "standards/apple.md": guide.format(t="Apple", d="apple guide"),
            "standards/index.md": index,
        },
    )

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert "standards/index.md: knowledge-organization.index-ordering" in result.stdout


def test_description_with_trailing_period_is_flagged(tmp_path: Path) -> None:
    """A concept doc's frontmatter `description` must carry no trailing period."""
    repo = make_bundle(
        tmp_path,
        {
            "standards/README.md": (
                "---\ntype: README\ntitle: Standards\n"
                "description: Standards desc.\n---\n\n# Standards\n"
            ),
            "standards/index.md": (
                "# standards/ — index\n\n"
                "- [Standards](/standards/README.md) — Standards desc.\n"
                "- [Document Types](/standards/docs/document-types.md) —"
                " The document type registry\n"
            ),
        },
    )

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert (
        "standards/README.md: knowledge-organization.description-shape" in result.stdout
    )


def test_index_with_readme_not_first_is_flagged(tmp_path: Path) -> None:
    """The README.md entry must head an index; here it trails a concept doc."""
    index = (
        "# standards/ — index\n\n"
        "- [Document Types](/standards/docs/document-types.md) —"
        " The document type registry\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
    )
    repo = make_bundle(tmp_path, {"standards/index.md": index})

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert "standards/index.md: knowledge-organization.index-ordering" in result.stdout


def test_ordering_marker_exempts_a_deviating_index(tmp_path: Path) -> None:
    """An intro line beginning `Ordering:` declares a meaningful order and
    exempts the index from the alphabetical checks. README.md still leads, so the
    marker excuses only the out-of-alphabetical concept order below."""
    guide = "---\ntype: Guide\ntitle: {t}\ndescription: {d}\n---\n\n# {t}\n"
    index = (
        "# standards/ — index\n\n"
        "Ordering: by significance, not alphabetical.\n\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
        "- [Zebra](/standards/zebra.md) — zebra guide\n"
        "- [Apple](/standards/apple.md) — apple guide\n"
        "- [Document Types](/standards/docs/document-types.md) —"
        " The document type registry\n"
    )
    repo = make_bundle(
        tmp_path,
        {
            "standards/zebra.md": guide.format(t="Zebra", d="zebra guide"),
            "standards/apple.md": guide.format(t="Apple", d="apple guide"),
            "standards/index.md": index,
        },
    )

    result = run_okf_lint(repo)

    assert result.returncode == 0, result.stdout + result.stderr


def test_ordering_marker_does_not_exempt_readme_first(tmp_path: Path) -> None:
    """The `Ordering:` marker exempts only the alphabetical checks; the README.md
    entry must lead even under the marker, so a marked index that lists it
    non-first is still flagged."""
    index = (
        "# standards/ — index\n\n"
        "Ordering: by significance, not alphabetical.\n\n"
        "- [Document Types](/standards/docs/document-types.md) —"
        " The document type registry\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
    )
    repo = make_bundle(tmp_path, {"standards/index.md": index})

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert "standards/index.md: knowledge-organization.index-ordering" in result.stdout
    assert "the README.md entry must be listed first" in result.stdout


def test_concept_entries_out_of_alphabetical_order_are_flagged(
    tmp_path: Path,
) -> None:
    guide = "---\ntype: Guide\ntitle: {t}\ndescription: {d}\n---\n\n# {t}\n"
    index = (
        "# standards/ — index\n\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
        "- [Document Types](/standards/docs/document-types.md) —"
        " The document type registry\n"
        "- [Zebra](/standards/zebra.md) — zebra guide\n"
        "- [Apple](/standards/apple.md) — apple guide\n"
    )
    repo = make_bundle(
        tmp_path,
        {
            "standards/zebra.md": guide.format(t="Zebra", d="zebra guide"),
            "standards/apple.md": guide.format(t="Apple", d="apple guide"),
            "standards/index.md": index,
        },
    )

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert "standards/index.md: knowledge-organization.index-ordering" in result.stdout


def test_types_table_out_of_alphabetical_order_is_flagged(tmp_path: Path) -> None:
    """document-types.md declares its `## Types` table alphabetical; a table
    whose rows are not is a `knowledge-organization.index-ordering` finding."""
    doc = (
        "---\ntype: Standard\ntitle: Document Types\n"
        "description: The document type registry\n---\n\n"
        "# Document Types\n\n## Types\n\n"
        "| Type | What it is |\n|------|------------|\n"
        "| `README` | landing |\n| `Standard` | rules |\n"
        "| `Guide` | teaching |\n| `Recipe-Description` | describes code |\n"
    )
    repo = make_bundle(tmp_path, {"standards/docs/document-types.md": doc})

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert (
        "standards/docs/document-types.md: knowledge-organization.index-ordering"
        in result.stdout
    )


def test_finding_line_is_gnu_format(tmp_path: Path) -> None:
    repo = make_bundle(
        tmp_path,
        {
            "standards/README.md": "---\ntitle: Standards\ndescription: Standards desc\n---\n\n# S\n"
        },
    )

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert (
        "standards/README.md: knowledge-organization.type missing 'type'"
        in result.stdout
    )
