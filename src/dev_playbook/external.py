"""Single source of truth for content the workspace does not author.

A document whose body is a verbatim copy of an upstream external one is not
ours to hold to the authored-content standards. This module is where "not ours
to hold" is decided once, so the checks share one definition instead of
each hardcoding its own drifting skip list.

- :func:`is_verbatim_doc` -- a document whose frontmatter marks it a verbatim
  upstream mirror (OKF ``type: Mirror``). Keying on the OKF type means the
  classification follows the document wherever it lives, not a path.

The exclusion is stated in the population of standards/prose/conventions.md;
this module is where every check reads it.
"""

# The OKF document type meaning "verbatim mirror of an external document".
VERBATIM_DOC_TYPE = "Mirror"


def is_verbatim_doc(frontmatter: dict | None) -> bool:
    """Whether a document's frontmatter marks it a verbatim upstream mirror."""
    if not frontmatter:
        return False
    return frontmatter.get("type") == VERBATIM_DOC_TYPE
