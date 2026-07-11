"""Behavioral tests for scripts/skill-audit.

skill-audit declares pyyaml via PEP 723 and imports the local dev_playbook
package, so it is invoked the way pre-commit runs it: `uv run --script`. It
walks skill bundles under .claude/skills/ (no git needed).
"""

import subprocess
from pathlib import Path

SKILL_AUDIT = Path(__file__).resolve().parents[1] / "scripts" / "skill-audit"


def valid_skill(name: str = "greet", body: str = "# Greet\n\nDo the thing.\n") -> str:
    return (
        f"---\nname: {name}\ndescription: A greeting skill\n"
        "disable-model-invocation: true\nmodel: sonnet\neffort: low\n---\n\n"
    ) + body


def make_repo(tmp_path: Path, skills: dict[str, str]) -> Path:
    """Write {skill_name: SKILL.md contents} under .claude/skills/; return root."""
    repo = tmp_path / "repo"
    for name, contents in skills.items():
        path = repo / ".claude" / "skills" / name / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents)
    return repo


def run(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", "--script", str(SKILL_AUDIT), str(repo)],
        capture_output=True,
        text=True,
    )


def test_conforming_skill_is_clean(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"greet": valid_skill()})

    result = run(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""


def test_missing_required_field_is_a_claude_code_finding(tmp_path: Path) -> None:
    skill = "---\nname: greet\nmodel: sonnet\neffort: low\n---\n\n# Greet\n"
    repo = make_repo(tmp_path, {"greet": skill})

    result = run(repo)

    assert result.returncode == 1
    assert ".claude/skills/greet/SKILL.md: claude-code.required-field" in result.stdout


def test_name_mismatch_is_flagged(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"greet": valid_skill(name="hello")})

    result = run(repo)

    assert result.returncode == 1
    assert "claude-code.name-match" in result.stdout


def test_body_length_is_a_stderr_advisory_that_never_fails(tmp_path: Path) -> None:
    long_body = "# Greet\n\n" + "\n".join(f"line {i}" for i in range(200)) + "\n"
    repo = make_repo(tmp_path, {"greet": valid_skill(body=long_body)})

    result = run(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""
    assert "body is" in result.stderr
    assert "body-length" not in result.stdout


def test_list_rules_prints_claude_code_ids_from_any_cwd(tmp_path: Path) -> None:
    result = subprocess.run(
        ["uv", "run", "--script", str(SKILL_AUDIT), "--list-rules"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    ids = result.stdout.split()
    assert "claude-code.required-field" in ids
    assert "claude-code.body-h1" in ids
    assert "body-length" not in " ".join(ids)
    assert all(rule.startswith("claude-code.") for rule in ids), ids


def test_repo_self_scan_is_clean() -> None:
    """The dev-playbook repo's own authored skills pass skill-audit."""
    repo = Path(__file__).resolve().parents[1]
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr
