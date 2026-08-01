"""Which repo, which issue, and which skill each stored row belongs to.

The interval table says when Claude Code was working; these columns say what it
was working on. Every one of them attributes a **row**, never a session: `cwd`
moves mid-session, one session reads one issue while writing another, and a
session runs many skills ([Measurement Prototype](/docs/measurement-prototype.md)).

Three attributions of three different strengths:

- **Repo** — definitive. Every row carries a `cwd`, and the first path segment
  under the workspace names its repo. A worktree sits at
  `<repo>/.claude/worktrees/<name>`, so it folds into the repo it belongs to
  with no rule of its own.
- **Issue** — approximate by construction. It is recovered by reading the shell
  text of `gh` commands, stored byte-verbatim because Bash is the one tool
  captured whole. A session that worked an issue without running `gh` against it
  leaves no trace, and a `--body` quoting a `gh issue view` line leaves the trace
  of a contact that never happened.
- **Skill** — two paths, one of them forward-only. A human's `/skill` arrives as
  the `command_name` its expansion carried, which
  [`clean.collapse_expansions`](clean.py) folds onto the submit; an agent's
  arrives in a `Skill` tool row's kept input, which capture only recently began
  keeping.

**The read and write issue signals stay in separate columns.** One orchestrator
session in the store views 25 issues; it was not working 25 issues.
`gh issue edit`, `close` and `comment` are evidence of work, `gh issue view` is
evidence of contact, and one column averaging them would mislead about both.

An issue reference is `<repo>#<number>` rather than a bare number, because issue
numbers collide across repos and a timeline lane keyed on `272` would merge two
repos' work into one. The repo is the invocation's own `--repo` where it carries
one and the row's own repo otherwise, with the owner dropped from both so that
the two forms name one issue. Two owners of same-named repos would collide; this
machine has none.

Nothing here reads the store, and nothing here mutates the caller's frame.
"""

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

# Where this machine keeps its checkouts. Injected rather than assumed at every
# call site so the rule can be exercised against a path that is not this
# machine's ([Machines](/docs/machines.md)).
WORKSPACE = Path("~/workspace")

POST_TOOL_USE = "PostToolUse"
BASH_TOOL = "Bash"
SKILL_TOOL = "Skill"

# The kept `tool_input` key naming the skill an agent ran.
SKILL_KEY = "skill"

# The field an expansion carries and its submit does not, folded onto the submit
# by the cleaning: the name the human typed after the slash.
COMMAND_NAME = "command_name"

# `gh issue create` and `gh issue list` are deliberately absent: neither names a
# number on the command line — create's is in the response, which is stored for
# Bash but is prose — so neither can attribute a row.
WRITE_VERBS = ("edit", "close", "comment")
READ_VERBS = ("view",)

ATTRIBUTION_COLUMNS = ("repo", "issue_writes", "issue_reads", "skill")

# `repo` and `skill` are pinned to pandas' string dtype so that a frame no row
# of which names one has the same column type as a frame some rows of which do.
# Left to inference, an all-absent column comes back as object holding None
# while a mixed one comes back as strings holding NaN, and code written against
# one shape breaks on the other. Pinned, absence is always NA — the same as an
# interval row's absent session id, and read the same way, with `pd.isna`.
NAME_DTYPE = "str"

# --- reading the shell text ---------------------------------------------------

# `rest` runs to the next shell separator, which bounds one invocation: a line
# chaining two `gh issue` calls against different repos must not read the first
# one's `--repo` as the second's.
GH_ISSUE = re.compile(
    r"gh\s+issue\s+(?P<verb>"
    + "|".join((*WRITE_VERBS, *READ_VERBS))
    + r")\s+(?P<number>\d+)(?P<rest>[^;&|\n]*)"
)

# The owner is dropped, so `--repo GeoffNordling/dev-playbook` and a cwd under
# `workspace/dev-playbook` name the same repo. A flag whose value is a shell
# substitution matches nothing here, and the row's own repo stands instead —
# which is what such a substitution resolves to anyway.
REPO_FLAG = re.compile(r"--repo[=\s]+(?:[^\s/]+/)?(?P<repo>[\w.-]+)")


class AttributionError(Exception):
    """A row this module will not attribute.

    Raised rather than left unattributed: a `Skill` row whose kept input names
    no skill means the tool's input shape moved, and reading it as "no skill"
    would silently lose every agent-invoked skill — the exact blind spot capture
    was extended to close.
    """


@dataclass(frozen=True)
class Issues:
    """The issues one command line names, split by what it did to them.

    Both are tuples because one line can name several, and they are separate
    fields because a read and a write are different evidence.
    """

    writes: tuple[str, ...]
    reads: tuple[str, ...]


# What a row that names no issue carries — most rows, including every row that
# is not a Bash tool use.
NO_ISSUES = Issues((), ())


def repo_of(cwd: str, workspace: Path = WORKSPACE) -> str | None:
    """The repo `cwd` sits in, or None where it sits in none.

    The first segment under the workspace, so a worktree, a subdirectory and a
    checkout root all answer with the repo they belong to.

    None is a real state rather than a bad row: a session started at the
    workspace root itself, or anywhere outside it, genuinely belongs to no repo.
    The cleaned store holds 27 such rows.
    """
    path = Path(cwd)
    root = workspace.expanduser()
    if not path.is_relative_to(root):
        return None
    segments = path.relative_to(root).parts
    return segments[0] if segments else None


def issue_references(command: str, repo: str | None) -> Issues:
    """Every issue `command` names, qualified by `repo` where it names none itself.

    `repo` is the repo the command ran in — the row's own attribution — which is
    what `gh` acts on when the invocation carries no `--repo`. Pass None where
    the row has no repo either; the reference is then unqualified (`#272`), which
    names an issue without saying whose.

    One line naming the same issue twice yields it once. A view followed by a
    re-view of the same issue is one contact, not two.
    """
    writes: list[str] = []
    reads: list[str] = []
    for match in GH_ISSUE.finditer(command):
        flag = REPO_FLAG.search(match["rest"])
        named = flag["repo"] if flag else repo
        reference = f"{named}#{match['number']}" if named else f"#{match['number']}"
        found = writes if match["verb"] in WRITE_VERBS else reads
        found.append(reference)
    return Issues(tuple(dict.fromkeys(writes)), tuple(dict.fromkeys(reads)))


def skill_of(payload: dict) -> str | None:
    """The skill this row ran, by either invocation path, or None for neither.

    A human's `/skill` is the `command_name` the expansion carried; an agent's is
    the `skill` its `Skill` tool row was called with.

    A `Skill` row from before capture kept tool inputs has no input at all and
    answers None. That absence is a fact about capture history rather than an
    error — there is no backfill behind it — and it is the one absence tolerated
    here: an input that is present and names no skill is refused.
    """
    if COMMAND_NAME in payload:
        return _name_at(payload, COMMAND_NAME)
    if (
        payload["hook_event_name"] != POST_TOOL_USE
        or payload["tool_name"] != SKILL_TOOL
    ):
        return None
    if "tool_input" not in payload:
        return None
    kept = payload["tool_input"]
    if not isinstance(kept, dict) or SKILL_KEY not in kept:
        raise AttributionError(f"Skill row keeps an input naming no skill: {kept!r}")
    return _name_at(kept, SKILL_KEY)


def _name_at(payload: dict, key: str) -> str:
    """The skill name stored at `key`, refused if what is there is not one.

    Payload values arrive out of JSON untyped, and a name that came through as a
    number or an object is a shape no attribution can carry — better refused at
    the row than grouped into a lane named `None`.
    """
    value = payload[key]
    if not isinstance(value, str):
        raise AttributionError(f"{key} is a {type(value).__name__}, not a skill name")
    return value


def attributed(events: pd.DataFrame, workspace: Path = WORKSPACE) -> pd.DataFrame:
    """`events` with `repo`, `issue_writes`, `issue_reads` and `skill` added.

    A new frame; the caller's is untouched. Every row gets all four columns, so
    an absent attribution is an empty tuple or an NA in the row rather than a row
    missing from the table — a `Read` proves the session was in that repo whether
    or not any `gh` command ever named an issue.

    The two issue columns hold tuples, because one command line can name several
    issues. A caller wanting one row per issue explodes the column it cares
    about; a caller wanting both must explode them separately, which is the
    point — the two signals do not add up.
    """
    frame = events.copy()
    # Held as Python values first: the qualification below needs None for a row
    # with no repo, and the column's NA is not None.
    repos = [repo_of(cwd, workspace) for cwd in frame["cwd"]]
    issues = [
        _issues_of(payload, repo)
        for payload, repo in zip(frame["payload"], repos, strict=True)
    ]
    frame["repo"] = pd.Series(repos, dtype=NAME_DTYPE, index=frame.index)
    frame["issue_writes"] = [issue.writes for issue in issues]
    frame["issue_reads"] = [issue.reads for issue in issues]
    frame["skill"] = pd.Series(
        [skill_of(payload) for payload in frame["payload"]],
        dtype=NAME_DTYPE,
        index=frame.index,
    )
    return frame


def _issues_of(payload: dict, repo: str | None) -> Issues:
    """The issues one row names — none unless it is a Bash tool use.

    Bash is the only tool whose `tool_input` is stored whole, so it is the only
    row a command line can be read from at all.
    """
    if payload["hook_event_name"] != POST_TOOL_USE or payload["tool_name"] != BASH_TOOL:
        return NO_ISSUES
    return issue_references(payload["tool_input"]["command"], repo)
