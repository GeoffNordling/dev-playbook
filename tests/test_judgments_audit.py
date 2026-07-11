"""Behavioral tests for judgments-audit: loader.lint_findings and the hook."""

import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from dev_playbook.judgments.loader import lint_findings

CONFIG = '[tool.judgments]\npaths = ["judgments/*.yaml"]\n'
REPO_ROOT = Path(__file__).resolve().parents[1]
LINT_HOOK = REPO_ROOT / "scripts" / "judgments-audit"


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
    assert lint_findings(clean_repo(make_repo)) == []


def test_lint_returns_empty_for_a_repo_with_no_config() -> None:
    assert lint_findings(None) == []


def test_missing_evidence_file_is_an_evidence_path_finding_at_the_yaml(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo(
        {"pyproject.toml": CONFIG, "judgments/a.yaml": judgment_yaml("[docs/gone.md]")}
    )

    findings = lint_findings(repo)

    assert len(findings) == 1
    assert findings[0].location == "judgments/a.yaml"
    assert findings[0].rule == "judgments.evidence-path"
    assert "docs/gone.md" in findings[0].message


def test_lint_reports_an_absolute_evidence_path(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo(
        {"pyproject.toml": CONFIG, "judgments/a.yaml": judgment_yaml("[/etc/hosts]")}
    )

    findings = lint_findings(repo)

    assert any("/etc/hosts" in f.message for f in findings)


def test_lint_reports_a_parent_escape_evidence_path(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo(
        {"pyproject.toml": CONFIG, "judgments/a.yaml": judgment_yaml("[../escape.md]")}
    )

    findings = lint_findings(repo)

    assert any(".." in f.message for f in findings)


def test_structural_error_is_a_declaration_finding(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo(
        {"pyproject.toml": CONFIG, "judgments/a.yaml": judgment_yaml(model="gpt-4")}
    )

    findings = lint_findings(repo)

    assert any(
        f.rule == "judgments.declaration" and "model" in f.message for f in findings
    )


def test_lint_reports_every_missing_path_not_just_the_first(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo(
        {
            "pyproject.toml": CONFIG,
            "judgments/a.yaml": judgment_yaml("[a.md, b.md]"),
        }
    )

    findings = lint_findings(repo)

    assert len(findings) == 2


def test_no_finding_message_leaks_the_absolute_repo_path(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    """A malformed declaration's finding carries path-free detail; the absolute
    repo/source path must never leak into a message. The location is a separate,
    repo-relative field, so a reworded error can never smuggle a path in."""
    repo = make_repo(
        {
            "pyproject.toml": CONFIG,
            "judgments/a.yaml": "judgments: 5\n",  # 'judgments' must be a list
            "judgments/b.yaml": judgment_yaml(model="gpt-4"),  # bad field value
        }
    )

    findings = lint_findings(repo)

    assert findings
    assert all(str(repo) not in f.message for f in findings)


def _run_hook(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run the judgments-audit hook script against ``repo`` as its working dir."""
    return subprocess.run(
        [sys.executable, str(LINT_HOOK), *args],
        cwd=repo,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT / "src")},
        capture_output=True,
        text=True,
    )


def test_hook_exits_zero_on_a_clean_repo(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    result = _run_hook(clean_repo(make_repo))

    assert result.returncode == 0, result.stderr


def test_hook_prints_gnu_finding_to_stdout_on_a_broken_repo(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo(
        {"pyproject.toml": CONFIG, "judgments/a.yaml": judgment_yaml("[docs/gone.md]")}
    )

    result = _run_hook(repo)

    assert result.returncode != 0
    assert "judgments/a.yaml: judgments.evidence-path" in result.stdout
    assert "docs/gone.md" in result.stdout


def test_hook_list_rules_prints_judgments_prefixed_ids(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    result = _run_hook(clean_repo(make_repo), "--list-rules")

    assert result.returncode == 0, result.stderr
    ids = result.stdout.split()
    assert "judgments.declaration" in ids
    assert "judgments.evidence-path" in ids
    assert all(rule.startswith("judgments.") for rule in ids), ids
