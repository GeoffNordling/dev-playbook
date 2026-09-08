"""Turning a markdown link target into an identity, the way every kind must.

An identity is a repo-relative path, and it is how two panels name the same
thing without a lookup table
([Contract](/worktree-cloa-viewer-tool-working-docs/contract.md)). The tree
resolves the targets an ``index.md`` lists and the file panel resolves the
targets a document links to, so the rule that turns ``/docs/beta.md`` or
``../beta.md`` into ``docs/beta.md`` is written once, here, for both.
"""

import posixpath

EXTERNAL_SCHEMES = ("http://", "https://", "mailto:")


def is_external(target: str) -> bool:
    """True when a link target leaves the checkout and names no file in it."""
    return target.startswith(EXTERNAL_SCHEMES)


def resolve_target(source: str, target: str) -> str:
    """The identity ``target`` names, read from the file at identity ``source``.

    A leading ``/`` resolves against the checkout root, anything else against
    the source file's own directory, and a ``#fragment`` is dropped: the
    identity names the file, and the heading slug is the caller's business.
    """
    path = target.split("#", 1)[0]
    if path.startswith("/"):
        return posixpath.normpath(path.lstrip("/"))
    return posixpath.normpath(posixpath.join(posixpath.dirname(source), path))
