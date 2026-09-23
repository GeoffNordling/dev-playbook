"""Unit tests for the prose family's checks.

The banned word is never spelled here: every fixture builds it from
``WORKSPACE_WORD``, so this file needs no entry in the exempt file.
"""

from pathlib import Path

from dev_playbook import sources
from dev_playbook.checks.prose import (
    WORKSPACE_WORD,
    judgment_spelling,
    no_banned_word,
    no_first_person,
    no_word_the_repo_bans,
    vocabulary_well_formed,
)
from dev_playbook.model import Repo

WORD = WORKSPACE_WORD


def test_judgment_not_judgement() -> None:
    repo = Repo.from_files(
        Path("/r"),
        {
            "a.md": b"---\ntitle: judgement\n---\n\nA judgment call.\n",
            "b.md": b"Judgement here, `judgement` there.\n\n```\njudgements\n```\n",
            "c.md": b"---\ntype: Mirror\n---\n\na judgement\n",
            "d.txt": b"a judgement\n",
        },
    )
    assert [(f.path, f.line) for f in judgment_spelling(repo)] == [("b.md", 1)]


def test_no_first_person() -> None:
    skill = "---\ndescription: Use when my build fails.\n---\n\n# Demo\n\n{}\n"
    repo = Repo.from_files(
        Path("/r"),
        {
            "skills/a/SKILL.md": skill.format("Run the I/O step.").encode(),
            "skills/b/SKILL.md": skill.format('Say "fix me" or `I`.').encode(),
            "rules/c.md": b"# C\n\nI think so.\n\n```\nmy block\n```\n",
            "docs/d.md": b"# D\n\nI think so.\n",
        },
    )
    assert [(f.path, f.line) for f in no_first_person(repo)] == [
        ("rules/c.md", 3),
        ("skills/a/SKILL.md", 2),
        ("skills/b/SKILL.md", 2),
    ]


def test_no_banned_word() -> None:
    repo = Repo.from_files(
        Path("/r"),
        {
            "a.py": f"x = '{WORD}s'\n# {WORD}-readable\n".encode(),
            "b.md": f"`{WORD.upper()}`\n\nsuper{WORD} and {WORD}e\n".encode(),
            "c.md": f"---\ntype: Mirror\n---\n\n{WORD}\n".encode(),
            "skip/d.txt": WORD.encode(),
            "e.bin": f"\0{WORD}".encode(),
            ".prose-lint-exempt": b"# why\nskip/\n",
        },
    )
    assert [(f.path, f.line) for f in no_banned_word(repo)] == [
        ("a.py", 1),
        ("a.py", 2),
        ("b.md", 1),
    ]


def test_the_standard_names_the_banned_word(dev_playbook_repo: Repo) -> None:
    section = dev_playbook_repo.markdown[sources.BANNED_WORD.path].section(
        sources.BANNED_WORD.heading
    )
    assert any(f"`{WORD}`" in text for _, text in section)


def test_no_word_the_repo_bans() -> None:
    repo = Repo.from_files(
        Path("/r"),
        {
            ".prose-lint-vocabulary": (
                b"guard:\n  say: condition\n  where: [doc-types]\nfoo:\n  say: bar\n"
            ),
            "doc-types/a.md": b"a Guard and two guards\n",
            "src/b.py": b"guard = 1\n# foo\n",
        },
    )
    assert [(f.path, f.line) for f in no_word_the_repo_bans(repo)] == [
        ("doc-types/a.md", 1),
        ("doc-types/a.md", 1),
        ("src/b.py", 2),
    ]


def test_the_vocabulary_file_is_well_formed() -> None:
    good = Repo.from_files(
        Path("/r"),
        {
            ".prose-lint-vocabulary": b"guard:\n  say: condition\n  where: [d]\n",
            "d/a.md": b"",
        },
    )
    bad = Repo.from_files(
        Path("/r"),
        {
            ".prose-lint-vocabulary": (
                f"{WORD}:\n  say: user\n".encode()
                + b"a:\n  where: [d]\n"
                + b"b:\n  say: c\n  also: 1\n"
                + b"e:\n  say: f\n  where: [nowhere]\n"
            ),
            "d/a.md": b"",
        },
    )
    assert list(vocabulary_well_formed(good)) == []
    assert [f.message for f in vocabulary_well_formed(bad)] == [
        f"`{WORD}` is the workspace's banned word already",
        "`a` has no `say` string",
        "`b` has keys other than `say` and `where`: ['also']",
        "`e`'s `where` names `nowhere`, not a directory of the repo",
    ]
