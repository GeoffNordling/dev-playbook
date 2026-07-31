"""The agent-facing voice vocabulary: words instruction text may not speak in.

Agent-facing instruction text names the human actor "user" and never speaks in
first person. Four tokens: the actor-noun "human" (but not the
"human-readable" compound) and the first-person "I" (but not the "I/O"
abbreviation), "me", and "my". Only "human" and "I" carry an exemption --
nothing in the workspace's vocabulary spells "me" or "my" as anything but the
first person, so neither gets a speculative guard. Each pattern carries its own
message: an actor-noun hit and a first-person hit are two different faults
(conventions.md -- Terminology: human vs user).

Two actors read this vocabulary, so it lives here rather than in either of
them: ``scripts/repo-lint`` enforces it over every CLAUDE.md, skill, and rule
body, and ``dev_playbook.repo_init`` refuses a repo name that carries one of
these words, since the name becomes the H1 of the CLAUDE.md a fresh scaffold
writes. Masking prose before matching -- inline code, fenced blocks, quoted
speech -- is the enforcing detector's job, not this module's.
"""

import re

VOICE_PATTERNS = (
    (
        re.compile(r"\bhuman\b(?!-)", re.IGNORECASE),
        "name the human 'user', not 'human'",
    ),
    (re.compile(r"\bI\b(?!/O)"), "never speak in first person: 'I'"),
    (re.compile(r"\b[Mm]e\b"), "never speak in first person: 'me'"),
    (re.compile(r"\b[Mm]y\b"), "never speak in first person: 'my'"),
)


def first_fault(text: str) -> str | None:
    """The fault ``text`` trips, worded as the detector words it, else ``None``.

    Matches the raw string: callers passing prose mask it first.
    """
    for pattern, fault in VOICE_PATTERNS:
        if pattern.search(text):
            return fault
    return None
