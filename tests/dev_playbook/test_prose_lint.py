"""Behavioral tests for the prose-lint detector, src/dev_playbook/prose_lint.py.

The rule prose.spelling flags the British judgement / judgements form
in authored Markdown; prose.the-banned-word flags the banned actor noun "human" in
every tracked file, with no code-span or fence escape; prose.the-repo-vocabulary
flags a word the repo's own .prose-lint-vocabulary bans, in the directories the
entry names. This test file is listed in dev-playbook's own .prose-lint-exempt
— its fixtures must name the word to test it. The scanning logic is tested with string inputs;
the discovery, exclusion, and CLI behaviors are tested over throwaway git repos
(discovery goes through git ls-files, so every fixture is a git repo).
"""

import os
import subprocess
from pathlib import Path

import pytest

from dev_playbook import prose_lint
from dev_playbook.repo_init import RepoInitError, RepoSpec, render_tree

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "prose-lint"


def make_repo(tmp_path: Path, files: dict[str, str]) -> Path:
    """Write files into a fresh git repo and return its root."""
    repo = tmp_path / "repo"
    for rel, content in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    return repo


# --- scan_text: the rule over string inputs ---


def test_flags_british_singular() -> None:
    findings = prose_lint.scan_text("f.md", "a judgement call\n")

    assert len(findings) == 1
    assert findings[0].rule == prose_lint.SPELLING
    assert findings[0].line == 1


def test_flags_british_plural() -> None:
    findings = prose_lint.scan_text("f.md", "two judgements later\n")

    assert len(findings) == 1


def test_american_spelling_is_clean() -> None:
    assert prose_lint.scan_text("f.md", "a judgment call\n") == []


def test_flags_capitalized_form() -> None:
    findings = prose_lint.scan_text("f.md", "Judgement matters here\n")

    assert len(findings) == 1


def test_judgemental_is_not_flagged() -> None:
    # The rule matches the words judgement / judgements only, not longer words
    # that merely contain the sequence.
    assert prose_lint.scan_text("f.md", "a judgemental tone\n") == []


def test_inline_code_span_is_skipped() -> None:
    assert prose_lint.scan_text("f.md", "the `judgement` token is fine\n") == []


def test_double_backtick_code_span_is_skipped() -> None:
    # A double-backtick span (the form used when the code itself contains a
    # backtick) must be stripped whole — not read as two adjacent empty
    # single-backtick spans that leave the word exposed to the scanner.
    assert prose_lint.scan_text("f.md", "the ``judgement`` token is fine\n") == []


def test_fenced_block_is_skipped() -> None:
    assert prose_lint.scan_text("f.md", "before\n```\njudgement\n```\nafter\n") == []


def test_reports_the_offending_line_number() -> None:
    findings = prose_lint.scan_text("f.md", "clean\nline\na judgement here\n")

    assert findings[0].line == 3


# --- scan_banned: the banned-word rule over string inputs ---


def test_flags_banned_actor_noun() -> None:
    findings = prose_lint.scan_banned("f.md", "ask the human first\n")

    assert len(findings) == 1
    assert findings[0].rule == prose_lint.THE_BANNED_WORD
    assert findings[0].line == 1


def test_flags_plural_and_capitalized_forms() -> None:
    findings = prose_lint.scan_banned("f.md", "Humans differ.\nHUMAN input.\n")

    assert [f.line for f in findings] == [1, 2]


def test_flags_hyphenated_compound() -> None:
    # The word boundary sits at the hyphen, so compounds are the noun too.
    findings = prose_lint.scan_banned("f.md", "a human-readable name\n")

    assert len(findings) == 1


def test_longer_words_are_not_the_noun() -> None:
    assert prose_lint.scan_banned("f.md", "a humane, superhuman effort\n") == []


def test_code_span_is_not_an_escape_for_the_ban() -> None:
    # Unlike the spelling rule, the ban is absolute: backticks do not shelter it.
    assert len(prose_lint.scan_banned("f.md", "the `human` token\n")) == 1


def test_fenced_block_is_not_an_escape_for_the_ban() -> None:
    findings = prose_lint.scan_banned("f.md", "before\n```\nhuman\n```\nafter\n")

    assert [f.line for f in findings] == [3]


# --- audit: discovery, scope, and exclusions over a repo ---


def test_flags_harness_markdown(tmp_path: Path) -> None:
    # Scope is all authored Markdown, harness files included — not md.classify's
    # concept-only set. A CLAUDE.md (harness) carrying the British form is flagged.
    repo = make_repo(tmp_path, {"CLAUDE.md": "Exercise judgement here.\n"})

    findings = prose_lint.audit(repo)

    assert [f.file for f in findings] == ["CLAUDE.md"]


def test_skips_verbatim_reference_doc(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {"docs/references/x.md": "---\ntype: Reference\n---\na judgement\n"},
    )

    assert prose_lint.audit(repo) == []


def test_skips_transient_plan_progress_scratch(tmp_path: Path) -> None:
    # PLAN.md / PROGRESS.md are the ralph-loop scratch pair — md.classify's
    # "excluded" category, out of the authored-content bundle. A British spelling
    # in throwaway scratch must not block every commit.
    repo = make_repo(
        tmp_path,
        {"PLAN.md": "a judgement in scratch\n", "PROGRESS.md": "another judgement\n"},
    )

    assert prose_lint.audit(repo) == []


def test_skips_root_tmp_scratch_tree(tmp_path: Path) -> None:
    # The root tmp/ tree is scratch too — excluded, never scanned.
    repo = make_repo(tmp_path, {"tmp/notes.md": "a judgement here\n"})

    assert prose_lint.audit(repo) == []


def test_flags_non_reference_doc(tmp_path: Path) -> None:
    # Control for the verbatim exclusion: an authored (non-Reference) doc with
    # the same body is flagged.
    repo = make_repo(
        tmp_path,
        {"standards/x.md": "---\ntype: Standard\n---\na judgement\n"},
    )

    findings = prose_lint.audit(repo)

    assert [f.file for f in findings] == ["standards/x.md"]


def test_frontmatter_values_are_not_scanned_as_prose(tmp_path: Path) -> None:
    # Frontmatter is structured YAML, not prose, and a YAML scalar has no
    # backtick escape hatch — so a title/description carrying the British form in
    # a non-Reference doc must not be flagged. Only the body is scanned.
    repo = make_repo(
        tmp_path,
        {
            "standards/x.md": (
                "---\ntype: Standard\ntitle: A judgement of taste\n---\nclean body\n"
            )
        },
    )

    assert prose_lint.audit(repo) == []


def test_body_finding_reports_absolute_line_number(tmp_path: Path) -> None:
    # The scanner runs over the body only, but reported line numbers stay
    # absolute to the file so an editor jumps to the right line.
    repo = make_repo(
        tmp_path,
        {"standards/x.md": "---\ntype: Standard\n---\na judgement\n"},
    )

    findings = prose_lint.audit(repo)

    assert [(f.file, f.line) for f in findings] == [("standards/x.md", 4)]


def test_malformed_frontmatter_exits_two_not_traceback(tmp_path: Path) -> None:
    # A single .md with a malformed frontmatter block — even an untracked draft,
    # since discovery lists --others — must surface as the detector's exit 2, not
    # an uncaught YAML traceback that blocks every commit.
    repo = make_repo(
        tmp_path,
        {"draft.md": "---\ntype: [unterminated\n---\nbody\n"},
    )

    assert prose_lint.main([str(repo)]) == 2


def test_ban_reaches_non_markdown_files(tmp_path: Path) -> None:
    # The ban reads every tracked file, not just Markdown — a code comment or a
    # config value carrying the noun is a finding.
    repo = make_repo(tmp_path, {"src/tool.py": "# reviewed by a human\n"})

    findings = prose_lint.audit(repo)

    assert [(f.file, f.rule) for f in findings] == [
        ("src/tool.py", prose_lint.THE_BANNED_WORD)
    ]


def test_ban_reaches_frontmatter(tmp_path: Path) -> None:
    # The spelling rule scans the body only; the ban has no such carve-out.
    repo = make_repo(
        tmp_path,
        {"docs/x.md": "---\ntype: Standard\ndescription: for the human\n---\nbody\n"},
    )

    findings = prose_lint.audit(repo)

    assert [(f.file, f.line) for f in findings] == [("docs/x.md", 3)]


def test_ban_skips_verbatim_reference_doc(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {"docs/references/spec.md": "---\ntype: Reference\n---\nhuman\n"},
    )

    assert prose_lint.audit(repo) == []


def test_exempt_file_entry_exempts_that_file(tmp_path: Path) -> None:
    # A .prose-lint-exempt entry naming a file exempts it from both rules —
    # spelling and ban alike — while its siblings stay governed.
    repo = make_repo(
        tmp_path,
        {
            ".prose-lint-exempt": "docs/essay.md\n",
            "docs/essay.md": "a judgement about the human condition\n",
            "docs/other.md": "the human next door\n",
        },
    )

    findings = prose_lint.audit(repo)

    assert [f.file for f in findings] == ["docs/other.md"]


@pytest.mark.parametrize("entry", ["data/postings", "data/postings/"])
def test_exempt_directory_entry_exempts_its_subtree(tmp_path: Path, entry: str) -> None:
    # A directory entry — trailing slash or not — covers everything beneath it,
    # but never a sibling whose name merely shares the prefix.
    repo = make_repo(
        tmp_path,
        {
            ".prose-lint-exempt": f"{entry}\n",
            "data/postings/role.txt": "human resources experience required\n",
            "data/postings/deep/role.txt": "human-in-the-loop controls\n",
            "data/postings-notes.md": "notes on the human reviewer\n",
        },
    )

    findings = prose_lint.audit(repo)

    assert [f.file for f in findings] == ["data/postings-notes.md"]


def test_exempt_comments_and_blank_lines_are_ignored(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            ".prose-lint-exempt": "# why: captured external text\n\ndata/x.txt\n",
            "data/x.txt": "the human author\n",
        },
    )

    assert prose_lint.audit(repo) == []


def test_exempt_declaration_itself_is_never_scanned(tmp_path: Path) -> None:
    # An entry may legitimately name a path carrying the banned word, so the
    # declaration file is structurally exempt — listed or not.
    repo = make_repo(
        tmp_path,
        {".prose-lint-exempt": "# human-facing captures\nassets/human-vs-agent.jpg\n"},
    )

    assert prose_lint.audit(repo) == []


# --- the repo vocabulary: .prose-lint-vocabulary ---

VOCABULARY = (
    "guard:\n  say: condition\n  where:\n    - doc-types\n    - standards/doc-type\n"
)


def test_repo_word_is_banned_under_its_directories_only(tmp_path: Path) -> None:
    # The ban holds in every tracked file under a named directory, of any type,
    # and nowhere else: code outside the scope keeps its guard clauses.
    repo = make_repo(
        tmp_path,
        {
            ".prose-lint-vocabulary": VOCABULARY,
            "doc-types/loop/definition.md": "a step's guard\n",
            "standards/doc-type/x.md": "---\ntitle: Guards\n---\nnone\n",
            "src/tool.py": "# an early-return guard\n",
            "doc-types-notes.md": "guard\n",
        },
    )

    findings = prose_lint.audit(repo)

    assert [(f.file, f.line, f.rule) for f in findings] == [
        ("doc-types/loop/definition.md", 1, prose_lint.THE_REPO_VOCABULARY),
        ("standards/doc-type/x.md", 2, prose_lint.THE_REPO_VOCABULARY),
    ]
    assert "`guard` is `condition` under `doc-types/`" in findings[0].message


def test_repo_word_matches_like_the_workspace_word() -> None:
    # Bare or plural, any case, a hyphenated compound; a longer word that
    # contains the sequence is not the word.
    word = prose_lint.Word("guard", "condition", ())

    hits = prose_lint.scan_banned(
        "f.md", "Guards guard-rail\nguarded safeguard\n", (word,)
    )

    assert [(f.line) for f in hits] == [1, 1]


def test_repo_word_with_no_where_covers_the_whole_repo(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            ".prose-lint-vocabulary": "utilise:\n  say: use\n",
            "src/a.py": "# utilise\n",
        },
    )

    findings = prose_lint.audit(repo)

    assert [(f.file, f.rule) for f in findings] == [
        ("src/a.py", prose_lint.THE_REPO_VOCABULARY)
    ]
    assert "in every tracked file" in findings[0].message


def test_workspace_word_still_holds_beside_a_repo_vocabulary(tmp_path: Path) -> None:
    # The layers add: a repo's declaration never narrows the workspace's word.
    repo = make_repo(
        tmp_path,
        {
            ".prose-lint-vocabulary": VOCABULARY,
            "doc-types/a.md": "clean\n",
            "standards/doc-type/a.md": "clean\n",
            "src/a.py": "# a human\n",
        },
    )

    assert [f.rule for f in prose_lint.audit(repo)] == [prose_lint.THE_BANNED_WORD]


def test_vocabulary_declaration_itself_is_never_scanned(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {".prose-lint-vocabulary": "human:\n  say: user\n"})
    (repo / ".prose-lint-vocabulary").write_text("guard:\n  say: condition\n")

    assert prose_lint.audit(repo) == []


@pytest.mark.parametrize(
    "declaration",
    [
        "- guard\n",  # not a mapping
        "guard: condition\n",  # entry is not a mapping
        "guard:\n  where: [doc-types]\n",  # no say
        "guard:\n  say: condition\n  where: doc-types\n",  # where not a list
        "guard:\n  say: condition\n  where: [nowhere]\n",  # not a directory
        "guard:\n  say: condition\n  forms: [guards]\n",  # unknown key
        "human:\n  say: person\n",  # the workspace's word
        "guard: [\n",  # malformed YAML
    ],
)
def test_faulty_vocabulary_exits_two(tmp_path: Path, declaration: str) -> None:
    # Every fault in the declaration is a run failure, never a silent no-op.
    repo = make_repo(
        tmp_path,
        {".prose-lint-vocabulary": declaration, "doc-types/a.md": "clean\n"},
    )

    result = run(repo)

    assert result.returncode == 2, result.stdout + result.stderr
    assert ".prose-lint-vocabulary" in result.stderr


def test_dev_playbook_bans_guard_under_the_doc_type_system() -> None:
    repo = Path(__file__).resolve().parents[2]

    words = {w.word: w for w in prose_lint.vocabulary(repo)}

    assert words["guard"].say == "condition"
    assert words["guard"].where == ("doc-types", "standards/doc-type")
    assert not words["guard"].covers("src/dev_playbook/md.py")


def test_binary_file_is_skipped(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"data/blob.bin": ""})
    (repo / "data/blob.bin").write_bytes(b"human\0human")

    assert prose_lint.audit(repo) == []


def test_symlinked_content_is_not_scanned(tmp_path: Path) -> None:
    # A symlink's content belongs to its target: an out-of-repo target is not
    # ours, and an in-repo target is scanned at its own path.
    target = tmp_path / "outside.md"
    target.write_text("the human partner\n")
    repo = make_repo(tmp_path, {})
    link = repo / "dotfiles/dot-claude/skills/x/SKILL.md"
    link.parent.mkdir(parents=True)
    os.symlink(target, link)

    assert prose_lint.audit(repo) == []


@pytest.mark.parametrize("name", ["the-human", "human-readable"])
def test_ban_reaches_repo_names(name: str) -> None:
    # repo-init consults the ban pattern before scaffolding, so a name that
    # would put the noun in a fresh CLAUDE.md H1 is refused up front.
    spec = RepoSpec(name=name, description="A demo repo", python=False)

    with pytest.raises(RepoInitError, match="prose-lint"):
        render_tree(spec, "0" * 40)


# --- agent-facing voice: the first-person ban over harness-loaded files ---


def skill(body: str, description: str = "Use when demoing.") -> str:
    return f"---\nname: demo\ndescription: {description}\n---\n\n# Demo\n\n{body}"


def voice_findings(repo: Path) -> list[prose_lint.Finding]:
    return [f for f in prose_lint.audit(repo) if f.rule == prose_lint.NO_FIRST_PERSON]


def test_claude_md_first_person_fails(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"CLAUDE.md": "# Repo\n\nI want my tests to pass.\n"})

    faults = {f.message for f in voice_findings(repo)}

    assert "never speak in first person: 'I'" in faults
    assert "never speak in first person: 'my'" in faults


def test_voice_guards_io_abbreviation(tmp_path: Path) -> None:
    # "I/O" is an abbreviation, not a first-person violation.
    repo = make_repo(tmp_path, {"CLAUDE.md": "# Repo\n\nProduce well-formed I/O.\n"})

    assert voice_findings(repo) == []


def test_nested_claude_md_is_checked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"sub/CLAUDE.md": "I run the tool from here.\n"})

    assert [f.file for f in voice_findings(repo)] == ["sub/CLAUDE.md"]


def test_object_pronoun_fails(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path, {".claude/rules/commands.md": "# Commands\n\nHand it to me.\n"}
    )

    assert [f.message for f in voice_findings(repo)] == [
        "never speak in first person: 'me'"
    ]


@pytest.mark.parametrize(
    "relpath",
    [
        ".claude/skills/demo/SKILL.md",
        "dotfiles/dot-claude/skills/demo/SKILL.md",
        ".claude/agents/demo.md",
        "dotfiles/dot-claude/agents/demo.md",
        ".claude/rules/commands.md",
        "dotfiles/dot-claude/rules/commands.md",
    ],
)
def test_every_runbook_and_rule_root_is_checked(tmp_path: Path, relpath: str) -> None:
    # One roster decides membership for the six roots, so a consumer's .claude/
    # tree and dev-playbook's Stow source answer alike.
    repo = make_repo(tmp_path, {relpath: skill("I check the work.\n")})

    assert [f.file for f in voice_findings(repo)] == [relpath]


def test_frontmatter_is_in_scope(tmp_path: Path) -> None:
    # The description is prose the agent reads to choose the runbook, so it
    # answers to the same voice as the body.
    repo = make_repo(
        tmp_path,
        {".claude/skills/demo/SKILL.md": skill("Run it.\n", "Use when I run my demo.")},
    )

    assert {f.line for f in voice_findings(repo)} == {3}


def test_code_is_not_voice(tmp_path: Path) -> None:
    # A backticked token and a fenced example are code, not the document talking.
    repo = make_repo(
        tmp_path,
        {
            ".claude/skills/demo/SKILL.md": skill(
                "Ask before running `I am ready`.\n\n"
                "```text\nI told my agent to run it.\n```\n"
            )
        },
    )

    assert voice_findings(repo) == []


def test_quoted_speech_is_exempt(tmp_path: Path) -> None:
    # A quoted utterance is the user's voice, not the document's — the trigger
    # phrasing a skill is written to recognize.
    repo = make_repo(
        tmp_path,
        {
            ".claude/skills/demo/SKILL.md": skill(
                'Use when the user says "Show me my options before I commit."\n'
            )
        },
    )

    assert voice_findings(repo) == []


def test_prose_outside_the_quotes_still_fails(tmp_path: Path) -> None:
    # The exemption ends at the closing quote; the sentence around it is the
    # document speaking.
    repo = make_repo(
        tmp_path,
        {
            ".claude/skills/demo/SKILL.md": skill(
                'When the user says "ship it", I commit my work.\n'
            )
        },
    )

    assert len(voice_findings(repo)) == 2


def test_declarative_document_is_out_of_scope(tmp_path: Path) -> None:
    # The ban reaches agent instructions, not every authored doc: a standard
    # quoting first-person prose is describing, not instructing.
    repo = make_repo(tmp_path, {"standards/prose.md": "# Prose\n\nI, me, my.\n"})

    assert voice_findings(repo) == []


def test_exempt_declaration_covers_the_voice_rule(tmp_path: Path) -> None:
    # One exemption mechanism for every rule this detector runs, as the standard
    # states — a path listed here is exempt from these conventions, not from two
    # of the three.
    files = {
        ".claude/skills/demo/SKILL.md": skill("I check my own work.\n"),
        ".prose-lint-exempt": "# quoted upstream text\n.claude/skills/demo\n",
    }

    assert voice_findings(make_repo(tmp_path, files)) == []


# --- CLI: --list-rules, exit codes, and finding format ---


def run(repo: Path) -> subprocess.CompletedProcess:
    """Run scripts/prose-lint against repo and capture its output."""
    return subprocess.run(
        ["python3", str(SCRIPT), str(repo)],
        capture_output=True,
        text=True,
    )


def test_list_rules_prints_the_rule_id(tmp_path: Path) -> None:
    result = subprocess.run(
        ["python3", str(SCRIPT), "--list-rules"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.split() == [
        "prose.no-first-person",
        "prose.spelling",
        "prose.the-banned-word",
        "prose.the-repo-vocabulary",
    ]


def test_clean_repo_exits_zero(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"doc.md": "a sound judgment\n"})

    result = run(repo)

    assert result.returncode == 0, result.stdout + result.stderr


def test_finding_line_is_gnu_format(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"doc.md": "a judgement call\n"})

    result = run(repo)

    assert result.returncode == 1
    assert "doc.md:1: prose.spelling " in result.stdout


def test_dev_playbook_self_scan_is_clean() -> None:
    repo = Path(__file__).resolve().parents[2]

    result = run(repo)

    assert result.returncode == 0, result.stdout + result.stderr
