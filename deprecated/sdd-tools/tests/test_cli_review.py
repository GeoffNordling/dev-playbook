"""Tests for sdd_tools.cli.review."""

from __future__ import annotations

from pathlib import Path

from sdd_tools.cli import review as cli


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


class TestEmptyInventory:
    def test_no_reviews_message(self, tmp_path, capsys):
        _write_pyproject(tmp_path)
        (tmp_path / "specs").mkdir()
        code = cli.main(["--root", str(tmp_path)])
        captured = capsys.readouterr()
        assert code == 0
        assert "No AgentReview: fields found" in captured.out


class TestInventoryRendering:
    def test_one_review_one_record(self, tmp_path, capsys):
        _write_pyproject(tmp_path)
        _write_spec(
            tmp_path,
            "specs/design.md",
            "## Data\n\n"
            "### No-filler prompt\n"
            "`dsn~no-filler~1`\n"
            "Status: approved\n"
            "AgentReview: Prompt at src/prompts/agent.md should discourage filler.\n"
            "\n"
            "## API Shape\n\n## Algorithms\n\n## Composition\n",
        )
        code = cli.main(["--root", str(tmp_path)])
        captured = capsys.readouterr()
        assert code == 0
        assert "# AgentReview Inventory" in captured.out
        assert "## `dsn~no-filler~1` — No-filler prompt" in captured.out
        assert "Source: specs/design.md:" in captured.out
        assert "Section: Data" in captured.out
        assert "- Prompt at src/prompts/agent.md should discourage filler." in captured.out

    def test_multiple_reviews_on_one_dsn(self, tmp_path, capsys):
        _write_pyproject(tmp_path)
        _write_spec(
            tmp_path,
            "specs/design.md",
            "## Data\n\n## API Shape\n\n## Algorithms\n\n"
            "## Composition\n\n"
            "### Dual check\n"
            "`dsn~dual~1`\n"
            "Status: approved\n"
            "AgentReview: First check.\n"
            "AgentReview: Second check.\n",
        )
        code = cli.main(["--root", str(tmp_path)])
        captured = capsys.readouterr()
        assert code == 0
        assert captured.out.count("## `dsn~dual~1`") == 1
        assert "- First check." in captured.out
        assert "- Second check." in captured.out

    def test_non_dsn_with_review_excluded(self, tmp_path, capsys):
        """Lint flags AgentReview on non-dsn; the inventory tool still ignores
        them — reviews apply to design commitments only."""
        _write_pyproject(tmp_path)
        _write_spec(
            tmp_path,
            "specs/req.md",
            "### Misplaced\n"
            "`req~misplaced~1`\n"
            "Status: approved\n"
            "AgentReview: Should not appear in inventory.\n"
            "\n"
            "Needs: dsn\n",
        )
        code = cli.main(["--root", str(tmp_path)])
        captured = capsys.readouterr()
        assert code == 0
        assert "No AgentReview: fields found" in captured.out
