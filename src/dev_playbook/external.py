"""Single source of truth for content the workspace does not author.

A document whose body is a verbatim copy of an upstream external one is not
ours to hold to the authored-content standards. This module is where "not ours
to enforce" is decided once, so the detectors share one definition instead of
each hardcoding its own drifting skip list.

- :func:`is_verbatim_doc` -- a document whose frontmatter marks it a verbatim
  upstream mirror (OKF ``type: Reference``). Keying on the OKF type means the
  classification follows the document wherever it lives, not a path.

See standards/standard/format.md (Detectors -- verbatim content) for the norm
this module anchors.
"""

# The OKF document type meaning "verbatim mirror of an external document".
VERBATIM_DOC_TYPE = "Reference"


def is_verbatim_doc(frontmatter: dict | None) -> bool:
    """Whether a document's frontmatter marks it a verbatim upstream mirror."""
    if not frontmatter:
        return False
    return frontmatter.get("type") == VERBATIM_DOC_TYPE
