"""Where a check reads data out of a Standard: the path and heading, named once.

Some rules consume data a Standard's body holds, such as the registry table
of document types or the canonical files a repo copies. The path and the
heading are constants here, and the test beside this module pins each one
to its document: the file is tracked and the heading is present. A check
reads the section through the model, ``repo.markdown[path].section(slug)``,
and never scans for the heading itself.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Section:
    """One heading of one Standard, by path and heading slug."""

    path: str
    heading: str


# The global table of document types: every registered `type` and what it is.
TYPE_REGISTRY = Section(
    "standards/knowledge-organization/document-types.md",
    "type-names-a-registered-type",
)

# The directory of canonical files a repo copies as they are.
CANONICAL_DIR = "standards/build/canonical"


def sections() -> dict[str, Section]:
    """Every :class:`Section` constant in this module, by name."""
    return {
        name: value for name, value in globals().items() if isinstance(value, Section)
    }
