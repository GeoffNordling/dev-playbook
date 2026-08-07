"""Audit the workspace: GitHub repo settings, label/issue conformance, and pins.

The library behind the ``workspace-lint`` shim — the on-demand audit venue of
the enforcement standard, the checks that live outside any single commit. It
answers workspace-scope facts readable over `gh api`, and it reports and never
blocks — GitHub sits outside every gate.

The audited population is the ``GOVERNED`` roster, not whatever happens to sit
under the workspace root: repos land there for reasons the standard has no say
in, so governance is declared rather than inferred. For each governed repo:

  - **settings** — read the repo's merge settings over `gh api graphql` and
    compare them against the expected values (squash-only merges, PR title/body
    commit message, auto-deleted merged branches). REST is not the venue: its
    repository object omits every merge field for a fine-grained token — a 200
    whose body simply lacks them, whatever permissions the token carries — which
    would read as six drifted settings on every repo. A repo the API cannot
    reach, or with no GitHub origin, is reported loudly.
  - **protection** — read the rules in force on the default branch and require
    the two that deny destructive operations: no force-push, no deletion. The
    read is of the branch's effective rules, not of the ruleset list, so how a
    repo organizes its rulesets is its own business.
  - **labels** — compare the repo's labels against the canonical scheme at full
    parity (a finding exactly when bootstrap-labels would repair), and flag any
    label naming a blocked state.
  - **issues** — from one open-issues read, check each open issue against the
    shape rules of its species: a build leaf's four-tuple validity and brief
    shape, a build epic's category-only shape, and a wayfinder map's or decision
    ticket's shape. Species comes from the label set and ``sub_issues_summary``.
  - **pin** — read the dev-playbook `rev` pinned in the repo's
    `.pre-commit-config.yaml` and compare it against the hook repo's local
    `main`. Stale pins are reported but are not failures: a consumer catches up
    when its pin is deliberately bumped. No pin at all is a failure — being
    governed is what makes the absence wrong.

Every check but the pin reads GitHub, so an authenticated `gh` is a precondition
of the run rather than a per-repo condition: the audit checks it once up front
and refuses to start without it, because an unauthenticated `gh` degrades to
anonymous requests instead of failing (see ``check_auth``). ``--pins-only``
reads nothing over the network and so is exempt.

Output:
    stdout — one finding per line, ``repo: card.rule message`` (the repo name
             stands in the location slot; this audit inspects repos, not files).
    stderr — informational per-repo lines (current/absent pins) and one summary.
    exit   — 0 clean, 1 findings, 2 cannot run.
"""

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from dev_playbook import gitrepo, md
from dev_playbook.findings import print_rules, render
from dev_playbook.label_scheme import canonical_labels, values_by_dimension

# Every rule id this detector can emit. Repo-settings drift, reachability, and
# the live-repo tracking checks (label scheme, blocked labels, brief shape, epic
# shape, wayfinder shape) answer the tracking card; four-tuple validity answers
# the software-factory card; a stale dev-playbook pin answers the build card
# (non-blocking).
# Informational pin lines carry no rule id. Each id is a module-level constant so
# every emission site references the constant, never a raw literal, and RULES
# (what --list-rules prints) cannot drift from what the detector actually emits.
SETTINGS = "tracking.settings"
PROTECTION = "tracking.branch-protection"
REMOTE = "tracking.remote"
LABEL_SCHEME = "tracking.label-scheme"
NO_BLOCKED_LABEL = "tracking.no-blocked-label"
ISSUE_BRIEF_SHAPE = "tracking.issue-brief-shape"
EPIC_SHAPE = "tracking.epic-shape"
WAYFINDER_SHAPE = "tracking.wayfinder-shape"
TUPLE_VALID = "software-factory.tuple-valid"
PIN = "build.pin"

RULES = (
    SETTINGS,
    PROTECTION,
    REMOTE,
    LABEL_SCHEME,
    NO_BLOCKED_LABEL,
    ISSUE_BRIEF_SHAPE,
    EPIC_SHAPE,
    WAYFINDER_SHAPE,
    TUPLE_VALID,
    PIN,
)

# The required headings of each brief format, stated here exactly as
# standards/tracking/issue-authoring.md states them — the doc and this rule
# read one contract and cannot disagree. A build leaf carries all seven; a
# spike leaf carries the spike shape.
BUILD_HEADINGS = (
    "Summary",
    "User intent",
    "Current behavior",
    "Desired behavior",
    "Key interfaces",
    "Acceptance criteria",
    "Out of scope",
)
SPIKE_HEADINGS = ("Summary", "Question", "Deliverable")

# The body sections of a wayfinder map and of a decision ticket, stated here
# exactly as the ``/wayfinder`` skill states them (``§ The map body`` and
# ``§ Tickets`` of dotfiles/.agents/skills/wayfinder/SKILL.md). The skill — not
# this workspace — is the definition of a map's shape, per
# standards/tracking/issue-authoring.md § Two species of epic, so this rule
# mirrors the skill directly, the way BUILD_HEADINGS mirrors the brief standard.
# The bundle is installed verbatim at a pin, which is what makes the mirror
# stable: a pin bump delta-checks these tuples against the upstream text.
# Wayfinder writes ``##`` sections, not the bold headings a brief uses.
MAP_SECTIONS = (
    "Destination",
    "Notes",
    "Decisions so far",
    "Not yet specified",
    "Out of scope",
)
TICKET_SECTIONS = ("Question",)

# The four dimensions of the state-machine tuple (status is not part of it).
TUPLE_DIMENSIONS = ("category", "mode", "tests", "phase")

HOOK_REPO_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_CONFIG = (
    HOOK_REPO_ROOT / "standards" / "build" / "canonical" / ".pre-commit-config.yaml"
)

# The governed repos — the workspace population the standards apply to, named
# here because governance is an act rather than a property of sitting under the
# workspace root. Inclusion is the decision: a repo absent from this tuple is
# simply not governed, and the audit says nothing about it. That is what keeps
# the roster a record of intent instead of a chore that fires on every clone.
#
# The default of the ``--repos`` option, exactly as ``~/workspace`` is the
# default of ``--workspace``: both are facts about a machine's layout, not about
# the standard, and both are overridable for a one-off run.
GOVERNED = (
    "dev-playbook",
    "story-forge",
    "spec-tools",
    "mission-control",
    "fedora-playbook",
)

# Expected GitHub settings, under the REST field names. The audit only reads;
# the merge settings are set by hand per the repo-settings standard.
EXPECTED_SETTINGS = {
    "allow_squash_merge": True,
    "allow_merge_commit": False,
    "allow_rebase_merge": False,
    "delete_branch_on_merge": True,
    "squash_merge_commit_title": "PR_TITLE",
    "squash_merge_commit_message": "PR_BODY",
}

# The GraphQL field serving each expected setting. GraphQL is the only venue
# that answers these for a fine-grained token; the names map back to the REST
# ones so findings stay in one vocabulary. Both venues share the enum values
# ("PR_TITLE", "PR_BODY"), so only the keys need translating.
SETTINGS_FIELDS = {
    "squashMergeAllowed": "allow_squash_merge",
    "mergeCommitAllowed": "allow_merge_commit",
    "rebaseMergeAllowed": "allow_rebase_merge",
    "deleteBranchOnMerge": "delete_branch_on_merge",
    "squashMergeCommitTitle": "squash_merge_commit_title",
    "squashMergeCommitMessage": "squash_merge_commit_message",
}

SETTINGS_QUERY = """query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    squashMergeAllowed
    mergeCommitAllowed
    rebaseMergeAllowed
    deleteBranchOnMerge
    squashMergeCommitTitle
    squashMergeCommitMessage
  }
}"""

# The rule types the default branch must carry, each mapped to the operation it
# denies, so a finding names the exposure rather than the GraphQL enum. Together
# these two are what "protected against destructive operations" means: history
# cannot be rewritten under the branch, and the branch cannot be removed.
REQUIRED_RULES = {
    "NON_FAST_FORWARD": "force-push",
    "DELETION": "deletion",
}

# Rules are read off the default branch rather than out of the ruleset list, so
# the audit asks what protects the branch instead of how the protection is
# organized. ``defaultBranchRef.rules`` is the effective view — every rule
# reaching the branch from every ruleset, whatever those rulesets are named, how
# many there are, or which ref patterns they match — so a repo may reorganize
# its rulesets freely without moving this detector. The branch name comes back
# with it, so nothing here assumes ``main``.
PROTECTION_QUERY = """query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    defaultBranchRef {
      name
      rules(first: 100) {
        nodes {
          type
        }
      }
    }
  }
}"""

REMOTE_SLUG_PATTERN = re.compile(
    r"^(?:git@github\.com:|https://github\.com/)([^/\s]+/[^/\s]+?)(?:\.git)?$"
)


class ToolError(Exception):
    """The audit could not run at all."""


@dataclass(frozen=True)
class Line:
    """One line of the audit's output — a finding or an informational advisory."""

    repo: str
    rule: str | None  # None = informational (no rule id): a stderr advisory
    message: str
    blocking: bool = False  # a real finding: sets exit 1

    @property
    def stale(self) -> bool:
        """Whether this line reports a stale (non-blocking) dev-playbook pin."""
        return self.rule == PIN and not self.blocking

    def render(self) -> str:
        """The finding rendered as ``repo: card.rule message``."""
        assert self.rule is not None
        return render(self.repo, self.rule, self.message)


def hook_repo_url() -> str:
    """The published hook-repo URL, read from the canonical config's pinned block."""
    text = CANONICAL_CONFIG.read_text(encoding="utf-8")
    match = re.search(r"-\s*repo:\s*(\S+)\n\s*rev:\s*<pinned-sha>", text)
    if not match:
        raise ToolError(f"no pinned block in {CANONICAL_CONFIG}")
    return match.group(1)


def hook_repo_main() -> str:
    """The hook repo's local ``main`` commit sha."""
    result = subprocess.run(
        ["git", "-C", str(HOOK_REPO_ROOT), "rev-parse", "main"],
        capture_output=True,
        text=True,
        env=gitrepo.no_git_env(),
    )
    if result.returncode != 0:
        raise ToolError(
            f"cannot resolve main in {HOOK_REPO_ROOT}: {result.stderr.strip()}"
        )
    return result.stdout.strip()


def workspace_repos(workspace: Path, roster: tuple[str, ...]) -> list[Path]:
    """The roster's repos under ``workspace``, in roster order.

    Only the listed repos are audited — an unlisted repo under the root is not
    governed and draws no output. The reverse does not hold: a listed repo that
    is not a git repo under the root is a false claim by the roster, and the
    audit refuses to run rather than quietly auditing a shorter list.
    """
    if not workspace.is_dir():
        raise ToolError(f"workspace root not found: {workspace}")
    repos = [workspace / name for name in roster]
    missing = [repo.name for repo in repos if not (repo / ".git").exists()]
    if missing:
        raise ToolError(
            f"governed repo(s) not found under {workspace}: {', '.join(missing)}"
        )
    return repos


def origin_slug(repo: Path) -> str | None:
    """``owner/name`` from the repo's GitHub origin, or None if there is none."""
    result = subprocess.run(
        ["git", "-C", str(repo), "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        env=gitrepo.no_git_env(),
    )
    if result.returncode != 0:
        return None
    match = REMOTE_SLUG_PATTERN.match(result.stdout.strip())
    return match.group(1) if match else None


def rev_line(lines: list[str], url: str) -> int | None:
    """Index of the ``rev:`` line pinning ``url``, or None when there is none.

    The one place a pinned block's rev line is located. The audit reads through
    it and bump_pins rewrites through it, so the reader and the writer cannot
    disagree about which line carries the pin.
    """
    for i, line in enumerate(lines):
        if re.match(rf"^\s*-\s*repo:\s*{re.escape(url)}\s*$", line):
            for follower in range(i + 1, min(i + 3, len(lines))):
                if re.match(r"^\s*rev:\s*\S+", lines[follower]):
                    return follower
    return None


def pinned_rev(config_text: str, url: str) -> str | None:
    """The ``rev`` pinned for ``url`` in a ``.pre-commit-config.yaml`` body, or None."""
    lines = config_text.splitlines()
    index = rev_line(lines, url)
    return lines[index].split(":", 1)[1].strip() if index is not None else None


def check_pin(repo: Path, url: str, main_sha: str) -> Line | None:
    """One pin line per consumer repo; None for the hook repo itself.

    A governed repo carrying no pin at all is a finding, not an advisory: being
    on the roster is what makes the absence wrong. A stale pin stays advisory —
    the consumer catches up when its pin is deliberately bumped.
    """
    # Only dev-playbook itself is exempt, and identity is the test: it dogfoods
    # from its working tree, so it has nothing to pin. Publishing a manifest is
    # not the test — a consumer may publish hooks of its own and still pin
    # dev-playbook, and reading the exemption off the manifest would drop that
    # repo's pin from the audit entirely.
    if repo.resolve() == HOOK_REPO_ROOT:
        return None
    name = repo.name
    config = repo / ".pre-commit-config.yaml"
    if not config.is_file():
        return Line(name, PIN, "no .pre-commit-config.yaml", blocking=True)
    rev = pinned_rev(config.read_text(encoding="utf-8"), url)
    if rev is None:
        return Line(name, PIN, "no dev-playbook pin", blocking=True)
    current = main_sha == rev or (len(rev) >= 7 and main_sha.startswith(rev))
    if current:
        return Line(name, None, "pin current")
    return Line(
        name,
        PIN,
        f"{rev} (hook repo main is {main_sha[:12]})",
    )


def gh_api(path: str, *, paginate: bool = False) -> object | None:
    """Parsed JSON from ``gh api <path>``, or None when the call fails.

    A non-zero exit or a body that is not JSON (an empty 204, a degraded/HTML
    error page) yields None for that one path, so a single bad response degrades
    to an unreachable finding rather than a traceback that blinds the audit to
    every remaining repo. With ``paginate=True``, ``gh api --paginate`` follows
    the Link headers and merges every page's JSON array into one array, so a list
    endpoint with more than a page of results is read in full.
    """
    argv = ["gh", "api"]
    if paginate:
        argv.append("--paginate")
    argv.append(path)
    return _gh_json(argv)


def _gh_json(argv: list[str]) -> object | None:
    """Parsed JSON from one ``gh`` invocation, or None when the call is unusable."""
    try:
        result = subprocess.run(argv, capture_output=True, text=True)
    except FileNotFoundError as err:
        raise ToolError("gh not found on PATH") from err
    if result.returncode != 0:
        return None
    try:
        parsed: object = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    return parsed


def check_auth() -> None:
    """Stop the run when `gh` holds no usable credential.

    Authentication is a precondition of the whole audit, not a per-repo
    condition, because an unauthenticated `gh` does not fail — it degrades to
    anonymous requests, and anonymity is answered three different ways. A public
    repo serves its REST resources, so labels and issues return real findings. A
    private repo answers 404, indistinguishable from one that was deleted.
    GraphQL has no anonymous mode at all, so the settings check fails on every
    repo whatever its visibility. The audit would then print a mix of genuine
    findings and per-repo unreachable lines under one exit 1, with nothing in the
    output telling a reader which was which. Refusing to start is the only honest
    answer.
    """
    try:
        result = subprocess.run(
            ["gh", "auth", "status"], capture_output=True, text=True
        )
    except FileNotFoundError as err:
        raise ToolError("gh not found on PATH") from err
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise ToolError(
            "gh holds no usable credential, so every GitHub read would "
            "silently degrade to an anonymous request. Run `gh auth login`, or "
            "re-run where the credential store is readable — a sandbox that "
            f"hides it produces exactly this.\n{detail}"
        )


def gh_graphql(query: str, **variables: str) -> object | None:
    """Parsed JSON from ``gh api graphql``, or None when the call fails.

    The same degradation contract as ``gh_api``: a non-zero exit (which is how
    `gh` reports GraphQL errors) or an unparseable body yields None for that one
    call, so a single bad response degrades to an unreachable finding.
    """
    argv = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        argv += ["-f", f"{key}={value}"]
    return _gh_json(argv)


def fetch_settings(slug: str) -> dict | None:
    """The repo's merge settings under their REST names, or None when unusable.

    A failed read, a wrong-shaped response, a null repository, or a repository
    object that does not carry every expected field degrades to None — the
    unreachable path — so one malformed response cannot abort the whole run.
    That last case is the one REST fails: it answers 200 with the merge fields
    absent, and a partial read reported as drift is a wrong answer, not a
    lenient one.
    """
    owner, _, name = slug.partition("/")
    data = gh_graphql(SETTINGS_QUERY, owner=owner, name=name)
    if not isinstance(data, dict):
        return None
    payload = data.get("data")
    repository = payload.get("repository") if isinstance(payload, dict) else None
    if (
        not isinstance(repository, dict)
        or not SETTINGS_FIELDS.keys() <= repository.keys()
    ):
        return None
    return {rest: repository[field] for field, rest in SETTINGS_FIELDS.items()}


def fetch_protection(slug: str) -> tuple[str, set[str]] | None:
    """The default branch's name and the rule types in force on it, or None.

    Its own round trip rather than extra fields on ``SETTINGS_QUERY``: the two
    reads then degrade independently, so a repo that answers one and not the
    other still reports what it could answer. The audit runs on demand over a
    roster of five, which is what makes the second call affordable.

    An empty rule list is data, not a failure — it is precisely the unprotected
    repo, and reporting it is the point. None is reserved for a read that could
    not be trusted: an unusable response, or a repository with no default branch
    at all (an empty repo), where there is no branch whose protection to judge.
    """
    owner, _, name = slug.partition("/")
    data = gh_graphql(PROTECTION_QUERY, owner=owner, name=name)
    if not isinstance(data, dict):
        return None
    payload = data.get("data")
    repository = payload.get("repository") if isinstance(payload, dict) else None
    if not isinstance(repository, dict):
        return None
    ref = repository.get("defaultBranchRef")
    if not isinstance(ref, dict) or not isinstance(ref.get("name"), str):
        return None
    rules = ref.get("rules")
    nodes = rules.get("nodes") if isinstance(rules, dict) else None
    if not isinstance(nodes, list):
        return None
    types = {
        node["type"]
        for node in nodes
        if isinstance(node, dict) and isinstance(node.get("type"), str)
    }
    return ref["name"], types


def fetch_labels(slug: str) -> list | None:
    """Every label on the repo (all pages), or None when the read is unusable.

    A failed read or a wrong-shaped response (anything but a JSON array) degrades
    to None — the unreachable path.
    """
    data = gh_api(f"repos/{slug}/labels?per_page=100", paginate=True)
    return data if isinstance(data, list) else None


def fetch_issues(slug: str) -> list | None:
    """Every open issue on the repo (all pages), or None when the read is unusable.

    A failed read or a wrong-shaped response (anything but a JSON array) degrades
    to None — the unreachable path.
    """
    data = gh_api(f"repos/{slug}/issues?per_page=100&state=open", paginate=True)
    return data if isinstance(data, list) else None


def check_settings(repo: Path, slug: str | None) -> list[Line]:
    """A repo's GitHub merge settings against the expected values.

    A loud finding when the repo has no GitHub origin (``slug`` is None) or the
    settings API is unreachable; otherwise one finding per drifted field.
    """
    name = repo.name
    if slug is None:
        return [
            Line(name, REMOTE, "no GitHub origin; settings unchecked", blocking=True)
        ]
    settings = fetch_settings(slug)
    if settings is None:
        return [Line(name, SETTINGS, f"unreachable via gh api ({slug})", blocking=True)]
    return [
        Line(
            name,
            SETTINGS,
            f"{field} is {settings.get(field)!r} (want {want!r})",
            blocking=True,
        )
        for field, want in EXPECTED_SETTINGS.items()
        if settings.get(field) != want
    ]


def check_protection(repo: Path, slug: str | None) -> list[Line]:
    """The default branch's protection against destructive operations.

    A repo with no GitHub origin draws nothing here: ``check_settings`` already
    reports that once, and one missing origin should not print twice under two
    rule ids.
    """
    name = repo.name
    if slug is None:
        return []
    found = fetch_protection(slug)
    if found is None:
        return [
            Line(
                name,
                PROTECTION,
                f"rules unreachable via gh api ({slug})",
                blocking=True,
            )
        ]
    branch, rules = found
    return [
        Line(
            name,
            PROTECTION,
            f"{branch} is not protected against {operation}",
            blocking=True,
        )
        for rule, operation in REQUIRED_RULES.items()
        if rule not in rules
    ]


def check_labels(name: str, labels: list) -> list[Line]:
    """A repo's labels against the canonical scheme, at full parity.

    Mirrors what bootstrap-labels would repair — a finding for every missing
    label, every drifted color/description, and every label outside the closed
    world — plus its own named rule for any label naming a blocked state (which
    the closed-world check already flags, deliberately overlapping).
    """
    have = {label["name"]: label for label in labels}
    canonical = canonical_labels()
    canonical_names = {label_name for label_name, _, _ in canonical}
    lines: list[Line] = []
    for label_name, color, desc in canonical:
        if label_name not in have:
            lines.append(
                Line(name, LABEL_SCHEME, f"missing label {label_name}", blocking=True)
            )
        elif (
            have[label_name].get("color", "").lower() != color.lower()
            or have[label_name].get("description", "") != desc
        ):
            lines.append(
                Line(
                    name,
                    LABEL_SCHEME,
                    f"label {label_name} drifted (color/description)",
                    blocking=True,
                )
            )
    for label_name in sorted(have):
        if label_name not in canonical_names:
            lines.append(
                Line(
                    name, LABEL_SCHEME, f"unexpected label {label_name}", blocking=True
                )
            )
        if label_name.split(":")[-1].lower() == "blocked":
            lines.append(
                Line(
                    name,
                    NO_BLOCKED_LABEL,
                    f"label {label_name} names a blocked state",
                    blocking=True,
                )
            )
    return lines


def _post_intake(labels: set[str]) -> bool:
    """Whether an issue is triaged past intake.

    In scope once it carries a phase label other than phase:intake; untriaged
    issues (no phase, or only phase:intake) are out.
    """
    return any(
        label.startswith("phase:") and label != "phase:intake" for label in labels
    )


def _has_heading(prose: list[str], heading: str) -> bool:
    """Whether the brief's prose lines carry the bold heading.

    The colon may sit inside or outside the markers — both ``**Heading:**`` and
    ``**Heading**:`` read as present. The lines come already stripped of fenced
    code, so a heading inside a fence neither satisfies a required heading nor
    forges one the brief lacks: a brief quotes templates inside fences — the
    brief template itself, an approved artifact under ``## Artifacts`` — and a
    quoted heading is being *shown*, not carried. The caller does the stripping
    once per body rather than once per heading.
    """
    pattern = re.compile(rf"\*\*\s*{re.escape(heading)}\s*(?:\*\*)?\s*:", re.IGNORECASE)
    return any(pattern.search(line) for line in prose)


def _has_section(body: str, section: str) -> bool:
    """Whether the body carries the markdown section heading.

    Wayfinder bodies are ``##``-sectioned rather than bold-headed, so this is the
    section counterpart of ``_has_heading`` in what it looks for. It is not its
    counterpart in fence handling: this scans the raw body, so a ``##`` section
    quoted inside a fence forges one the map lacks. Deliberate — fence awareness
    was scoped to the brief-shape audit — and tracked in GeoffNordling/dev-playbook#386.

    Any heading level reads as present: the level is the skill's formatting, the
    section's presence is the rule.
    """
    pattern = rf"^\s{{0,3}}#{{1,6}}\s+{re.escape(section)}\s*#*\s*$"
    return re.search(pattern, body, re.IGNORECASE | re.MULTILINE) is not None


def _dimension_values(labels: set[str], dim: str) -> list[str]:
    """The sorted values a label set carries for one ``<dim>:`` prefix."""
    return sorted(
        label.split(":", 1)[1] for label in labels if label.startswith(f"{dim}:")
    )


def _factory_labels(labels: set[str]) -> list[str]:
    """The sorted factory-dimension labels a label set carries.

    The four dimensions that route an issue through the software factory. A
    wayfinder issue carries none of them: it never enters the graph.
    """
    prefixes = tuple(f"{dim}:" for dim in TUPLE_DIMENSIONS)
    return sorted(label for label in labels if label.startswith(prefixes))


def _map_findings(name: str, number: int, labels: set[str], body: str) -> list[Line]:
    """Findings for a wayfinder map that breaks its shape.

    A map is a planning epic, so it carries no factory-dimension label and is not
    itself a ticket; its body carries the sections the ``/wayfinder`` skill
    states. The map/build-epic split is the species distinction — this is the
    map's own shape rule, not an exemption from the build epic's.
    """
    lines: list[Line] = []
    offending = _factory_labels(labels)
    if offending:
        lines.append(
            Line(
                name,
                WAYFINDER_SHAPE,
                f"#{number} map carries {offending}; a map carries no factory label",
                blocking=True,
            )
        )
    types = sorted(set(_dimension_values(labels, "wayfinder")) - {"map"})
    if types:
        lines.append(
            Line(
                name,
                WAYFINDER_SHAPE,
                f"#{number} map also carries ticket types {types}; a map is not a ticket",
                blocking=True,
            )
        )
    lines.extend(
        Line(
            name,
            WAYFINDER_SHAPE,
            f"#{number} map missing {section} section",
            blocking=True,
        )
        for section in MAP_SECTIONS
        if not _has_section(body, section)
    )
    return lines


def _ticket_findings(
    name: str, number: int, labels: set[str], body: str, scheme: dict[str, set[str]]
) -> list[Line]:
    """Findings for a decision ticket that breaks its shape.

    A ticket is not a factory leaf: it carries exactly one in-scheme
    ``wayfinder:<type>``, no factory-dimension label, and the body section the
    ``/wayfinder`` skill states. This mirrors the leaf's tuple and brief rules at
    the ticket's own, much smaller, contract.
    """
    lines: list[Line] = []
    offending = _factory_labels(labels)
    if offending:
        lines.append(
            Line(
                name,
                WAYFINDER_SHAPE,
                f"#{number} ticket carries {offending}; a decision ticket carries no factory label",
                blocking=True,
            )
        )
    types = _dimension_values(labels, "wayfinder")
    if len(types) > 1:
        lines.append(
            Line(
                name,
                WAYFINDER_SHAPE,
                f"#{number} ticket has multiple wayfinder labels: {types}",
                blocking=True,
            )
        )
    elif types[0] not in scheme["wayfinder"]:
        lines.append(
            Line(
                name,
                WAYFINDER_SHAPE,
                f"#{number} ticket wayfinder:{types[0]} is not a scheme value",
                blocking=True,
            )
        )
    lines.extend(
        Line(
            name,
            WAYFINDER_SHAPE,
            f"#{number} ticket missing {section} section",
            blocking=True,
        )
        for section in TICKET_SECTIONS
        if not _has_section(body, section)
    )
    return lines


def _epic_findings(
    name: str, number: int, labels: set[str], scheme: dict[str, set[str]]
) -> list[Line]:
    """Findings for an epic that breaks its category-only shape.

    An epic (an issue with children) carries exactly one valid category label and
    nothing else — no phase/mode/tests, and a present, single, in-scheme category.
    """
    lines: list[Line] = []
    offending = sorted(
        label for label in labels if label.startswith(("phase:", "mode:", "tests:"))
    )
    if offending:
        lines.append(
            Line(
                name,
                EPIC_SHAPE,
                f"#{number} epic carries {offending}; an epic carries a category label only",
                blocking=True,
            )
        )
    categories = _dimension_values(labels, "category")
    if not categories:
        lines.append(
            Line(
                name,
                EPIC_SHAPE,
                f"#{number} epic missing category label",
                blocking=True,
            )
        )
    elif len(categories) > 1:
        lines.append(
            Line(
                name,
                EPIC_SHAPE,
                f"#{number} epic has multiple category labels: {categories}",
                blocking=True,
            )
        )
    elif categories[0] not in scheme["category"]:
        lines.append(
            Line(
                name,
                EPIC_SHAPE,
                f"#{number} epic category:{categories[0]} is not a scheme value",
                blocking=True,
            )
        )
    return lines


def _tuple_findings(
    name: str, number: int, labels: set[str], scheme: dict[str, set[str]]
) -> list[Line]:
    """Findings for a leaf whose four-tuple is invalid.

    A leaf carries the full four-tuple: one label per dimension, each value in the
    scheme, and the mode↔tests pairings holding.
    """
    present = {dim: _dimension_values(labels, dim) for dim in TUPLE_DIMENSIONS}
    lines: list[Line] = []
    for dim in TUPLE_DIMENSIONS:
        vals = present[dim]
        if not vals:
            lines.append(
                Line(name, TUPLE_VALID, f"#{number} missing {dim} label", blocking=True)
            )
        elif len(vals) > 1:
            lines.append(
                Line(
                    name,
                    TUPLE_VALID,
                    f"#{number} multiple {dim} labels: {vals}",
                    blocking=True,
                )
            )
        elif vals[0] not in scheme[dim]:
            lines.append(
                Line(
                    name,
                    TUPLE_VALID,
                    f"#{number} {dim}:{vals[0]} is not a scheme value",
                    blocking=True,
                )
            )
    mode = present["mode"][0] if len(present["mode"]) == 1 else None
    tests = present["tests"][0] if len(present["tests"]) == 1 else None
    if mode == "spike" and tests != "no":
        lines.append(
            Line(
                name,
                TUPLE_VALID,
                f"#{number} mode:spike requires tests:no",
                blocking=True,
            )
        )
    return lines


def _brief_findings(name: str, number: int, labels: set[str], body: str) -> list[Line]:
    """A leaf's body carries its mode's required brief headings."""
    modes = _dimension_values(labels, "mode")
    if len(modes) != 1:
        return []  # a missing or ambiguous mode is tuple-valid's finding
    mode = modes[0]
    required: tuple[str, ...]
    if mode == "spike":
        required = SPIKE_HEADINGS
    elif mode == "direct":
        required = BUILD_HEADINGS
    else:
        return []  # an unknown mode value is tuple-valid's finding
    try:
        prose = [line for _, line in md.lines_outside_fences(body)]
    except md.UnclosedFence as unclosed:
        # An issue body is authored on GitHub, past the reach of any hook that
        # could have caught this at commit time, and the audit sweeps every open
        # issue of every governed repo — so the fence is reported as this
        # issue's finding and the sweep goes on, rather than the exception
        # ending the run. The headings past the fence are unreadable, so they
        # are not reported as missing on top of it.
        return [
            Line(
                name,
                ISSUE_BRIEF_SHAPE,
                f"#{number} body has an {unclosed}",
                blocking=True,
            )
        ]
    return [
        Line(
            name,
            ISSUE_BRIEF_SHAPE,
            f"#{number} missing {heading} heading",
            blocking=True,
        )
        for heading in required
        if not _has_heading(prose, heading)
    ]


def check_issues(name: str, issues: list) -> list[Line]:
    """Every open issue against the shape rules of its species.

    Four species, each with its own contract: a **wayfinder map** and a
    **decision ticket** (told by their ``wayfinder:*`` labels, shaped as the
    ``/wayfinder`` skill states), a **build epic** (told by having children,
    category-only), and a **build leaf** (the four-tuple and brief shape, checked
    only once triaged past intake).

    Species comes off the label set and sub_issues_summary — no per-issue API
    call. Pull requests the issues endpoint returns are skipped.
    """
    scheme = values_by_dimension()
    lines: list[Line] = []
    for issue in issues:
        if "pull_request" in issue:
            continue
        # GitHub always returns a labels array (empty at worst); a missing key
        # is a malformed response, so index it and let the KeyError surface.
        labels = {label["name"] for label in issue["labels"]}
        number = issue["number"]
        body = issue.get("body") or ""
        # GitHub returns sub_issues_summary as null (not absent) for an issue
        # with no children, so `or {}` covers both the missing and null cases.
        total = (issue.get("sub_issues_summary") or {}).get("total", 0)
        wayfinder = set(_dimension_values(labels, "wayfinder"))
        if "map" in wayfinder:
            # A map is told by its label, not by having children: a freshly
            # charted map with no tickets yet is still a map.
            lines.extend(_map_findings(name, number, labels, body))
        elif wayfinder:
            # A ticket carries a wayfinder type and no phase label, so it would
            # otherwise fall past the post-intake gate unchecked.
            lines.extend(_ticket_findings(name, number, labels, body, scheme))
        elif total > 0:
            # An epic (issue with children) carries a category label only — the
            # invariant holds regardless of triage state, so the epic branch is
            # not gated on post-intake (a phase label on an epic is itself a
            # finding).
            lines.extend(_epic_findings(name, number, labels, scheme))
        elif _post_intake(labels):
            # A leaf is checked only once triaged; untriaged leaves are out.
            lines.extend(_tuple_findings(name, number, labels, scheme))
            lines.extend(_brief_findings(name, number, labels, body))
    return lines


def _fetch_or_report(
    name: str,
    slug: str,
    rule: str,
    resource: str,
    fetcher: Callable[[str], list | None],
    checker: Callable[[str, list], list[Line]],
) -> list[Line]:
    """``checker``'s findings for one live resource, or a lone unreachable finding.

    A failed read is not a clean audit — surface it loudly (mirroring
    check_settings) rather than reporting zero findings for the repo. The
    unreachable finding is filed under ``rule``.
    """
    payload = fetcher(slug)
    if payload is None:
        return [
            Line(
                name, rule, f"{resource} unreachable via gh api ({slug})", blocking=True
            )
        ]
    return checker(name, payload)


def check_tracking(repo: Path, slug: str | None) -> list[Line]:
    """The live-repo label and issue checks, from one labels and one issues fetch.

    Skipped when the repo has no GitHub origin — check_settings has already
    reported that.
    """
    if slug is None:
        return []
    return [
        *_fetch_or_report(
            repo.name, slug, LABEL_SCHEME, "labels", fetch_labels, check_labels
        ),
        *_fetch_or_report(
            repo.name, slug, ISSUE_BRIEF_SHAPE, "issues", fetch_issues, check_issues
        ),
    ]


def main(argv: list[str] | None = None) -> int:
    """The ``workspace-lint`` command-line entry point.

    Returns the process exit code: 0 clean, 1 findings, 2 cannot run.
    """
    parser = argparse.ArgumentParser(
        prog="workspace-lint",
        description=(
            "Report GitHub settings drift, label/issue/epic/tuple conformance, "
            "and stale dev-playbook pins across the workspace."
        ),
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.home() / "workspace",
        help="workspace root holding the repos (default: ~/workspace)",
    )
    parser.add_argument(
        "--repos",
        type=lambda value: tuple(name for name in value.split(",") if name),
        default=GOVERNED,
        help="comma-separated repo names to audit (default: the governed roster)",
    )
    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="print the rule ids this detector can emit, one per line, and exit",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--pins-only", action="store_true", help="skip the gh api checks")
    mode.add_argument(
        "--settings-only",
        action="store_true",
        help=(
            "run only the repo-settings checks — merge settings and default-branch "
            "protection (skip pins and the tracking gh-api checks)"
        ),
    )
    args = parser.parse_args(argv)
    if args.list_rules:
        return print_rules(RULES)

    try:
        repos = workspace_repos(args.workspace.resolve(), args.repos)
        if not args.pins_only:
            check_auth()
        url = hook_repo_url()
        main_sha = hook_repo_main() if not args.settings_only else ""
        lines: list[Line] = []
        for repo in repos:
            if not args.settings_only:
                pin = check_pin(repo, url, main_sha)
                if pin is not None:
                    lines.append(pin)
            if not args.pins_only:
                slug = origin_slug(repo)
                lines.extend(check_settings(repo, slug))
                lines.extend(check_protection(repo, slug))
                if not args.settings_only:
                    lines.extend(check_tracking(repo, slug))
    except ToolError as err:
        print(f"workspace-lint: {err}", file=sys.stderr)
        return 2

    for line in lines:
        if line.rule is not None:
            print(line.render())
        else:
            print(f"workspace-lint: {line.repo}: {line.message}", file=sys.stderr)

    findings = sum(1 for line in lines if line.blocking)
    stale = sum(1 for line in lines if line.stale)
    print(
        f"workspace-lint: {len(repos)} repos, {findings} finding(s), {stale} stale pin(s)",
        file=sys.stderr,
    )
    return 1 if findings else 0
