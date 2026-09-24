"""The one exception the command-line tools raise when a run cannot proceed.

A finding is a fact about a repo; a ``ToolError`` is the tool saying it could
not establish the facts at all — a missing program, an unreadable remote, a
precondition unmet. Every tool's ``main`` catches it once, prints it to
stderr, and exits 2, so "could not check" is never reported as "found
something".
"""


class ToolError(Exception):
    """The tool could not run at all."""
