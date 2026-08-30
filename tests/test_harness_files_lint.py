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


def valid_agent(name: str = "scout", body: str = "# Scout\n\nGo look.\n") -> str:
    return (
        f"---\nname: {name}\n"
        "description: Scouts the repo for a topic. Use when a caller "
        "dispatches a scouting task.\n"
        "tools: Read, Bash\nmodel: sonnet\neffort: low\n---\n\n"
    ) + body


def make_agent(repo: Path, filename: str, contents: str) -> None:
    """Write one agent definition under .claude/agents/."""
    path = repo / ".claude" / "agents" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents)


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


def test_user_invocable_is_an_unknown_field(tmp_path: Path) -> None:
    """The retired field gets no special ban — the closed vocabulary catches it."""
    repo = make_repo(
        tmp_path, {"greet": with_field(valid_skill(), "user-invocable: true")}
    )

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "harness.unknown-field" in result.stdout
    assert "user-invocable" in result.stdout


def test_argument_hint_is_an_unknown_field(tmp_path: Path) -> None:
    """The retired argument-hint field is outside the vocabulary."""
    skill = with_field(valid_skill(), 'argument-hint: "[topic]"')
    repo = make_repo(tmp_path, {"greet": skill})

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "harness.unknown-field" in result.stdout
    assert "argument-hint" in result.stdout


def test_arguments_list_of_kebab_names_is_clean(tmp_path: Path) -> None:
    skill = with_field(valid_skill(), "arguments: [subject, issue-number]")
    repo = make_repo(tmp_path, {"greet": skill})

    result = run(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""


def test_arguments_that_is_not_a_list_blocks(tmp_path: Path) -> None:
    skill = with_field(valid_skill(), "arguments: subject")
    repo = make_repo(tmp_path, {"greet": skill})

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "harness.arguments-format" in result.stdout


def test_non_kebab_argument_name_blocks(tmp_path: Path) -> None:
    skill = with_field(valid_skill(), "arguments: [setHint]")
    repo = make_repo(tmp_path, {"greet": skill})

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "harness.arguments-format" in result.stdout
    assert "setHint" in result.stdout


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
    assert "harness.arguments-format" in ids
    assert "harness.tools-format" in ids
    assert "harness.banned-field" not in ids
    assert "body-length" not in " ".join(ids)
    assert all(rule.startswith("harness.") for rule in ids), ids


def test_repo_self_scan_is_clean() -> None:
    """The dev-playbook repo's own authored runbooks pass harness-files-lint."""
    repo = Path(__file__).resolve().parents[1]
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_conforming_agent_is_clean(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    make_agent(repo, "scout.md", valid_agent())

    result = run(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""
    assert "1 agents" in result.stderr


def test_agent_name_must_match_file_stem(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    make_agent(repo, "lookout.md", valid_agent(name="scout"))

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "harness.name-match" in result.stdout
    assert "file stem" in result.stdout


def test_skill_only_field_on_an_agent_is_unknown(tmp_path: Path) -> None:
    """The agent vocabulary is closed to its five fields."""
    agent = valid_agent().replace(
        "effort: low\n", "effort: low\ndisable-model-invocation: false\n", 1
    )
    repo = tmp_path / "repo"
    make_agent(repo, "scout.md", agent)

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "harness.unknown-field" in result.stdout
    assert "disable-model-invocation" in result.stdout


def test_agent_tools_must_be_a_string(tmp_path: Path) -> None:
    agent = valid_agent().replace("tools: Read, Bash\n", "tools: [Read, Bash]\n", 1)
    repo = tmp_path / "repo"
    make_agent(repo, "scout.md", agent)

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "harness.tools-format" in result.stdout


def test_agent_description_takes_the_two_sentence_shape(tmp_path: Path) -> None:
    """Agents carry no disable-model-invocation, so the trigger sentence binds."""
    agent = valid_agent().replace(
        "description: Scouts the repo for a topic. Use when a caller "
        "dispatches a scouting task.\n",
        "description: Scouts the repo for a topic.\n",
        1,
    )
    repo = tmp_path / "repo"
    make_agent(repo, "scout.md", agent)

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "harness.description-sentences" in result.stdout
    assert "must be exactly 2" in result.stdout


def test_agent_without_tools_field_is_clean(tmp_path: Path) -> None:
    """tools is optional: omitting it grants the full toolset, not a finding."""
    agent = valid_agent().replace("tools: Read, Bash\n", "", 1)
    repo = tmp_path / "repo"
    make_agent(repo, "scout.md", agent)

    result = run(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""


# --- the global CLAUDE.md source (dev-playbook only) ---

# A conformant global CLAUDE.md source: the two buckets, in order, carrying the
# workspace-wide rules.
GLOBAL_VALID = (
    "# Global\n\n"
    "## Principles\n\n"
    "### Be terse\n\nBe terse.\n\n"
    "## Behaviors\n\n"
    "### Read the standards\n\nRead the catalog first.\n\n"
    "### Navigate docs by index\n\nWalk the index descriptions.\n\n"
    "### Teach unfamiliar terms\n\nExplain the unfamiliar term.\n"
)


def make_global_claude(tmp_path: Path, contents: str) -> Path:
    """Write a global CLAUDE.md source into a fresh repo and return its root."""
    repo = tmp_path / "repo"
    path = repo / "dotfiles" / "dot-claude" / "CLAUDE.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents)
    return repo


def test_global_claude_valid_passes(tmp_path: Path) -> None:
    result = run(make_global_claude(tmp_path, GLOBAL_VALID))

    assert result.returncode == 0, result.stdout + result.stderr


def test_global_claude_extra_section_fails(tmp_path: Path) -> None:
    repo = make_global_claude(tmp_path, GLOBAL_VALID + "\n## Extras\n\nNope.\n")

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "dotfiles/dot-claude/CLAUDE.md: harness.global-claude-shape" in result.stdout


def test_global_claude_sections_out_of_order_fails(tmp_path: Path) -> None:
    repo = make_global_claude(
        tmp_path,
        "# Global\n\n"
        "## Behaviors\n\n"
        "### Read the standards\n\nRead the catalog first.\n\n"
        "### Navigate docs by index\n\nWalk the index descriptions.\n\n"
        "## Principles\n\n"
        "### Be terse\n\nBe terse.\n",
    )

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "dotfiles/dot-claude/CLAUDE.md: harness.global-claude-shape" in result.stdout


def test_global_claude_missing_workspace_rule_fails(tmp_path: Path) -> None:
    # No repo's own CLAUDE.md restates these, so dropping one here would leave
    # the instruction stationed nowhere.
    repo = make_global_claude(
        tmp_path,
        GLOBAL_VALID.replace(
            "### Navigate docs by index\n\nWalk the index descriptions.\n\n", ""
        ),
    )

    result = run(repo)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "dotfiles/dot-claude/CLAUDE.md: harness.global-claude-rules" in result.stdout
    assert "Navigate docs by index" in result.stdout


def test_global_claude_fenced_heading_is_not_a_section(tmp_path: Path) -> None:
    # A worked example inside a fence is illustration, not structure.
    repo = make_global_claude(
        tmp_path,
        GLOBAL_VALID + "\n```markdown\n## Extras\n\nAn example, not a section.\n```\n",
    )

    result = run(repo)

    assert result.returncode == 0, result.stdout + result.stderr


def test_global_claude_absent_gates_the_check(tmp_path: Path) -> None:
    # Owning-repo gate: a repo with no global source — even one carrying an
    # ordinary nested CLAUDE.md — emits no global-claude-* finding.
    repo = tmp_path / "repo"
    (repo / "sub").mkdir(parents=True)
    (repo / "sub" / "CLAUDE.md").write_text("Operate carefully.\n")

    result = run(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "global-claude" not in result.stdout
