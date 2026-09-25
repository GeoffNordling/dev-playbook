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

# Every type name in the TYPE_REGISTRY table. A consumer runs the installed
# package, not dev-playbook's tree, so the names ship here; the test beside
# this module pins the set, and the table's shape, to the table.
REGISTERED_TYPES = frozenset(
    {
        "Candidate-List",
        "Decision-Record",
        "General-Sheet",
        "Guide",
        "Log",
        "Loop",
        "Mirror",
        "README",
        "Recipe-Description",
        "Standard",
        "Survey",
        "Vocabulary",
        "Workstream",
    }
)

# The menu a Workstream's head file picks its headings from.
WORKSTREAM_MENU = Section(
    "standards/doc-type/workstream-conventions.md",
    "headings-from-the-menu",
)

# Every heading in the WORKSTREAM_MENU table, shipped as REGISTERED_TYPES is;
# the test beside this module pins the set to the table.
WORKSTREAM_HEADINGS = frozenset(
    {
        "Goal",
        "Done when",
        "Principles",
        "Constraints",
        "Terms",
        "Settled",
        "Open",
        "Planned",
        "Completed",
        "Stints",
        "Unfiled",
        "Acronyms",
    }
)

# The table whose Ruling cells link each doc-type's directory.
REGISTRY_RULINGS = Section("doc-types/doc-type-system.md", "registry-rulings")

# The rule that names the workspace's banned word; a test asserts the word
# there is the one the prose checks hold.
BANNED_WORD = Section("standards/prose/conventions.md", "no-banned-word")

# The directory of canonical files a repo copies as they are.
CANONICAL_DIR = "standards/build/canonical"

# The copy of CANONICAL_DIR the package ships, so an installed package carries
# the sources; the test beside this module pins it byte-identical to the tree.
SHIPPED_CANONICAL_DIR = "src/dev_playbook/canonical"

# Every file directly under CANONICAL_DIR, each the source a build check
# compares a repo's copy against; the test beside this module pins the set.
CANONICAL_FILES = frozenset(
    {
        ".gitignore",
        ".pre-commit-config.yaml",
        ".python-version",
        "Makefile.base",
        "Makefile.python",
        "ci.yml",
        "pyproject.toml",
    }
)


# Every directory directly under standards/ that dev-playbook publishes. A
# consumer runs the installed package, not dev-playbook's tree, so the names
# ship here; the test beside this module pins the set.
STANDARD_DIRECTORIES = frozenset(
    {
        "billing",
        "build",
        "decisions",
        "distribution",
        "doc-type",
        "harness",
        "knowledge-organization",
        "prose",
        "python",
        "shell",
        "standard",
        "testing",
        "tracking",
    }
)


def sections() -> dict[str, Section]:
    """Every :class:`Section` constant in this module, by name."""
    return {
        name: value for name, value in globals().items() if isinstance(value, Section)
    }
