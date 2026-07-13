"""Behavioral tests for scripts/okf-audit.

okf-audit declares pyyaml via PEP 723 and imports the local dev_playbook package, so it
is invoked exactly the way pre-commit runs it: `uv run --script`.
"""

import re
import subprocess
from pathlib import Path

OKF_AUDIT = Path(__file__).resolve().parents[1] / "scripts" / "okf-audit"

# A minimal but valid OKF bundle: a registry doc, two concept docs, a root
# index (with okf_version) and a standards index, all internally consistent.
BASE_BUNDLE: dict[str, str] = {
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
        "| `Recipe Description` | describes code |\n| `Standard` | rules |\n"
    ),
    "standards/index.md": (
        "# standards/ — index\n\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
        "- [Document Types](/standards/docs/document-types.md) — The document type registry\n"
    ),
}


def run_okf_audit(repo_root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", "--script", str(OKF_AUDIT), str(repo_root)],
        capture_output=True,
        text=True,
    )


def make_bundle(tmp_path: Path, overrides: dict[str, str | None]) -> Path:
    """Write BASE_BUNDLE into a fresh git repo, applying overrides.

    An override value of None deletes that file; any other value replaces it.
    """
    repo = tmp_path / "repo"
    files = dict(BASE_BUNDLE)
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


def test_valid_bundle_is_clean(tmp_path: Path) -> None:
    repo = make_bundle(tmp_path, {})

    result = run_okf_audit(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "clean" in result.stderr


def test_missing_type_is_flagged(tmp_path: Path) -> None:
    repo = make_bundle(
        tmp_path,
        {
            "standards/README.md": "---\ntitle: Standards\ndescription: Standards desc\n---\n\n# S\n"
        },
    )

    result = run_okf_audit(repo)

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

    result = run_okf_audit(repo)

    assert result.returncode == 1
    assert "not in the registry" in result.stdout


def test_missing_description_is_flagged(tmp_path: Path) -> None:
    repo = make_bundle(
        tmp_path,
        {"standards/README.md": "---\ntype: README\ntitle: Standards\n---\n\n# S\n"},
    )

    result = run_okf_audit(repo)

    assert result.returncode == 1
    assert "missing 'description'" in result.stdout


def test_recipe_description_requires_resource(tmp_path: Path) -> None:
    recipe = "---\ntype: Recipe Description\ntitle: Ralph\ndescription: A loop\n---\n\n# Ralph\n"
    index = (
        "# standards/ — index\n\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
        "- [Document Types](/standards/docs/document-types.md) — The document type registry\n"
        "- [Ralph](/standards/ralph.md) — A loop\n"
    )
    repo = make_bundle(
        tmp_path, {"standards/ralph.md": recipe, "standards/index.md": index}
    )

    result = run_okf_audit(repo)

    assert result.returncode == 1
    assert "requires a 'resource'" in result.stdout


def test_index_omitting_a_concept_is_flagged(tmp_path: Path) -> None:
    index = (
        "# standards/ — index\n\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
    )  # drops the document-types.md line
    repo = make_bundle(tmp_path, {"standards/index.md": index})

    result = run_okf_audit(repo)

    assert result.returncode == 1
    assert "omits concept doc standards/docs/document-types.md" in result.stdout


def test_index_listing_missing_file_is_flagged(tmp_path: Path) -> None:
    index = BASE_BUNDLE["standards/index.md"] + "- [Gone](/standards/gone.md) — nope\n"
    repo = make_bundle(tmp_path, {"standards/index.md": index})

    result = run_okf_audit(repo)

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

    result = run_okf_audit(repo)

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

    result = run_okf_audit(repo)

    assert result.returncode == 1
    assert "okf_version" in result.stdout


def test_root_index_omitting_child_index_is_flagged(tmp_path: Path) -> None:
    index = (
        '---\nokf_version: "0.1"\n---\n\n# bundle index\n\n'
        "- [Root](/README.md) — Root readme desc\n"
    )  # drops the standards/ child-index link
    repo = make_bundle(tmp_path, {"index.md": index})

    result = run_okf_audit(repo)

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

    result = run_okf_audit(repo)

    assert result.returncode == 1
    assert "standards/README.md" in result.stdout
    assert "docs.frontmatter" in result.stdout
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

    result = run_okf_audit(repo)

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

    result = run_okf_audit(repo)

    assert result.returncode == 1
    assert "standards/README.md" in result.stdout
    assert "more than once" in result.stdout


def test_repo_self_scan_is_clean() -> None:
    """The dev-playbook bundle itself passes okf-audit."""
    repo = Path(__file__).resolve().parents[1]
    result = run_okf_audit(repo)
    assert result.returncode == 0, result.stdout + result.stderr


# --- consumer mode: no standards/docs/document-types.md in the audited repo ---

# A minimal bundle with no registry doc at all (no standards/ directory), so
# okf-audit must resolve consumer mode and validate types against its own
# clone's registry instead of raising "registry doc not found". Types used
# here (README) exist in dev-playbook's live registry, since the subprocess
# resolves its clone root to the real checkout via __file__.
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
    """Write CONSUMER_BUNDLE into a fresh git repo, applying overrides.

    An override value of None deletes that file; any other value replaces it.
    """
    repo = tmp_path / "repo"
    files = dict(CONSUMER_BUNDLE)
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


def test_consumer_mode_conformant_bundle_is_clean(tmp_path: Path) -> None:
    """A repo with no standards/docs/document-types.md is still linted — its
    types are validated against the hook's own clone registry, never treated
    as 'cannot run'."""
    repo = make_consumer_bundle(tmp_path, {})

    result = run_okf_audit(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "docs.registry-row" not in result.stdout
    assert "docs.index-ordering" not in result.stdout


def test_consumer_mode_bogus_type_is_flagged(tmp_path: Path) -> None:
    """A bogus type in a registry-less repo is checked against the clone's
    registry and flagged, and still emits no registry-shape finding — a
    consumer cannot fix dev-playbook's registry from its own commit."""
    repo = make_consumer_bundle(
        tmp_path,
        {
            "README.md": "---\ntype: Bogus\ntitle: Root\ndescription: Root readme desc\n---\n\n# Root\n"
        },
    )

    result = run_okf_audit(repo)

    assert result.returncode == 1
    assert "not in the registry" in result.stdout
    assert "docs.registry-row" not in result.stdout
    assert "docs.index-ordering" not in result.stdout


# --- instrument.employed-by ---

# The overlay a bundle needs to carry a typed Instrument Spec: the registry row
# that admits the type, the standards index that owns the spec doc, and the spec
# itself (its `{body}` slot filled per test).
INSTRUMENT_REGISTRY = (
    "---\ntype: Standard\ntitle: Document Types\n"
    "description: The document type registry\n---\n\n"
    "# Document Types\n\n## Types\n\n"
    "| Type | What it is |\n|------|------------|\n"
    "| `Guide` | teaching |\n| `Instrument Spec` | a device contract |\n"
    "| `README` | landing |\n| `Recipe Description` | describes code |\n"
    "| `Standard` | rules |\n"
)
INSTRUMENT_INDEX = (
    "# standards/ — index\n\n"
    "- [Standards](/standards/README.md) — Standards desc\n"
    "- [Document Types](/standards/docs/document-types.md) — The document type registry\n"
    "- [Widget](/standards/widget.md) — The widget instrument\n"
)
WIDGET_SPEC = (
    "---\ntype: Instrument Spec\ntitle: Widget\n"
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

    result = run_okf_audit(repo)

    assert result.returncode == 1
    assert "standards/widget.md: instrument.employed-by" in result.stdout


def test_instrument_spec_with_employed_by_is_clean(tmp_path: Path) -> None:
    """An Instrument Spec carrying an `## Employed by` section is not flagged."""
    repo = make_instrument_bundle(
        tmp_path,
        "## Employed by\n\n[System Legibility](/standards/legibility.md).\n",
    )

    result = run_okf_audit(repo)

    assert result.returncode == 0, result.stdout + result.stderr


# --- rule ids and finding format ---


def test_list_rules_prints_card_namespaced_ids_from_any_cwd(tmp_path: Path) -> None:
    result = subprocess.run(
        ["uv", "run", "--script", str(OKF_AUDIT), "--list-rules"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    ids = result.stdout.split()
    assert "docs.type" in ids
    assert "docs.registry-row" in ids
    assert "docs.description-shape" in ids
    assert "docs.index-ordering" in ids
    assert "instrument.employed-by" in ids
    assert all(rule.startswith(("docs.", "instrument.")) for rule in ids), ids


def test_malformed_registry_row_is_flagged_not_silently_skipped(
    tmp_path: Path,
) -> None:
    """A `## Types` row without a backticked name in its first cell used to drop
    out of the registry silently; now it is a `docs.registry-row` finding at the
    row's line."""
    doc = (
        "---\ntype: Standard\ntitle: Document Types\n"
        "description: The document type registry\n---\n\n"
        "# Document Types\n\n## Types\n\n"
        "| Type | What it is |\n|------|------------|\n"
        "| `Standard` | rules |\n| `README` | landing |\n"
        "| `Guide` | teaching |\n| `Recipe Description` | describes code |\n"
        "| Bogus row without ticks | nonsense |\n"
    )
    repo = make_bundle(tmp_path, {"standards/docs/document-types.md": doc})

    result = run_okf_audit(repo)

    assert result.returncode == 1
    assert re.search(
        r"standards/docs/document-types\.md:\d+: docs\.registry-row",
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
        "| `Recipe Description` | describes code |\n| `Standard` | rules |\n"
        "| `bogus name` | nonsense |\n"
    )
    repo = make_bundle(tmp_path, {"standards/docs/document-types.md": doc})

    result = run_okf_audit(repo)

    assert result.returncode == 1
    assert re.search(
        r"standards/docs/document-types\.md:\d+: docs\.registry-row",
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

    result = run_okf_audit(repo)

    assert result.returncode == 1
    assert "standards/index.md: docs.index-ordering" in result.stdout


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

    result = run_okf_audit(repo)

    assert result.returncode == 1
    assert "standards/README.md: docs.description-shape" in result.stdout


def test_index_with_readme_not_first_is_flagged(tmp_path: Path) -> None:
    """The README.md entry must head an index; here it trails a concept doc."""
    index = (
        "# standards/ — index\n\n"
        "- [Document Types](/standards/docs/document-types.md) —"
        " The document type registry\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
    )
    repo = make_bundle(tmp_path, {"standards/index.md": index})

    result = run_okf_audit(repo)

    assert result.returncode == 1
    assert "standards/index.md: docs.index-ordering" in result.stdout


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

    result = run_okf_audit(repo)

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

    result = run_okf_audit(repo)

    assert result.returncode == 1
    assert "standards/index.md: docs.index-ordering" in result.stdout
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

    result = run_okf_audit(repo)

    assert result.returncode == 1
    assert "standards/index.md: docs.index-ordering" in result.stdout


def test_types_table_out_of_alphabetical_order_is_flagged(tmp_path: Path) -> None:
    """document-types.md declares its `## Types` table alphabetical; a table
    whose rows are not is a `docs.index-ordering` finding."""
    doc = (
        "---\ntype: Standard\ntitle: Document Types\n"
        "description: The document type registry\n---\n\n"
        "# Document Types\n\n## Types\n\n"
        "| Type | What it is |\n|------|------------|\n"
        "| `README` | landing |\n| `Standard` | rules |\n"
        "| `Guide` | teaching |\n| `Recipe Description` | describes code |\n"
    )
    repo = make_bundle(tmp_path, {"standards/docs/document-types.md": doc})

    result = run_okf_audit(repo)

    assert result.returncode == 1
    assert "standards/docs/document-types.md: docs.index-ordering" in result.stdout


def test_finding_line_is_gnu_format(tmp_path: Path) -> None:
    repo = make_bundle(
        tmp_path,
        {
            "standards/README.md": "---\ntitle: Standards\ndescription: Standards desc\n---\n\n# S\n"
        },
    )

    result = run_okf_audit(repo)

    assert result.returncode == 1
    assert "standards/README.md: docs.type missing 'type'" in result.stdout
