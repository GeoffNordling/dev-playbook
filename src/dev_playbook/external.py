"""Single source of truth for content the workspace does not author.

Some content in a repo is not ours to hold to the authored-content standards: a
vendored skill bundle we mirror in but do not maintain file-by-file, or a
document whose body is a verbatim copy of an upstream external one. This module
is where "not ours to enforce" is decided once, so the detectors share one
definition instead of each hardcoding its own drifting skip list.

Two composable predicates -- deliberately not one monolithic skip-list, because
each detector needs a different subset:

- :func:`is_externally_managed` -- a repo-relative path inside an
  externally-managed vendored root. The only such root today is
  ``dotfiles/.agents``.
- :func:`is_verbatim_doc` -- a document whose frontmatter marks it a verbatim
  upstream mirror (OKF ``type: Reference``). Keying on the OKF type means the
  classification follows the document wherever it lives, not a path.

See standards/standard/format.md (Detectors -- externally-managed and verbatim
content) for the norm this module anchors.
"""

from pathlib import PurePosixPath

# Externally-managed vendored roots: bundles the repo mirrors in but does not
# maintain file-by-file, so authored-content rules do not reach them. Adding a
# root here reaches every detector that consults is_externally_managed.
EXTERNALLY_MANAGED_ROOTS: tuple[PurePosixPath, ...] = (
    PurePosixPath("dotfiles/.agents"),
)

# The OKF document type meaning "verbatim mirror of an external document".
VERBATIM_DOC_TYPE = "Reference"


def is_externally_managed(relpath: str) -> bool:
    """Whether a repo-relative path lies within an externally-managed root."""
    path = PurePosixPath(relpath)
    return any(
        path == root or root in path.parents for root in EXTERNALLY_MANAGED_ROOTS
    )


def is_verbatim_doc(frontmatter: dict | None) -> bool:
    """Whether a document's frontmatter marks it a verbatim upstream mirror."""
    if not frontmatter:
        return False
    return frontmatter.get("type") == VERBATIM_DOC_TYPE
