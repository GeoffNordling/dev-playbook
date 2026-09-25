"""Where a check reads data out of a document: the path and heading, named once.

Some rules consume data a document holds, such as the OKF Type Registry's table
of OKF types or the canonical files a repo copies. The path and the
heading are constants here, and the test beside this module pins each one
to its document: the file is tracked and the heading is present. A check
reads the section through the model, ``repo.markdown[path].section(slug)``,
and never scans for the heading itself.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Section:
    """One heading of one document, by path and heading slug."""

    path: str
    heading: str


# The global table of OKF types: every registered `type` and what it is.
OKF_TYPE_REGISTRY = Section("registries/okf-types.md", "okf-types")

# The table joining each built doc-type to the OKF type or harness members
# its instances are.
DOC_TYPE_REGISTRY = Section("registries/doc-types.md", "doc-types")

# The table of the files the Claude Code harness consumes, one row per member.
HARNESS_FILE_REGISTRY = Section("registries/harness-files.md", "members")

# Every type name in the OKF_TYPE_REGISTRY table. A consumer runs the installed
# package, not dev-playbook's tree, so the names ship here; the test beside
# this module pins the set, and the table's shape, to the table.
REGISTERED_OKF_TYPES = frozenset(
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
        "Registry",
        "Standard",
        "Survey",
        "Vocabulary",
        "Workstream",
    }
)

# The menu a Workstream's head file picks its headings from.
WORKSTREAM_HEADING_REGISTRY = Section("registries/workstream-headings.md", "headings")

# Every heading in the WORKSTREAM_HEADING_REGISTRY table, shipped as REGISTERED_OKF_TYPES is;
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
