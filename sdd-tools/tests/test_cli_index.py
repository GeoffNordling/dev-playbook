"""Tests for sdd_tools.cli.index."""

from __future__ import annotations

from pathlib import Path

from sdd_tools.cli import index as cli


def _write_pyproject(root: Path) -> None:
    (root / "pyproject.toml").write_text(
        '[tool.pytest-sdd]\n'
        'spec_dirs = ["specs"]\n'
        'oft_jar = "oft.jar"\n',
        encoding="utf-8",
    )


def _write_spec(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


class TestBuildParser:
    def test_root_flag(self):
        args = cli.build_parser().parse_args(["--root", "/tmp/x"])
        assert args.root == Path("/tmp/x")

    def test_default_root_none(self):
        args = cli.build_parser().parse_args([])
        assert args.root is None


class TestErrorPaths:
    def test_no_pyproject_exits_2(self, tmp_path, capsys):
        code = cli.main(["--root", str(tmp_path)])
        assert code == 2
        assert "no [tool.pytest-sdd]" in capsys.readouterr().err

    def test_malformed_config_exits_2(self, tmp_path, capsys):
        (tmp_path / "pyproject.toml").write_text(
            '[tool.pytest-sdd]\noft_jar = "x.jar"\n', encoding="utf-8"
        )
        code = cli.main(["--root", str(tmp_path)])
        assert code == 2
        assert "spec_dirs" in capsys.readouterr().err


class TestSuccessPath:
    def test_empty_project_still_emits_headers(self, tmp_path, capsys):
        _write_pyproject(tmp_path)
        (tmp_path / "specs").mkdir()
        code = cli.main(["--root", str(tmp_path)])
        captured = capsys.readouterr()
        assert code == 0
        assert "# Spec Index" in captured.out
        assert "## Data" in captured.out
        assert "## API Shape" in captured.out
        assert "## Algorithms" in captured.out
        assert "## Composition" in captured.out

    def test_one_dsn_under_data(self, tmp_path, capsys):
        _write_pyproject(tmp_path)
        _write_spec(
            tmp_path,
            "specs/design.md",
            "## Data\n\n"
            "### Foo\n`dsn~foo~1`\nStatus: approved\n\n"
            "Body of foo.\n"
            "\n"
            "## API Shape\n\n## Algorithms\n\n## Composition\n",
        )
        code = cli.main(["--root", str(tmp_path)])
        captured = capsys.readouterr()
        assert code == 0
        assert "- `dsn~foo~1` — Foo (specs/design.md:" in captured.out

    def test_items_grouped_by_dimension(self, tmp_path, capsys):
        _write_pyproject(tmp_path)
        _write_spec(
            tmp_path,
            "specs/design.md",
            "## Data\n\n"
            "### Foo\n`dsn~foo~1`\nStatus: approved\n\n"
            "\n"
            "## API Shape\n\n"
            "### Bar\n`dsn~bar~1`\nStatus: approved\n\n"
            "\n"
            "## Algorithms\n\n## Composition\n",
        )
        code = cli.main(["--root", str(tmp_path)])
        captured = capsys.readouterr()
        assert code == 0
        data_idx = captured.out.index("## Data")
        api_idx = captured.out.index("## API Shape")
        foo_idx = captured.out.index("dsn~foo~1")
        bar_idx = captured.out.index("dsn~bar~1")
        assert data_idx < foo_idx < api_idx < bar_idx

    def test_non_dsn_items_excluded(self, tmp_path, capsys):
        _write_pyproject(tmp_path)
        # Even if a req accidentally appears under a dimension header, index
        # excludes it (index is a dsn-only projection).
        _write_spec(
            tmp_path,
            "specs/design.md",
            "## Data\n\n"
            "### Misplaced\n`req~misplaced~1`\nStatus: approved\n\n"
            "### Real\n`dsn~real~1`\nStatus: approved\n\n"
            "\n"
            "## API Shape\n\n## Algorithms\n\n## Composition\n",
        )
        code = cli.main(["--root", str(tmp_path)])
        captured = capsys.readouterr()
        assert code == 0
        assert "dsn~real~1" in captured.out
        assert "req~misplaced~1" not in captured.out
