from pathlib import Path

import pytest

from dev_playbook.repo_init import RepoInitError, RepoSpec, render_tree, write_tree

BASE_SPEC = RepoSpec(name="My-Repo", description="A demo repo", python=False)
PY_SPEC = RepoSpec(name="My-Repo", description="A demo repo", python=True)
REV = "0" * 40

BASE_REQUIRED = {
    "README.md",
    "CLAUDE.md",
    "index.md",
    ".gitignore",
    ".pre-commit-config.yaml",
    "Makefile",
    ".github/workflows/ci.yml",
}


def test_name_mapping() -> None:
    assert PY_SPEC.project == "my-repo"
    assert PY_SPEC.package == "my_repo"


def test_base_tree_holds_every_base_required_file() -> None:
    tree = render_tree(BASE_SPEC, REV)
    assert set(tree) >= BASE_REQUIRED
    assert "pyproject.toml" not in tree


def test_pin_replaces_placeholder() -> None:
    config = render_tree(BASE_SPEC, REV)[".pre-commit-config.yaml"]
    assert REV in config
    assert "<pinned-sha>" not in config


def test_python_tree_fills_placeholders() -> None:
    tree = render_tree(PY_SPEC, REV)
    assert 'name = "my-repo"' in tree["pyproject.toml"]
    assert '"my_repo"' in tree["pyproject.toml"]
    assert "<package>" not in tree["pyproject.toml"]
    assert "<code-roots>" not in tree["Makefile"]
    assert tree["src/my_repo/__init__.py"] == ""
    assert "tests/conftest.py" in tree


def test_readme_carries_okf_frontmatter() -> None:
    readme = render_tree(BASE_SPEC, REV)["README.md"]
    assert readme.startswith("---\ntype: README\n")
    assert "# My-Repo" in readme


def test_invalid_package_name_fails_loud() -> None:
    spec = RepoSpec(name="1bad", description="x", python=True)
    with pytest.raises(RepoInitError):
        render_tree(spec, REV)


def test_write_tree_creates_nested_paths(tmp_path: Path) -> None:
    write_tree(tmp_path, {"a/b/c.txt": "x\n"})
    assert (tmp_path / "a" / "b" / "c.txt").read_text() == "x\n"
