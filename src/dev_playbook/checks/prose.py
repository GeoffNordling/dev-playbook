"""The prose family: the rules of ``standards/prose/``.

Five rules are decided by functions over the model: the American spelling
of judgment, the first person in a harness-loaded agent instruction, the
workspace's banned word, the words the repo's ``.prose-lint-vocabulary``
bans, and the form of that file. Every rule skips the population's
exceptions: a ``type: Mirror`` document and a path the repo lists in its
``.prose-lint-exempt``. The two declaration files are skipped as well,
since each must name what it bans.

This module spells the banned word, so the repo's exempt file lists it.
"""

import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass

import yaml

from dev_playbook import md, voice
from dev_playbook.check_registry import Finding, check
from dev_playbook.external import is_verbatim_doc
from dev_playbook.model import Repo

# The workspace's banned word, and the word that replaces it. The Standard
# names the same word under its rule; a test asserts the two agree.
WORKSPACE_WORD = "human"
WORKSPACE_SAY = "user"

VOCABULARY_FILE = ".prose-lint-vocabulary"
EXEMPT_FILE = ".prose-lint-exempt"
VOCABULARY_KEYS = frozenset({"say", "where"})

# The British form, singular or plural, as a whole word in any case.
JUDGEMENT = re.compile(r"\bjudgements?\b", re.IGNORECASE)
JUDGMENT_MESSAGE = "British `judgement`/`judgements`; the house spelling is `judgment`"

# A double-quoted span on one line is another speaker's voice.
QUOTED_SPEECH = re.compile(r'"[^"\n]*"')


@dataclass(frozen=True)
class Word:
    """One word the repo bans: the word, its replacement, and the directories it covers.

    ``where`` empty covers every tracked file.
    """

    word: str
    say: str
    where: tuple[str, ...]

    def covers(self, path: str) -> bool:
        """Whether the ban holds at a repo-relative path."""
        return not self.where or any(path.startswith(d + "/") for d in self.where)


def word_pattern(word: str) -> re.Pattern[str]:
    """The word bare or plural, in any case, as a whole word.

    A hyphen or a space ends a word, so the word in a compound is found; a
    longer word that only contains it is not the word.
    """
    return re.compile(rf"\b{re.escape(word)}s?\b", re.IGNORECASE)


def _exempt(repo: Repo) -> tuple[str, ...]:
    """The paths the repo's ``.prose-lint-exempt`` lists, trailing slash dropped."""
    if EXEMPT_FILE not in repo.contents:
        return ()
    entries = []
    for line in repo.text(EXEMPT_FILE).splitlines():
        entry = line.strip()
        if entry and not entry.startswith("#"):
            entries.append(entry.rstrip("/"))
    return tuple(entries)


def _governed(repo: Repo) -> Iterator[str]:
    """Every tracked path the family's rules read: the population's exceptions left out."""
    exempt = _exempt(repo)
    for path in repo.files:
        if path in (EXEMPT_FILE, VOCABULARY_FILE):
            continue
        if any(path == entry or path.startswith(entry + "/") for entry in exempt):
            continue
        if path in repo.markdown and is_verbatim_doc(repo.markdown[path].frontmatter):
            continue
        yield path


def _text(repo: Repo, path: str) -> str | None:
    """A file's text, or None for a binary file, one holding a zero byte."""
    data = repo.contents[path]
    if b"\0" in data:
        return None
    return data.decode("utf-8", errors="replace")


def _word_findings(
    repo: Repo, pattern: re.Pattern[str], paths: Iterable[str], message: str
) -> Iterator[Finding]:
    """One finding per occurrence of ``pattern`` in each of ``paths``, whole file."""
    for path in paths:
        text = _text(repo, path)
        if text is None:
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            for _ in pattern.finditer(line):
                yield Finding(path, number, message)


@check("prose.judgment-not-judgement")
def judgment_spelling(repo: Repo) -> Iterator[Finding]:
    """A document's body, outside code spans and fences, never spells ``judgement``."""
    for path in _governed(repo):
        if path not in repo.markdown:
            continue
        for number, line in repo.markdown[path].content:
            prose = md.INLINE_CODE_PATTERN.sub("", line)
            for _ in JUDGEMENT.finditer(prose):
                yield Finding(path, number, JUDGMENT_MESSAGE)


@check("prose.no-first-person")
def no_first_person(repo: Repo) -> Iterator[Finding]:
    """A harness-loaded agent instruction does not say ``I``, ``me``, or ``my``."""
    for path in _governed(repo):
        if path not in repo.markdown or not md.is_agent_instruction(path):
            continue
        for number, line in md.lines_outside_fences(repo.markdown[path].text):
            prose = QUOTED_SPEECH.sub("", md.INLINE_CODE_PATTERN.sub("", line))
            for pattern, fault in voice.VOICE_PATTERNS:
                if pattern.search(prose):
                    yield Finding(path, number, fault)


@check("prose.no-banned-word")
def no_banned_word(repo: Repo) -> Iterator[Finding]:
    """No tracked file contains the workspace's banned word, bare or plural, in any case."""
    message = (
        f"the person is the `{WORKSPACE_SAY}`; the word `{WORKSPACE_WORD}` "
        "appears in no tracked file"
    )
    yield from _word_findings(
        repo, word_pattern(WORKSPACE_WORD), _governed(repo), message
    )


def _load_vocabulary(repo: Repo) -> tuple[object, str | None]:
    """The parsed ``.prose-lint-vocabulary``, or the YAML error that stopped it."""
    try:
        return yaml.safe_load(repo.text(VOCABULARY_FILE)), None
    except yaml.YAMLError as err:
        return None, f"malformed YAML: {err}"


def _entry_faults(repo: Repo, word: object, entry: object) -> Iterator[str]:
    """Each way one vocabulary entry fails the file's form."""
    if not isinstance(word, str) or not word:
        yield f"{word!r} is not a word"
        return
    if word.lower() == WORKSPACE_WORD:
        yield f"`{word}` is the workspace's banned word already"
    if not isinstance(entry, dict) or not isinstance(entry.get("say"), str):
        yield f"`{word}` has no `say` string"
        return
    unknown = sorted(set(entry) - VOCABULARY_KEYS)
    if unknown:
        yield f"`{word}` has keys other than `say` and `where`: {unknown}"
    where = entry.get("where", [])
    if not isinstance(where, list) or not all(isinstance(d, str) and d for d in where):
        yield f"`{word}`'s `where` is not a list of directories"
        return
    for directory in where:
        prefix = directory.rstrip("/") + "/"
        if not any(path.startswith(prefix) for path in repo.files):
            yield f"`{word}`'s `where` names `{directory}`, not a directory of the repo"


@check("prose.the-vocabulary-file-is-well-formed")
def vocabulary_well_formed(repo: Repo) -> Iterator[Finding]:
    """The repo's ``.prose-lint-vocabulary`` maps each new word to ``say`` and an optional ``where``."""
    if VOCABULARY_FILE not in repo.contents:
        return
    loaded, error = _load_vocabulary(repo)
    if error is not None:
        yield Finding(VOCABULARY_FILE, None, error)
        return
    if loaded is None:
        return
    if not isinstance(loaded, dict):
        yield Finding(VOCABULARY_FILE, None, "not a mapping of word to entry")
        return
    for word, entry in loaded.items():
        for fault in _entry_faults(repo, word, entry):
            yield Finding(VOCABULARY_FILE, None, fault)


def repo_words(repo: Repo) -> tuple[Word, ...]:
    """The well-formed entries of the repo's ``.prose-lint-vocabulary``.

    A malformed file or entry bans nothing here: the well-formed rule
    reports it, one fault, one finding.
    """
    if VOCABULARY_FILE not in repo.contents:
        return ()
    loaded, error = _load_vocabulary(repo)
    if error is not None or not isinstance(loaded, dict):
        return ()
    words = []
    for word, entry in loaded.items():
        if not isinstance(entry, dict) or any(_entry_faults(repo, word, entry)):
            continue
        where = tuple(d.rstrip("/") for d in entry.get("where", []))
        words.append(Word(word, entry["say"], where))
    return tuple(words)


@check("prose.no-word-the-repo-bans")
def no_word_the_repo_bans(repo: Repo) -> Iterator[Finding]:
    """No tracked file a vocabulary entry covers contains that entry's word."""
    governed = list(_governed(repo))
    for word in repo_words(repo):
        scope = (
            "in every tracked file"
            if not word.where
            else "under " + ", ".join(f"`{d}/`" for d in word.where)
        )
        message = f"the word `{word.word}` is `{word.say}` {scope} ({VOCABULARY_FILE})"
        covered = [path for path in governed if word.covers(path)]
        yield from _word_findings(repo, word_pattern(word.word), covered, message)
