"""The agent-facing voice vocabulary: words instruction text may not speak in.

Agent-facing instruction text is addressed *to* the executing agent, so it
never speaks in the first person. Three tokens: "I" (but not the "I/O"
abbreviation), "me", and "my". Only "I" carries an exemption -- nothing in the
workspace's vocabulary spells "me" or "my" as anything but the first person, so
neither gets a speculative guard. Each pattern carries its own message. (The
other voice rule -- one word for the person, the ``user`` -- is repo-wide
rather than agent-facing-specific, and lives in ``dev_playbook.prose_lint``;
conventions.md -- Terminology: the person is the user.)

Two actors read this vocabulary, so it lives here rather than in either of
them: ``dev_playbook.prose_lint`` enforces it over every harness-loaded agent
instruction file (``md.is_agent_instruction`` decides which), and
``dev_playbook.repo_init`` refuses a repo name that carries one of these words,
since the name becomes the H1 of the CLAUDE.md a fresh scaffold writes. Masking
prose before matching -- inline code, fenced blocks, quoted speech -- is the
enforcing detector's job, not this module's.
"""

import re

VOICE_PATTERNS = (
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
