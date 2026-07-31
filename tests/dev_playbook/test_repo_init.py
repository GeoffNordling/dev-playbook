import re
import subprocess
from pathlib import Path

import pytest

from dev_playbook.repo_init import (
    PLAYBOOK_ROOT,
    RepoInitError,
    RepoSpec,
    init_repo,
    render_tree,
)

REV = "0" * 40
BASE_SPEC = RepoSpec(name="sample-tool", description="A demo repo", python=False)
PY_SPEC = RepoSpec(name="sample-lib", description="A demo repo", python=True)

# Any `<token>` the canonical artifacts use as a substitution point. The
# rendered tree must carry none of them.
PLACEHOLDER = re.compile(r"<[a-zA-Z][a-zA-Z0-9_-]*>")


def run_repo_lint(target: Path) -> subprocess.CompletedProcess[str]:
    """Audit a scaffolded repo with the same detector the standard enforces."""
    return subprocess.run(
        [str(PLAYBOOK_ROOT / "scripts" / "repo-lint"), str(target)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_scaffolded_base_repo_passes_repo_lint(tmp_path: Path) -> None:
    target = init_repo(BASE_SPEC, tmp_path)

    lint = run_repo_lint(target)

    assert lint.returncode == 0, lint.stdout


def test_scaffolded_python_repo_passes_repo_lint(tmp_path: Path) -> None:
    target = init_repo(PY_SPEC, tmp_path)

    lint = run_repo_lint(target)

    assert lint.returncode == 0, lint.stdout


def test_no_placeholder_survives_in_the_rendered_tree() -> None:
    tree = render_tree(PY_SPEC, REV)

    leftovers = {
        rel: PLACEHOLDER.findall(text)
        for rel, text in tree.items()
        if PLACEHOLDER.search(text)
    }

    assert leftovers == {}


def test_hook_config_pins_the_supplied_rev() -> None:
    tree = render_tree(BASE_SPEC, REV)

    config = tree[".pre-commit-config.yaml"]

    assert f"rev: {REV}" in config


def test_repo_name_maps_to_project_and_package() -> None:
    spec = RepoSpec(name="Sample-Tool", description="A demo repo", python=True)

    assert spec.project == "sample-tool"
    assert spec.package == "sample_tool"


def test_python_layer_adds_the_project_and_package_files() -> None:
    tree = render_tree(PY_SPEC, REV)

    assert 'name = "sample-lib"' in tree["pyproject.toml"]
    assert "src/sample_lib/__init__.py" in tree
    assert "tests/conftest.py" in tree
    assert ".python-version" in tree


def test_base_layer_omits_the_python_project() -> None:
    tree = render_tree(BASE_SPEC, REV)

    assert "pyproject.toml" not in tree
    assert ".python-version" not in tree
    assert [rel for rel in tree if rel.startswith("src/")] == []


@pytest.mark.parametrize(
    ("name", "word"),
    [
        ("the-human", "human"),
        ("I-tool", "I"),
        ("notify-me", "me"),
        ("my-tool", "my"),
    ],
)
def test_name_carrying_an_agent_facing_voice_word_is_refused(
    name: str, word: str
) -> None:
    spec = RepoSpec(name=name, description="A demo repo", python=False)

    with pytest.raises(RepoInitError, match=re.escape(f"'{word}'")):
        render_tree(spec, REV)


@pytest.mark.parametrize("name", ["metrics", "mystery", "human-readable"])
def test_name_merely_embedding_a_voice_word_is_allowed(name: str) -> None:
    spec = RepoSpec(name=name, description="A demo repo", python=False)

    tree = render_tree(spec, REV)

    assert tree["CLAUDE.md"] == f"# {name}\n"


def test_name_that_is_not_a_valid_package_is_refused() -> None:
    spec = RepoSpec(name="1bad", description="A demo repo", python=True)

    with pytest.raises(RepoInitError, match="not a valid import package"):
        render_tree(spec, REV)


def test_scaffold_refuses_a_target_that_already_exists(tmp_path: Path) -> None:
    (tmp_path / BASE_SPEC.name).mkdir()

    with pytest.raises(RepoInitError, match="already exists"):
        init_repo(BASE_SPEC, tmp_path)
