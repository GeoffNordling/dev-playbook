"""Tests for sdd_tools.cli.atlas."""

from __future__ import annotations

from pathlib import Path

from sdd_tools.cli import atlas as cli


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


class TestErrorPaths:
    def test_no_pyproject_exits_2(self, tmp_path, capsys):
        code = cli.main(["--root", str(tmp_path)])
        assert code == 2
        assert "no [tool.pytest-sdd]" in capsys.readouterr().err


class TestSuccessPath:
    def test_empty_project_still_emits_headers(self, tmp_path, capsys):
        _write_pyproject(tmp_path)
        (tmp_path / "specs").mkdir()
        code = cli.main(["--root", str(tmp_path)])
        captured = capsys.readouterr()
        assert code == 0
        assert "# Spec Atlas" in captured.out
        assert "## Data" in captured.out
        assert "## API Shape" in captured.out

    def test_renders_full_body(self, tmp_path, capsys):
        _write_pyproject(tmp_path)
        _write_spec(
            tmp_path,
            "specs/design.md",
            "## Data\n\n"
            "### Foo Definition\n"
            "`dsn~foo~1`\n"
            "Status: approved\n"
            "\n"
            "The canonical description of foo.\n"
            "\n"
            "Interface: myapp.Foo.render(self) -> str\n"
            "\n"
            "## API Shape\n\n## Algorithms\n\n## Composition\n",
        )
        code = cli.main(["--root", str(tmp_path)])
        captured = capsys.readouterr()
        assert code == 0
        assert "### Foo Definition" in captured.out
        assert "`dsn~foo~1`" in captured.out
        assert "Status: approved" in captured.out
        assert "canonical description of foo" in captured.out
        assert "Interface: myapp.Foo.render(self) -> str" in captured.out
        assert "Source: specs/design.md:" in captured.out

    def test_agent_review_rendered(self, tmp_path, capsys):
        _write_pyproject(tmp_path)
        _write_spec(
            tmp_path,
            "specs/design.md",
            "## Data\n\n"
            "## API Shape\n\n"
            "## Algorithms\n\n"
            "### Filler check\n"
            "`dsn~no-filler~1`\n"
            "Status: approved\n"
            "AgentReview: The prompt at src/prompts/agent.md should discourage filler.\n"
            "\n"
            "## Composition\n",
        )
        code = cli.main(["--root", str(tmp_path)])
        captured = capsys.readouterr()
        assert code == 0
        assert "AgentReview: The prompt at src/prompts/agent.md" in captured.out

    def test_covers_and_needs_rendered(self, tmp_path, capsys):
        _write_pyproject(tmp_path)
        _write_spec(
            tmp_path,
            "specs/design.md",
            "## Data\n\n"
            "### Foo\n"
            "`dsn~foo~1`\n"
            "Status: approved\n"
            "\n"
            "Body.\n"
            "\n"
            "Covers:\n"
            "- req~foo-behavior~1\n"
            "\n"
            "Needs: utest\n"
            "\n"
            "## API Shape\n\n## Algorithms\n\n## Composition\n",
        )
        code = cli.main(["--root", str(tmp_path)])
        captured = capsys.readouterr()
        assert code == 0
        assert "Covers:" in captured.out
        assert "- req~foo-behavior~1" in captured.out
        assert "Needs: utest" in captured.out
