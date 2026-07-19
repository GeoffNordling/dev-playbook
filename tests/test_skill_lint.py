"""Behavioral tests for scripts/skill-lint.

skill-lint declares pyyaml via PEP 723 and imports the local dev_playbook
package, so it is invoked the way pre-commit runs it: `uv run --script`. It
walks skill bundles under .claude/skills/ (no git needed).
"""

import subprocess
from pathlib import Path

SKILL_AUDIT = Path(__file__).resolve().parents[1] / "scripts" / "skill-lint"


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


def agents_skill(repo: Path, name: str) -> None:
    """Create an externally-managed skill directory under dotfiles/.agents/skills/."""
    (repo / "dotfiles" / ".agents" / "skills" / name).mkdir(parents=True, exist_ok=True)


def claude_skills_dir(repo: Path) -> Path:
    """Create and return the dotfiles/dot-claude/skills/ mirror directory."""
    d = repo / "dotfiles" / "dot-claude" / "skills"
    d.mkdir(parents=True, exist_ok=True)
    return d


def mirror_link(repo: Path, name: str, target: str) -> None:
    """Create a symlink dot-claude/skills/<name> pointing at the literal target."""
    (claude_skills_dir(repo) / name).symlink_to(target)


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
    """The dev-playbook repo's own authored skills pass skill-lint."""
    repo = Path(__file__).resolve().parents[1]
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_missing_mirror_symlink_is_a_skill_mirror_finding(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    agents_skill(repo, "caveman")
    claude_skills_dir(repo)  # exists, but carries no mirror symlink for caveman

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "claude-code.skill-mirror" in result.stdout
    assert "caveman" in result.stdout


def test_agents_tree_without_mirror_dir_fails_loudly(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    agents_skill(repo, "caveman")
    # dotfiles/dot-claude/skills/ deliberately absent: an error state, since the
    # mirror directory always exists in a repo that has externally-managed skills.

    result = run(repo)

    assert result.returncode == 2, result.stdout + result.stderr
    assert "dot-claude/skills" in result.stderr


def test_mirror_symlink_pointing_elsewhere_is_a_finding(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    agents_skill(repo, "foo")
    agents_skill(repo, "bar")
    mirror_link(repo, "bar", "../../.agents/skills/bar")  # correct
    mirror_link(repo, "foo", "../../.agents/skills/bar")  # resolves, wrong target

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "claude-code.skill-mirror" in result.stdout
    assert "dot-claude/skills/foo" in result.stdout


def test_list_rules_includes_skill_mirror(tmp_path: Path) -> None:
    result = subprocess.run(
        ["uv", "run", "--script", str(SKILL_AUDIT), "--list-rules"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "claude-code.skill-mirror" in result.stdout.split()


def test_correctly_mirrored_tree_is_clean(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    agents_skill(repo, "caveman")
    mirror_link(repo, "caveman", "../../.agents/skills/caveman")

    result = run(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""


def test_mirror_is_inert_without_agents_tree(tmp_path: Path) -> None:
    # An authored-skills repo with a mirror directory but no externally-managed
    # tree: the mirror check never activates.
    repo = make_repo(tmp_path, {"greet": valid_skill()})
    claude_skills_dir(repo)  # dot-claude/skills exists; .agents/skills does not

    result = run(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""


def test_stale_mirror_symlink_is_a_finding(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    agents_skill(repo, "foo")
    mirror_link(repo, "foo", "../../.agents/skills/foo")  # correct, resolves
    mirror_link(repo, "gone", "../../.agents/skills/gone")  # target removed: stale

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "claude-code.skill-mirror" in result.stdout
    assert "dot-claude/skills/gone" in result.stdout


def test_real_entry_colliding_with_agents_skill_is_a_finding(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    agents_skill(repo, "foo")
    # dot-claude/skills/foo is a real directory, not a symlink: an authored skill
    # collides with the same-named externally-managed one.
    (claude_skills_dir(repo) / "foo").mkdir()

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "claude-code.skill-mirror" in result.stdout
    assert "dot-claude/skills/foo" in result.stdout
