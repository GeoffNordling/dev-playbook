"""Behavioral tests for the judgments-lint validation: loader.lint and the hook."""

import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from judgments.loader import lint

CONFIG = '[tool.judgments]\npaths = ["judgments/*.yaml"]\n'
TOOLS_DIR = Path(__file__).resolve().parents[1]
LINT_HOOK = TOOLS_DIR / "bin" / "judgments-lint"


def judgment_yaml(
    evidence: str = "[docs/errors.md]", model: str = "claude-sonnet-4-6"
) -> str:
    """Render a one-judgment declaration with controllable evidence and model."""
    return (
        "judgments:\n"
        "  - id: j1\n"
        "    claim: a claim\n"
        f"    evidence: {evidence}\n"
        f"    model: {model}\n"
        "    effort: high\n"
    )


def clean_repo(make_repo: Callable[[dict[str, str]], Path]) -> Path:
    """A repo whose single judgment is structurally valid with existing evidence."""
    return make_repo(
        {
            "pyproject.toml": CONFIG,
            "judgments/a.yaml": judgment_yaml(),
            "docs/errors.md": "errors\n",
        }
    )


def test_lint_passes_a_clean_repo(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    assert lint(clean_repo(make_repo)) == []


def test_lint_returns_empty_for_a_repo_with_no_config() -> None:
    assert lint(None) == []


def test_lint_reports_a_missing_evidence_file(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo(
        {"pyproject.toml": CONFIG, "judgments/a.yaml": judgment_yaml("[docs/gone.md]")}
    )

    errors = lint(repo)

    assert len(errors) == 1
    assert "docs/gone.md" in errors[0]


def test_lint_reports_an_absolute_evidence_path(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo(
        {"pyproject.toml": CONFIG, "judgments/a.yaml": judgment_yaml("[/etc/hosts]")}
    )

    errors = lint(repo)

    assert any("/etc/hosts" in error for error in errors)


def test_lint_reports_a_parent_escape_evidence_path(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo(
        {"pyproject.toml": CONFIG, "judgments/a.yaml": judgment_yaml("[../escape.md]")}
    )

    errors = lint(repo)

    assert any(".." in error for error in errors)


def test_lint_surfaces_a_structural_error_from_the_loader(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo(
        {"pyproject.toml": CONFIG, "judgments/a.yaml": judgment_yaml(model="gpt-4")}
    )

    errors = lint(repo)

    assert any("model" in error for error in errors)


def test_lint_reports_every_missing_path_not_just_the_first(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo(
        {
            "pyproject.toml": CONFIG,
            "judgments/a.yaml": judgment_yaml("[a.md, b.md]"),
        }
    )

    errors = lint(repo)

    assert len(errors) == 2


def _run_hook(repo: Path) -> subprocess.CompletedProcess[str]:
    """Run the judgments-lint hook script against ``repo`` as its working dir."""
    return subprocess.run(
        [sys.executable, str(LINT_HOOK)],
        cwd=repo,
        env={**os.environ, "PYTHONPATH": str(TOOLS_DIR / "src")},
        capture_output=True,
        text=True,
    )


def test_hook_exits_zero_on_a_clean_repo(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    result = _run_hook(clean_repo(make_repo))

    assert result.returncode == 0, result.stderr


def test_hook_exits_nonzero_and_names_the_path_on_a_broken_repo(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo(
        {"pyproject.toml": CONFIG, "judgments/a.yaml": judgment_yaml("[docs/gone.md]")}
    )

    result = _run_hook(repo)

    assert result.returncode != 0
    assert "docs/gone.md" in result.stderr
