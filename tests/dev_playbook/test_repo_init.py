import re
import subprocess
from pathlib import Path

import pytest

from dev_playbook.checks.prose import WORKSPACE_WORD
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


def run_playbook_lint(target: Path) -> subprocess.CompletedProcess[str]:
    """Audit a scaffolded repo with the very hook the scaffold installs."""
    return subprocess.run(
        [str(PLAYBOOK_ROOT / "scripts" / "playbook-lint"), str(target)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_scaffolded_base_repo_passes_playbook_lint(tmp_path: Path) -> None:
    target = init_repo(BASE_SPEC, tmp_path)

    lint = run_playbook_lint(target)

    assert lint.returncode == 0, lint.stdout


def test_scaffolded_python_repo_passes_playbook_lint(tmp_path: Path) -> None:
    target = init_repo(PY_SPEC, tmp_path)

    lint = run_playbook_lint(target)

    assert lint.returncode == 0, lint.stdout


def test_root_index_carries_an_introduction() -> None:
    # The knowledge-organization.introduction-between-h1-and-listing rule: prose stands between
    # the H1 and the first entry.
    tree = render_tree(BASE_SPEC, REV)

    lines = tree["index.md"].splitlines()
    heading = lines.index(f"# {BASE_SPEC.name} — bundle index")
    first_entry = next(i for i, line in enumerate(lines) if line.startswith("- ["))

    assert [line for line in lines[heading + 1 : first_entry] if line.strip()]


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
    assert ".python-version" in tree


def test_python_layer_ships_a_test_that_imports_the_package() -> None:
    # `make check` runs pytest, which exits 5 when no test is collected, so a
    # suite with no tests cannot pass the gate the scaffold installs.
    tree = render_tree(PY_SPEC, REV)

    assert tree["tests/test_package.py"] == (
        "import sample_lib\n"
        "\n"
        "\n"
        "def test_package_imports() -> None:\n"
        '    assert sample_lib.__name__ == "sample_lib"\n'
    )


def test_base_layer_omits_the_python_project() -> None:
    tree = render_tree(BASE_SPEC, REV)

    assert "pyproject.toml" not in tree
    assert ".python-version" not in tree
    assert [rel for rel in tree if rel.startswith("src/")] == []


@pytest.mark.parametrize(
    ("name", "word"),
    [
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


@pytest.mark.parametrize(
    "name", [f"the-{WORKSPACE_WORD}", f"{WORKSPACE_WORD}-readable"]
)
def test_name_carrying_the_banned_word_is_refused(name: str) -> None:
    spec = RepoSpec(name=name, description="A demo repo", python=False)

    with pytest.raises(RepoInitError, match="the prose checks reject"):
        render_tree(spec, REV)


@pytest.mark.parametrize("name", ["metrics", "mystery"])
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
