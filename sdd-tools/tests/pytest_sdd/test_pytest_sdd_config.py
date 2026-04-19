"""Tests for pytest_sdd.config — pyproject.toml configuration loading."""

from pathlib import Path

import pytest

from pytest_sdd.config import load_config_from_root


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestLoadConfig:
    def test_loads_spec_dirs(self, tmp_path):
        _write(
            tmp_path / "pyproject.toml",
            """\
[tool.pytest-sdd]
spec_dirs = ["specs/functional_requirements", "specs/design"]
oft_jar = "tools/oft.jar"
""",
        )
        config = load_config_from_root(tmp_path)
        assert config is not None
        assert config.spec_dirs == [
            tmp_path / "specs/functional_requirements",
            tmp_path / "specs/design",
        ]

    def test_no_pyproject_returns_none(self, tmp_path):
        assert load_config_from_root(tmp_path) is None

    def test_no_sdd_section_returns_none(self, tmp_path):
        _write(
            tmp_path / "pyproject.toml",
            """\
[project]
name = "myproject"
""",
        )
        assert load_config_from_root(tmp_path) is None

    def test_string_spec_dir_converted_to_list(self, tmp_path):
        _write(
            tmp_path / "pyproject.toml",
            """\
[tool.pytest-sdd]
spec_dirs = "specs"
oft_jar = "tools/oft.jar"
""",
        )
        config = load_config_from_root(tmp_path)
        assert config is not None
        assert config.spec_dirs == [tmp_path / "specs"]

    def test_oft_jar_resolved(self, tmp_path):
        _write(
            tmp_path / "pyproject.toml",
            """\
[tool.pytest-sdd]
spec_dirs = ["specs"]
oft_jar = "tools/openfasttrace-4.2.2.jar"
""",
        )
        config = load_config_from_root(tmp_path)
        assert config is not None
        assert config.oft_jar == tmp_path / "tools/openfasttrace-4.2.2.jar"

    def test_paths_relative_to_rootdir(self, tmp_path):
        _write(
            tmp_path / "pyproject.toml",
            """\
[tool.pytest-sdd]
spec_dirs = ["specs/functional_requirements"]
oft_jar = "tools/oft.jar"
""",
        )
        config = load_config_from_root(tmp_path)
        assert config is not None
        assert config.spec_dirs[0].parent == tmp_path / "specs"

    def test_missing_spec_dirs_raises(self, tmp_path):
        _write(
            tmp_path / "pyproject.toml",
            """\
[tool.pytest-sdd]
oft_jar = "tools/oft.jar"
""",
        )
        with pytest.raises(ValueError, match="spec_dirs"):
            load_config_from_root(tmp_path)

    def test_missing_oft_jar_raises(self, tmp_path):
        _write(
            tmp_path / "pyproject.toml",
            """\
[tool.pytest-sdd]
spec_dirs = ["specs"]
""",
        )
        with pytest.raises(ValueError, match="oft_jar"):
            load_config_from_root(tmp_path)
