"""Audit the workspace: GitHub repo settings, label/issue conformance, and pins.

The library behind the ``workspace-lint`` shim — the on-demand audit venue of
the enforcement standard, the checks that live outside any single commit. It
answers workspace-scope facts readable over `gh api`, and it reports and never
blocks — GitHub sits outside every gate. For every git repo under the workspace
root:

  - **settings** — read the repo's GitHub settings over `gh api` and compare
    them against the expected values (squash-only merges, PR title/body commit
    message, auto-deleted merged branches). A repo the API cannot reach, or with
    no GitHub origin, is reported loudly.
  - **labels** — compare the repo's labels against the canonical scheme at full
    parity (a finding exactly when bootstrap-labels would repair), and flag any
    label naming a blocked state.
  - **issues** — from one open-issues read, check every post-intake leaf's
    four-tuple validity and brief shape, and every epic's category-only shape;
    epic/leaf comes from ``sub_issues_summary``.
  - **pin** — read the dev-playbook `rev` pinned in the repo's
    `.pre-commit-config.yaml` and compare it against the hook repo's local
    `main`. Stale pins are reported but are not failures: a consumer catches up
    when its pin is deliberately bumped.

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

from dev_playbook import gitrepo
from dev_playbook.findings import print_rules, render
from dev_playbook.label_scheme import canonical_labels, values_by_dimension

# Every rule id this detector can emit. Repo-settings drift, reachability, and
# the live-repo tracking checks (label scheme, blocked labels, brief shape, epic
# shape) answer the tracking card; four-tuple validity answers the software-factory
# card; a stale dev-playbook pin answers the build card (non-blocking).
# Informational pin lines carry no rule id. Each id is a module-level constant so
# every emission site references the constant, never a raw literal, and RULES
# (what --list-rules prints) cannot drift from what the detector actually emits.
SETTINGS = "tracking.settings"
REMOTE = "tracking.remote"
LABEL_SCHEME = "tracking.label-scheme"
NO_BLOCKED_LABEL = "tracking.no-blocked-label"
ISSUE_BRIEF_SHAPE = "tracking.issue-brief-shape"
EPIC_SHAPE = "tracking.epic-shape"
TUPLE_VALID = "software-factory.tuple-valid"
PIN = "build.pin"

RULES = (
    SETTINGS,
    REMOTE,
    LABEL_SCHEME,
    NO_BLOCKED_LABEL,
    ISSUE_BRIEF_SHAPE,
    EPIC_SHAPE,
    TUPLE_VALID,
    PIN,
)

# The required headings of each brief format, stated here exactly as
# standards/tracking/issues.md states them — the doc and this rule read one
# contract and cannot disagree. A build leaf (mode:sdd, mode:direct) carries all
# six; a spike leaf carries the spike shape.
BUILD_HEADINGS = (
    "Summary",
    "Current behavior",
    "Desired behavior",
    "Key interfaces",
    "Acceptance criteria",
    "Out of scope",
)
SPIKE_HEADINGS = ("Summary", "Question", "Deliverable")

# The four dimensions of the state-machine tuple (status is not part of it).
TUPLE_DIMENSIONS = ("category", "mode", "tests", "phase")

HOOK_REPO_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_CONFIG = (
    HOOK_REPO_ROOT / "standards" / "build" / "canonical" / ".pre-commit-config.yaml"
)

# Expected GitHub settings, as the repos API reports them. The audit only
# reads; the merge settings are set by hand per the repo-settings standard.
EXPECTED_SETTINGS = {
    "allow_squash_merge": True,
    "allow_merge_commit": False,
    "allow_rebase_merge": False,
    "delete_branch_on_merge": True,
    "squash_merge_commit_title": "PR_TITLE",
    "squash_merge_commit_message": "PR_BODY",
}

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
        return self.rule == PIN

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


def workspace_repos(workspace: Path) -> list[Path]:
    """Every git repo directly under ``workspace``, sorted by path."""
    if not workspace.is_dir():
        raise ToolError(f"workspace root not found: {workspace}")
    return sorted(entry for entry in workspace.iterdir() if (entry / ".git").exists())


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


def pinned_rev(config_text: str, url: str) -> str | None:
    """The ``rev`` pinned for ``url`` in a ``.pre-commit-config.yaml`` body, or None."""
    lines = config_text.splitlines()
    for i, line in enumerate(lines):
        if re.match(rf"^\s*-\s*repo:\s*{re.escape(url)}\s*$", line):
            for follower in lines[i + 1 : i + 3]:
                match = re.match(r"^\s*rev:\s*(\S+)", follower)
                if match:
                    return match.group(1)
    return None


def check_pin(repo: Path, url: str, main_sha: str) -> Line | None:
    """One pin line per consumer repo; None for the hook repo itself."""
    if (repo / ".pre-commit-hooks.yaml").is_file():
        return None  # the hook repo dogfoods from its working tree, no pin
    name = repo.name
    config = repo / ".pre-commit-config.yaml"
    if not config.is_file():
        return Line(name, None, "no .pre-commit-config.yaml")
    rev = pinned_rev(config.read_text(encoding="utf-8"), url)
    if rev is None:
        return Line(name, None, "no dev-playbook pin")
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


def fetch_settings(slug: str) -> dict | None:
    """The repo's GitHub settings object, or None when the read is unusable.

    A failed read or a wrong-shaped response (anything but a JSON object)
    degrades to None — the unreachable path — so one malformed response cannot
    abort the whole run.
    """
    data = gh_api(f"repos/{slug}")
    return data if isinstance(data, dict) else None


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


def _has_heading(body: str, heading: str) -> bool:
    """Whether the body carries the bold heading.

    The colon may sit inside or outside the markers — both ``**Heading:**`` and
    ``**Heading**:`` read as present.
    """
    pattern = rf"\*\*\s*{re.escape(heading)}\s*(?:\*\*)?\s*:"
    return re.search(pattern, body, re.IGNORECASE) is not None


def _dimension_values(labels: set[str], dim: str) -> list[str]:
    """The sorted values a label set carries for one ``<dim>:`` prefix."""
    return sorted(
        label.split(":", 1)[1] for label in labels if label.startswith(f"{dim}:")
    )


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
    if mode == "sdd" and tests != "yes":
        lines.append(
            Line(
                name,
                TUPLE_VALID,
                f"#{number} mode:sdd requires tests:yes",
                blocking=True,
            )
        )
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
    elif mode in ("sdd", "direct"):
        required = BUILD_HEADINGS
    else:
        return []  # an unknown mode value is tuple-valid's finding
    return [
        Line(
            name,
            ISSUE_BRIEF_SHAPE,
            f"#{number} missing {heading} heading",
            blocking=True,
        )
        for heading in required
        if not _has_heading(body, heading)
    ]


def check_issues(name: str, issues: list) -> list[Line]:
    """Every open post-intake leaf's four-tuple and brief shape, plus every epic's category-only shape.

    Epic/leaf comes from sub_issues_summary — no per-issue API call. Pull requests
    the issues endpoint returns are skipped.
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
        # GitHub returns sub_issues_summary as null (not absent) for an issue
        # with no children, so `or {}` covers both the missing and null cases.
        total = (issue.get("sub_issues_summary") or {}).get("total", 0)
        if total > 0:
            # An epic (issue with children) carries a category label only — the
            # invariant holds regardless of triage state, so the epic branch is
            # not gated on post-intake (a phase label on an epic is itself a
            # finding).
            lines.extend(_epic_findings(name, number, labels, scheme))
        elif _post_intake(labels):
            # A leaf is checked only once triaged; untriaged leaves are out.
            lines.extend(_tuple_findings(name, number, labels, scheme))
            lines.extend(_brief_findings(name, number, labels, issue.get("body") or ""))
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
        "--list-rules",
        action="store_true",
        help="print the rule ids this detector can emit, one per line, and exit",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--pins-only", action="store_true", help="skip the gh api checks")
    mode.add_argument(
        "--settings-only",
        action="store_true",
        help="run only the settings checks (skip pins and the tracking gh-api checks)",
    )
    args = parser.parse_args(argv)
    if args.list_rules:
        return print_rules(RULES)

    try:
        repos = workspace_repos(args.workspace.resolve())
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
