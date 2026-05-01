"""Tests for sdd_tools.config."""

from pathlib import Path

import pytest

from sdd_tools.config import find_project_root, load_config_from_root


def _write_pyproject(root: Path, body: str) -> None:
    (root / "pyproject.toml").write_text(body, encoding="utf-8")


class TestLoadConfig:
    def test_no_pyproject_returns_none(self, tmp_path):
        assert load_config_from_root(tmp_path) is None

    def test_no_section_returns_none(self, tmp_path):
        _write_pyproject(tmp_path, '[project]\nname = "x"\n')
        assert load_config_from_root(tmp_path) is None

    def test_minimal_config(self, tmp_path):
        _write_pyproject(
            tmp_path,
            '[tool.pytest-sdd]\n'
            'spec_dirs = ["specs"]\n'
            'oft_jar = "lib/oft.jar"\n',
        )
        config = load_config_from_root(tmp_path)
        assert config is not None
        assert config.spec_dirs == [tmp_path / "specs"]
        assert config.oft_jar == tmp_path / "lib" / "oft.jar"

    def test_string_spec_dir_normalized_to_list(self, tmp_path):
        _write_pyproject(
            tmp_path,
            '[tool.pytest-sdd]\n'
            'spec_dirs = "specs"\n'
            'oft_jar = "oft.jar"\n',
        )
        config = load_config_from_root(tmp_path)
        assert config is not None
        assert config.spec_dirs == [tmp_path / "specs"]

    def test_missing_spec_dirs_raises(self, tmp_path):
        _write_pyproject(
            tmp_path,
            '[tool.pytest-sdd]\noft_jar = "oft.jar"\n',
        )
        with pytest.raises(ValueError, match="spec_dirs"):
            load_config_from_root(tmp_path)

    def test_missing_oft_jar_raises(self, tmp_path):
        _write_pyproject(
            tmp_path,
            '[tool.pytest-sdd]\nspec_dirs = ["specs"]\n',
        )
        with pytest.raises(ValueError, match="oft_jar"):
            load_config_from_root(tmp_path)


class TestFindProjectRoot:
    def test_returns_dir_with_pyproject(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("")
        sub = tmp_path / "a" / "b"
        sub.mkdir(parents=True)
        assert find_project_root(sub) == tmp_path

    def test_returns_start_when_none_found(self, tmp_path):
        sub = tmp_path / "deep"
        sub.mkdir()
        # parents include tmp_path which has no pyproject.toml in this fresh dir
        assert find_project_root(sub) == sub
