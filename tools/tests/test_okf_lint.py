"""Behavioral tests for tools/bin/okf-lint.

okf-lint declares pyyaml via PEP 723 and imports the local lib package, so it
is invoked exactly the way pre-commit runs it: `uv run --script`.
"""

import subprocess
from pathlib import Path

OKF_LINT = Path(__file__).resolve().parents[1] / "bin" / "okf-lint"

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
    "standards/document-types.md": (
        "---\ntype: Standard\ntitle: Document Types\n"
        "description: The document type registry\n---\n\n"
        "# Document Types\n\n## Types\n\n"
        "| Type | What it is |\n|------|------------|\n"
        "| `Standard` | rules |\n| `README` | landing |\n"
        "| `Guide` | teaching |\n| `Recipe Description` | describes code |\n"
    ),
    "standards/index.md": (
        "# standards/ — index\n\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
        "- [Document Types](/standards/document-types.md) — The document type registry\n"
    ),
}


def run_okf_lint(repo_root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", "--script", str(OKF_LINT), str(repo_root)],
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
    recipe = "---\ntype: Recipe Description\ntitle: Ralph\ndescription: A loop\n---\n\n# Ralph\n"
    index = (
        "# standards/ — index\n\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
        "- [Document Types](/standards/document-types.md) — The document type registry\n"
        "- [Ralph](/standards/ralph.md) — A loop\n"
    )
    repo = make_bundle(
        tmp_path, {"standards/ralph.md": recipe, "standards/index.md": index}
    )

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert "requires a 'resource'" in result.stdout


def test_index_omitting_a_concept_is_flagged(tmp_path: Path) -> None:
    index = (
        "# standards/ — index\n\n"
        "- [Standards](/standards/README.md) — Standards desc\n"
    )  # drops the document-types.md line
    repo = make_bundle(tmp_path, {"standards/index.md": index})

    result = run_okf_lint(repo)

    assert result.returncode == 1
    assert "omits concept doc standards/document-types.md" in result.stdout


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
        "- [Document Types](/standards/document-types.md) — The document type registry\n"
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


def test_repo_self_scan_is_clean() -> None:
    """The dev-playbook bundle itself passes okf-lint."""
    repo = Path(__file__).resolve().parents[2]
    result = run_okf_lint(repo)
    assert result.returncode == 0, result.stdout + result.stderr
