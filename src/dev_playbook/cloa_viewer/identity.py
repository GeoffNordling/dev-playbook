"""Turning a markdown link target into an identity, the way every kind must.

An identity is a repo-relative path, and it is how two panels name the same
thing without a lookup table. The tree
resolves the targets an ``index.md`` lists and the file panel resolves the
targets a document links to, so the rule that turns ``/docs/beta.md`` or
``../beta.md`` into ``docs/beta.md`` is written once, here, for both.

A Citation, ``~/workspace/<repo>/<path>``
([Cross-References](/standards/knowledge-organization/cross-references.md#workspace-path-for-a-stable-location)),
is the third shape. A Citation of the checkout's own repo is a root-absolute
link written the long way and resolves like one; a Citation of another repo
names nothing in this checkout and has no identity here.
"""

import posixpath

EXTERNAL_SCHEMES = ("http://", "https://", "mailto:")
WORKSPACE_PREFIX = "~/workspace/"


def is_external(target: str) -> bool:
    """True when a link target leaves the checkout and names no file in it."""
    return target.startswith(EXTERNAL_SCHEMES)


def citation_repo(target: str) -> str | None:
    """The repo a Citation names, or ``None`` when the target is not one.

    The repo is the segment after ``~/workspace/``: the on-disk name of a
    workspace checkout, which is what ``gitrepo.canonical_repo_name`` answers
    for the checkout being read.
    """
    if not target.startswith(WORKSPACE_PREFIX):
        return None
    return target[len(WORKSPACE_PREFIX) :].split("/", 1)[0] or None


def resolve_target(source: str, target: str, repo: str) -> str:
    """The identity ``target`` names, read from the file at identity ``source``.

    A leading ``/`` resolves against the checkout root, anything else against
    the source file's own directory, and a ``#fragment`` is dropped: the
    identity names the file, and the heading slug is the caller's business. A
    Citation of ``repo``, the checkout's own canonical repo name, drops the
    ``~/workspace/<repo>`` prefix and resolves against the root like a ``/``
    link.

    Raises ``ValueError`` for a Citation of another repo. A generator reads one
    checkout, so there is no file to name; an index that lists another repo's
    file is a defect, and the refresh record has to carry it rather than the
    tree inventing a path.
    """
    citation = citation_repo(target)
    if citation is not None and citation != repo:
        raise ValueError(
            f"{target}: a citation of another repo has no identity in this checkout"
        )
    path = target.split("#", 1)[0]
    if citation is not None:
        path = path[len(WORKSPACE_PREFIX) + len(repo) :]
    if path.startswith("/"):
        return posixpath.normpath(path.lstrip("/"))
    return posixpath.normpath(posixpath.join(posixpath.dirname(source), path))
