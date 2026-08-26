"""Behavioral tests for scripts/harness-files-lint.

harness-files-lint declares pyyaml via PEP 723 and imports the local dev_playbook
package, so it is invoked the way pre-commit runs it: `uv run --script`. It
walks skill bundles under .claude/skills/ (no git needed).
"""

import subprocess
from pathlib import Path

HARNESS_FILES_LINT = (
    Path(__file__).resolve().parents[1] / "scripts" / "harness-files-lint"
)


def valid_skill(name: str = "greet", body: str = "# Greet\n\nDo the thing.\n") -> str:
    return (
        f"---\nname: {name}\n"
        "description: Greet the user by name. Use when the user asks for a greeting.\n"
        "disable-model-invocation: false\nmodel: sonnet\neffort: low\n---\n\n"
    ) + body


def with_field(skill: str, line: str) -> str:
    """Return `skill` with one extra front matter line after `effort`."""
    return skill.replace("effort: low\n", f"effort: low\n{line}\n", 1)


def with_description(skill: str, description: str) -> str:
    return skill.replace(
        "description: Greet the user by name. Use when the user asks for a greeting.",
        f"description: {description}",
        1,
    )


def with_user_invocation(skill: str) -> str:
    """Return `skill` switched to user-invoked only."""
    return skill.replace(
        "disable-model-invocation: false", "disable-model-invocation: true", 1
    )


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
        ["uv", "run", "--script", str(HARNESS_FILES_LINT), str(repo)],
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


def test_missing_required_field_is_a_harness_finding(tmp_path: Path) -> None:
    skill = "---\nname: greet\nmodel: sonnet\neffort: low\n---\n\n# Greet\n"
    repo = make_repo(tmp_path, {"greet": skill})

    result = run(repo)

    assert result.returncode == 1
    assert ".claude/skills/greet/SKILL.md: harness.required-field" in result.stdout


def test_unclosed_front_matter_names_what_is_wrong(tmp_path: Path) -> None:
    """The parse finding says the delimiter is missing, not 'substring not found'."""
    skill = valid_skill().replace("---\n\n", "\n", 1)
    repo = make_repo(tmp_path, {"greet": skill})

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "harness.parse" in result.stdout
    assert "never closed" in result.stdout


def test_name_mismatch_is_flagged(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"greet": valid_skill(name="hello")})

    result = run(repo)

    assert result.returncode == 1
    assert "harness.name-match" in result.stdout


def test_body_length_is_a_stderr_advisory_that_never_fails(tmp_path: Path) -> None:
    long_body = "# Greet\n\n" + "\n".join(f"line {i}" for i in range(600)) + "\n"
    repo = make_repo(tmp_path, {"greet": valid_skill(body=long_body)})

    result = run(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""
    assert "body is" in result.stderr
    assert "body-length" not in result.stdout


def test_body_under_the_advisory_threshold_is_silent(tmp_path: Path) -> None:
    """251 lines tripped the old ~100-line threshold; at ~500 it does not."""
    body = "# Greet\n\n" + "\n".join(f"line {i}" for i in range(249)) + "\n"
    repo = make_repo(tmp_path, {"greet": valid_skill(body=body)})

    result = run(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "body is" not in result.stderr


def test_description_that_is_not_two_sentences_blocks(tmp_path: Path) -> None:
    """The two-sentence shape, on the model-invoked skills it binds."""
    skill = with_description(valid_skill(), "Greet the user by name.")
    repo = make_repo(tmp_path, {"greet": skill})

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "harness.description-sentences" in result.stdout


def test_unterminated_description_counts_as_zero_sentences(tmp_path: Path) -> None:
    """A bare fragment with no terminal punctuation is not one sentence."""
    skill = with_description(valid_skill(), "Greet the user by name")
    repo = make_repo(tmp_path, {"greet": skill})

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "is 0 sentence(s)" in result.stdout


def test_trigger_rule_binds_a_model_invoked_skill(tmp_path: Path) -> None:
    """A second sentence that names no trigger fails the match-surface rule."""
    skill = with_description(
        valid_skill(), "Greet the user by name. Invoked from the greeting menu."
    )
    repo = make_repo(tmp_path, {"greet": skill})

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "harness.description-trigger" in result.stdout


def test_a_user_invoked_description_is_one_sentence(tmp_path: Path) -> None:
    """No model loads it, so it is the user's one-line label and nothing more."""
    skill = with_user_invocation(
        with_description(valid_skill(), "Greet the user by name.")
    )
    repo = make_repo(tmp_path, {"greet": skill})

    result = run(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""


def test_a_user_invoked_description_carrying_a_trigger_blocks(tmp_path: Path) -> None:
    """The two-sentence form fails the other way round: one sentence is the rule."""
    skill = with_user_invocation(valid_skill())
    repo = make_repo(tmp_path, {"greet": skill})

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "harness.description-sentences" in result.stdout
    assert "must be exactly 1" in result.stdout


def test_a_malformed_invocation_field_keeps_the_strict_description_rule(
    tmp_path: Path,
) -> None:
    """Only a literal `true` opens the free-shape path; anything else is strict."""
    skill = with_description(valid_skill(), "Greet the user by name.").replace(
        "disable-model-invocation: false", "disable-model-invocation: sometimes", 1
    )
    repo = make_repo(tmp_path, {"greet": skill})

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "harness.description-sentences" in result.stdout


def test_use_when_must_open_the_second_sentence(tmp_path: Path) -> None:
    """A substring match is not enough — the marker anchors sentence two."""
    skill = with_description(
        valid_skill(), "Greet the user by name. Reach for it when needed."
    )
    repo = make_repo(tmp_path, {"greet": skill})

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "harness.description-trigger" in result.stdout


def test_period_inside_a_token_does_not_end_a_sentence(tmp_path: Path) -> None:
    skill = with_description(
        valid_skill(),
        "Promote a candidate to an issue. Use when the user names an entry in "
        "CANDIDATES.md they now want built.",
    )
    repo = make_repo(tmp_path, {"greet": skill})

    result = run(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""


def test_unknown_frontmatter_field_blocks(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"greet": with_field(valid_skill(), "turns: many")})

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "harness.unknown-field" in result.stdout
    assert "turns" in result.stdout


def test_disallowed_tools_is_a_documented_field(tmp_path: Path) -> None:
    skill = with_field(valid_skill(), "disallowed-tools: Edit MultiEdit Write(/**)")
    repo = make_repo(tmp_path, {"greet": skill})

    result = run(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""


def test_user_invocable_is_reported_once_as_a_banned_field(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path, {"greet": with_field(valid_skill(), "user-invocable: true")}
    )

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "harness.banned-field" in result.stdout
    assert "harness.unknown-field" not in result.stdout


def test_dot_directory_under_a_skill_root_is_not_a_skill(tmp_path: Path) -> None:
    """Harness scratch (e.g. .cc-writes) must not be counted as a bundle."""
    repo = make_repo(tmp_path, {"greet": valid_skill()})
    scratch = repo / ".claude" / "skills" / ".cc-writes"
    scratch.mkdir(parents=True)
    (scratch / "note.txt").write_text("harness scratch\n")

    result = run(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""
    assert "1 internal skills" in result.stderr


def test_a_directory_with_no_skill_md_is_an_error_state(tmp_path: Path) -> None:
    """Auditing nothing would leave it in a skill count the scan never covered."""
    repo = make_repo(tmp_path, {"greet": valid_skill()})
    (repo / ".claude" / "skills" / "halfbuilt").mkdir()

    result = run(repo)

    assert result.returncode == 2, result.stdout + result.stderr
    assert "halfbuilt" in result.stderr
    assert "no SKILL.md" in result.stderr


def test_list_rules_prints_harness_ids_from_any_cwd(tmp_path: Path) -> None:
    result = subprocess.run(
        ["uv", "run", "--script", str(HARNESS_FILES_LINT), "--list-rules"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    ids = result.stdout.split()
    assert "harness.required-field" in ids
    assert "harness.body-h1" in ids
    assert "harness.description-sentences" in ids
    assert "harness.unknown-field" in ids
    assert "body-length" not in " ".join(ids)
    assert all(rule.startswith("harness.") for rule in ids), ids


def test_repo_self_scan_is_clean() -> None:
    """The dev-playbook repo's own authored skills pass harness-files-lint."""
    repo = Path(__file__).resolve().parents[1]
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_missing_mirror_symlink_is_a_skill_mirror_finding(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    agents_skill(repo, "caveman")
    claude_skills_dir(repo)  # exists, but carries no mirror symlink for caveman

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "harness.skill-mirror" in result.stdout
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
    assert "harness.skill-mirror" in result.stdout
    assert "dot-claude/skills/foo" in result.stdout


def test_list_rules_includes_skill_mirror(tmp_path: Path) -> None:
    result = subprocess.run(
        ["uv", "run", "--script", str(HARNESS_FILES_LINT), "--list-rules"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "harness.skill-mirror" in result.stdout.split()


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
    assert "harness.skill-mirror" in result.stdout
    assert "dot-claude/skills/gone" in result.stdout


def test_real_entry_colliding_with_agents_skill_is_a_finding(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    agents_skill(repo, "foo")
    # dot-claude/skills/foo is a real bundle, not a symlink: an authored skill
    # collides with the same-named externally-managed one.
    foo = claude_skills_dir(repo) / "foo"
    foo.mkdir()
    (foo / "SKILL.md").write_text(valid_skill(name="foo"))

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "harness.skill-mirror" in result.stdout
    assert "dot-claude/skills/foo" in result.stdout
