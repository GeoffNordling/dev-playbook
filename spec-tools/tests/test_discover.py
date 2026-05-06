"""Tests for spec_tools.discover."""

import pathlib

import pytest

from spec_tools.discover import find


@pytest.mark.covers("dsn~discover.find~0")
def test_find_returns_single_file_layout_specs(tmp_path: pathlib.Path):
    specs_dir = tmp_path / "specs"
    specs_dir.mkdir()
    design_path = specs_dir / "design.md"
    design_path.write_text("# design\n")
    fr_path = specs_dir / "functional_requirements.md"
    fr_path.write_text("# fr\n")

    result = find(tmp_path)

    assert result == [design_path, fr_path]


@pytest.mark.covers("dsn~discover.find~0")
def test_find_returns_folder_form_specs_recursively(tmp_path: pathlib.Path):
    specs_dir = tmp_path / "specs"
    (specs_dir / "design").mkdir(parents=True)
    (specs_dir / "functional_requirements" / "nested").mkdir(parents=True)
    (specs_dir / "design" / "index.md").write_text("# index\n")
    (specs_dir / "functional_requirements" / "index.md").write_text("# index\n")
    design_alpha_path = specs_dir / "design" / "alpha.md"
    design_alpha_path.write_text("# alpha\n")
    design_beta_path = specs_dir / "design" / "beta.md"
    design_beta_path.write_text("# beta\n")
    fr_gamma_path = specs_dir / "functional_requirements" / "gamma.md"
    fr_gamma_path.write_text("# gamma\n")
    fr_delta_path = specs_dir / "functional_requirements" / "nested" / "delta.md"
    fr_delta_path.write_text("# delta\n")

    result = find(tmp_path)

    assert result == [
        design_alpha_path,
        design_beta_path,
        fr_gamma_path,
        fr_delta_path,
    ]


@pytest.mark.covers("dsn~discover.find~0")
def test_find_excludes_index_md_navigation_files(tmp_path: pathlib.Path):
    specs_dir = tmp_path / "specs"
    (specs_dir / "design").mkdir(parents=True)
    (specs_dir / "design" / "index.md").write_text("# index\n")
    alpha_path = specs_dir / "design" / "alpha.md"
    alpha_path.write_text("# alpha\n")

    result = find(tmp_path)

    assert result == [alpha_path]


@pytest.mark.covers("dsn~discover.find~0")
def test_find_raises_when_specs_dir_missing(tmp_path: pathlib.Path):
    with pytest.raises(ValueError, match="specs"):
        find(tmp_path)


@pytest.mark.covers("dsn~discover.find~0")
def test_find_raises_when_specs_dir_empty(tmp_path: pathlib.Path):
    (tmp_path / "specs").mkdir()

    with pytest.raises(ValueError, match="specs"):
        find(tmp_path)


@pytest.mark.covers("dsn~discover.find~0")
def test_find_raises_on_unexpected_file_under_specs(tmp_path: pathlib.Path):
    specs_dir = tmp_path / "specs"
    specs_dir.mkdir()
    (specs_dir / "design.md").write_text("# design\n")
    (specs_dir / "notes.md").write_text("# notes\n")

    with pytest.raises(ValueError, match="notes.md"):
        find(tmp_path)


@pytest.mark.covers("dsn~discover.find~0")
def test_find_raises_when_single_file_and_folder_form_both_present(
    tmp_path: pathlib.Path,
):
    specs_dir = tmp_path / "specs"
    specs_dir.mkdir()
    (specs_dir / "design.md").write_text("# design\n")
    (specs_dir / "design").mkdir()
    (specs_dir / "design" / "alpha.md").write_text("# alpha\n")

    with pytest.raises(ValueError, match="design"):
        find(tmp_path)


@pytest.mark.covers("dsn~discover.find~0")
def test_find_raises_on_unexpected_directory_under_specs(tmp_path: pathlib.Path):
    specs_dir = tmp_path / "specs"
    (specs_dir / "design").mkdir(parents=True)
    (specs_dir / "design" / "alpha.md").write_text("# alpha\n")
    (specs_dir / "scratch").mkdir()
    (specs_dir / "scratch" / "draft.md").write_text("# draft\n")

    with pytest.raises(ValueError, match="scratch"):
        find(tmp_path)


@pytest.mark.covers("dsn~discover.find~0")
def test_find_returns_paths_sorted_lexicographically(tmp_path: pathlib.Path):
    """Files created in non-alphabetical order still come back sorted."""
    specs_dir = tmp_path / "specs"
    (specs_dir / "design").mkdir(parents=True)
    (specs_dir / "design" / "index.md").write_text("# index\n")
    delta_path = specs_dir / "design" / "delta.md"
    alpha_path = specs_dir / "design" / "alpha.md"
    gamma_path = specs_dir / "design" / "gamma.md"
    beta_path = specs_dir / "design" / "beta.md"
    delta_path.write_text("# delta\n")
    alpha_path.write_text("# alpha\n")
    gamma_path.write_text("# gamma\n")
    beta_path.write_text("# beta\n")

    result = find(tmp_path)

    assert result == [alpha_path, beta_path, delta_path, gamma_path]


@pytest.mark.covers("dsn~discover.find~0")
def test_find_raises_when_folder_form_missing_index_md(tmp_path: pathlib.Path):
    specs_dir = tmp_path / "specs"
    (specs_dir / "design").mkdir(parents=True)
    (specs_dir / "design" / "alpha.md").write_text("# alpha\n")

    with pytest.raises(ValueError, match="index.md"):
        find(tmp_path)


@pytest.mark.covers("dsn~discover.find~0")
def test_find_raises_on_non_markdown_file_in_nested_folder(tmp_path: pathlib.Path):
    specs_dir = tmp_path / "specs"
    (specs_dir / "design" / "nested").mkdir(parents=True)
    (specs_dir / "design" / "index.md").write_text("# index\n")
    (specs_dir / "design" / "alpha.md").write_text("# alpha\n")
    (specs_dir / "design" / "nested" / "deep.txt").write_text("not a spec")

    with pytest.raises(ValueError, match="deep.txt"):
        find(tmp_path)


@pytest.mark.covers("dsn~discover.find~0")
def test_find_raises_on_non_markdown_file_inside_folder_form(tmp_path: pathlib.Path):
    specs_dir = tmp_path / "specs"
    (specs_dir / "design").mkdir(parents=True)
    (specs_dir / "design" / "index.md").write_text("# index\n")
    (specs_dir / "design" / "alpha.md").write_text("# alpha\n")
    (specs_dir / "design" / "notes.txt").write_text("not a spec")

    with pytest.raises(ValueError, match="notes.txt"):
        find(tmp_path)
