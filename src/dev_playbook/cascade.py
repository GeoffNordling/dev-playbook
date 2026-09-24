"""Move every governed consumer's dev-playbook pin to the release head, and record the run.

The fan-out half of the release described by
[Distribution Channel](/standards/distribution/channel.md). ``bump-pin`` moves
one repo's pin and stops at the verdict; this command walks the ``GOVERNED``
roster, lands each verdict, and writes one row per repo into the ledger. A
systemd user timer on the publishing machine runs it every fifteen minutes,
and the command itself decides whether there is anything to do, so the timer
needs no poller in front of it.

**The trigger is a repo without a ledger row at the release head.** The
release head is the newest commit on dev-playbook ``main`` that is not the
ledger's own bookkeeping (``workspace_lint.release_head``). For every governed
repo on this machine the ledger is searched for a row at that head; a repo
that has one, whatever its verdict, is done for this release, and a run in
which every repo has one prints one line and exits. So a fresh release moves
every repo once, a repo the last run could not finish is not retried until the
next release or a hand run of ``bump-pin``, and a ``--repos`` subset leaves the
rest to the next tick rather than marking them done.

**Per repo, in roster order, one at a time** — pre-commit's clone cache holds
one global lock — the run is:

  - ``git fetch --prune origin``, then read the pin on ``origin/main``; a pin
    already at the release head is the row ``current``.
  - Report every remote branch with commits not on ``origin/main``: name,
    last-commit date, commits ahead. The cascade bumps ``main`` regardless of
    in-flight work — a branch meets the new pin when it merges, on its own PR —
    and the report is how the user spots a live branch and vetoes. Merged
    branches nobody deleted are not in it.
  - Probe in a throwaway worktree of ``origin/main``: rewrite the pin and the
    hook ids, run the gate once. No baseline run: the question is "green at
    the new pin", and every finding at that pin is worked, whichever release
    brought it.
  - **Green**: commit the one-file change in the worktree and push it to
    ``main``. The consumer's commit hook runs the gate at the new pin and its
    pre-push hook runs ``make check``, so a landed commit is verified twice. A
    rejected push is the row ``failed`` with git's reason, never a retry.
  - **Red**: cut a persistent worktree at
    ``<repo>/.claude/worktrees/bump-pin-<sha12>`` on a branch of the same
    name, commit the pin there with ``--no-verify``, and hand it to a headless
    Claude — ``claude -p`` on Opus, ``--permission-mode bypassPermissions`` —
    with a prompt that names the state, orders the findings worked per the
    ``update-standards-pin`` skill, and ends in ``gh pr create``. Nothing the
    agent prints is trusted: the row is ``red`` with the PR's URL read back
    from ``gh pr list --head``, or ``failed`` naming the kept worktree when no
    PR exists afterwards. A PR already open on that branch is the row
    ``pending`` and no agent runs. The agent's transcript goes to
    ``~/.local/state/dev-playbook/cascade/<run>/<repo>.log``.

**Nothing here merges anything.** The agent is told so in its prompt, and the
cascade reads back a PR, never a merge.

**Billing.** A headless run must draw from the subscription
([Headless Operation](/docs/headless.md)), and any credential variable in the
environment outranks the login silently. The cascade refuses to launch the
agent while one is set, as a ``failed`` row, rather than scrub it: an
unexplained variable on the publishing machine is a fact to surface, not to
work around.

**The ledger.** ``docs/pin-cascade.md`` in dev-playbook, a ``Log`` whose last
section is one table: time, release head, repo, verdict, landing, notes. Rows
are appended and committed in a throwaway worktree of dev-playbook's
``origin/main`` and pushed to ``main``, so a run never touches the checkout the
command runs from and the history reads in ``git log`` and the IDE. The commit
changes the ledger alone, which is what lets ``release_head`` step over it.

``--dry-run`` probes and reports, and lands nothing: no push, no worktree, no
agent, no ledger row. It reads the ledger if there is one and treats a missing
ledger as empty, so the first run can be watched before this module is
published.

Output:
    stdout — one line per repo as it is decided, then the rows written.
    stderr — progress, and the refusal when the run cannot start.
    exit   — 0 nothing to do or every row landed; 1 a ``failed`` row; 2 cannot run.
"""

import argparse
import datetime
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from dev_playbook import bump_pins, workspace_lint
from dev_playbook.bump_pins import git_out, probe_worktree, rewritten, run_gate
from dev_playbook.workspace_lint import (
    GOVERNED,
    LEDGER,
    ToolError,
    hook_repo_slug,
    hook_repo_url,
    is_hook_repo,
    published_file,
    published_hook_ids,
    release_head,
    workspace_repos,
)

# The headless agent and the GitHub CLI, as tuples so a test can point each at
# a script; ``bump_pins.GATE`` is the same shape for the same reason.
CLAUDE = ("claude",)
GH = ("gh",)
AGENT_MODEL = "opus"
AGENT_EFFORT = "high"
# Working a red repo to green is reading standards, editing, and running the
# gate repeatedly; an hour is generous, and expiry is a hang, not slow work.
AGENT_TIMEOUT = 3600

STATE_DIR = Path.home() / ".local" / "state" / "dev-playbook" / "cascade"
WORKTREES = Path(".claude") / "worktrees"

# A branch whose last commit is this recent reads as live in the report.
LIVE_DAYS = 14

# The variables that move a headless run off the subscription, from
# docs/headless.md § Billing. ``CLAUDE_CODE_OAUTH_TOKEN`` is not among them: it
# is a subscription credential.
METERED_VARS = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_BASE_URL",
    "CLAUDE_CODE_USE_BEDROCK",
    "CLAUDE_CODE_USE_VERTEX",
    "CLAUDE_CODE_USE_FOUNDRY",
    "ANTHROPIC_PROFILE",
    "ANTHROPIC_FEDERATION_RULE_ID",
    "ANTHROPIC_ORGANIZATION_ID",
)

CURRENT = "current"
GREEN = "green"
RED = "red"
PENDING = "pending"
FAILED = "failed"

LEDGER_HEADER = "| Time (UTC) | Release head | Repo | Verdict | Landing | Notes |"
LEDGER_RULE = "|---|---|---|---|---|---|"

SKILL = (
    "~/workspace/dev-playbook/dotfiles/dot-claude/skills/update-standards-pin/SKILL.md"
)


@dataclass(frozen=True)
class Branch:
    """One remote branch carrying commits ``origin/main`` does not have."""

    name: str
    date: str
    ahead: int

    def render(self) -> str:
        """``name (date, n ahead)``."""
        return f"{self.name} ({self.date}, {self.ahead} ahead)"


@dataclass(frozen=True)
class Row:
    """One ledger row: one repo's outcome at one release head in one run."""

    time: str
    head: str
    repo: str
    verdict: str
    landing: str
    notes: str

    def render(self) -> str:
        """The row as the ledger table carries it."""
        cells = (
            self.time,
            self.head[:12],
            self.repo,
            self.verdict,
            self.landing,
            self.notes,
        )
        return "| " + " | ".join(cell.replace("|", "/") for cell in cells) + " |"


# --- the ledger ---


def ledger_rows(text: str) -> list[tuple[str, ...]]:
    """The cells of every data row in the ledger's table, in file order."""
    rows = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = tuple(cell.strip() for cell in stripped.strip("|").split("|"))
        if cells[:2] == ("Time (UTC)", "Release head") or set(cells[0]) <= {"-"}:
            continue
        rows.append(cells)
    return rows


def recorded(text: str, head: str) -> set[str]:
    """The repos the ledger already carries a row for at ``head``."""
    return {cells[2] for cells in ledger_rows(text) if head.startswith(cells[1])}


def published_ledger(*, required: bool) -> str:
    """The ledger as dev-playbook's ``main`` has it, or empty when absent and not required."""
    text = published_file(hook_repo_slug(), LEDGER)
    if text is None:
        if required:
            raise ToolError(
                f"no {LEDGER} on {hook_repo_slug()} main; the cascade records "
                "into that file and cannot run without it"
            )
        return ""
    return text


def record(rows: list[Row], hook_repo: Path | None = None) -> str:
    """Append ``rows`` to the ledger on dev-playbook ``origin/main`` and push; the commit sha.

    In a throwaway worktree, so the checkout this command runs from — the
    timer's main checkout, or a session's worktree — is never written. The
    commit touches the ledger alone: that is the property ``release_head``
    relies on to step over it.
    """
    repo = hook_repo if hook_repo is not None else workspace_lint.HOOK_REPO_ROOT
    bump_pins.fetch_origin(repo)
    with probe_worktree(repo) as tree:
        ledger = tree / LEDGER
        if not ledger.is_file():
            raise ToolError(f"no {LEDGER} in {repo} at origin/main")
        text = ledger.read_text(encoding="utf-8")
        if not text.endswith("\n"):
            text += "\n"
        ledger.write_text(
            text + "".join(row.render() + "\n" for row in rows), encoding="utf-8"
        )
        git_out(tree, "add", LEDGER)
        heads = sorted({row.head[:12] for row in rows})
        git_out(
            tree,
            "commit",
            "-q",
            "-m",
            f"Pin cascade: {len(rows)} row(s) at {', '.join(heads)}",
        )
        sha = git_out(tree, "rev-parse", "HEAD")
        git_out(tree, "push", "-q", "origin", "HEAD:main")
    return sha


# --- reading one consumer ---


def fetch_all(repo: Path) -> None:
    """Every remote branch, pruned: the report and the probe both read ``origin/*``."""
    git_out(repo, "fetch", "-q", "--prune", "origin")


def pinned_on_main(repo: Path, url: str) -> str:
    """The dev-playbook rev ``origin/main`` pins, refusing a tree with no pin."""
    result = subprocess.run(
        ["git", "-C", str(repo), "show", "origin/main:.pre-commit-config.yaml"],
        capture_output=True,
        text=True,
        env=bump_pins.gitrepo.no_git_env(),
    )
    if result.returncode != 0:
        raise ToolError("no .pre-commit-config.yaml on origin/main")
    rev = workspace_lint.pinned_rev(result.stdout, url)
    if rev is None:
        raise ToolError(f"no {url} pin on origin/main; wiring one is adoption")
    return rev


def unmerged_branches(repo: Path) -> list[Branch]:
    """Every ``origin/*`` branch with commits not on ``origin/main``, newest first.

    ``origin/HEAD`` is a pointer and ``origin/main`` is the base, so neither is
    a branch here. A branch fully merged reads as zero ahead and is left out:
    it is history, and the cascade's question is what is still in flight.
    """
    listing = git_out(
        repo,
        "for-each-ref",
        "--format=%(refname:short)%09%(committerdate:short)",
        "refs/remotes/origin/",
    )
    branches = []
    for line in listing.splitlines():
        name, _, date = line.partition("\t")
        if name in ("origin/HEAD", "origin/main"):
            continue
        ahead = int(git_out(repo, "rev-list", "--count", f"origin/main..{name}"))
        if ahead:
            branches.append(Branch(name.removeprefix("origin/"), date, ahead))
    return sorted(branches, key=lambda branch: branch.date, reverse=True)


def branch_notes(branches: list[Branch]) -> str:
    """The unmerged-branch report as one ledger cell."""
    if not branches:
        return "no unmerged branches"
    return "unmerged: " + "; ".join(branch.render() for branch in branches)


# --- landing ---


def land_green(tree: Path, old: str, sha: str) -> str:
    """Commit the moved pin in the probe worktree and push it to ``main``; the new sha.

    Hooks run: the consumer's commit hook is the gate at the new pin, its
    pre-push hook is ``make check``, and a rejection from either is the caller's
    ``failed`` row. The worktree is throwaway, so the commit's home is
    ``origin/main`` or nowhere.
    """
    git_out(tree, "add", ".pre-commit-config.yaml")
    git_out(
        tree,
        "commit",
        "-q",
        "-m",
        f"Pin dev-playbook at {sha[:12]}\n\n"
        f"The pin cascade moved the standards pin {old[:12]} -> {sha[:12]}; "
        "the gate is green at the new pin.",
    )
    landed = git_out(tree, "rev-parse", "HEAD")
    git_out(tree, "push", "-q", "origin", "HEAD:main")
    return landed


def branch_name(sha: str) -> str:
    """``bump-pin-<sha12>``: the branch and worktree name for one release."""
    return f"bump-pin-{sha[:12]}"


def red_worktree(
    repo: Path, url: str, sha: str, ids: tuple[str, ...]
) -> tuple[Path, str]:
    """A persistent worktree on ``bump-pin-<sha12>`` holding the moved pin; path and old rev.

    Cut from ``origin/main``, which is the tree the probe judged, so the
    findings reproduce there exactly. The pin is committed with ``--no-verify``
    because the gate is known red; the agent's last commit runs it. A worktree
    or branch already there is refused rather than reused: it belongs to an
    earlier run that did not finish, and its state is the user's to read.
    """
    branch = branch_name(sha)
    path = repo / WORKTREES / branch
    if path.exists():
        raise ToolError(f"worktree {path} already exists, kept from an earlier run")
    path.parent.mkdir(parents=True, exist_ok=True)
    git_out(repo, "worktree", "add", "-q", "-b", branch, str(path), "origin/main")
    config = path / ".pre-commit-config.yaml"
    updated, old = rewritten(config.read_text(encoding="utf-8"), url, sha, ids)
    config.write_text(updated, encoding="utf-8")
    git_out(path, "add", ".pre-commit-config.yaml")
    git_out(
        path,
        "commit",
        "-q",
        "--no-verify",
        "-m",
        f"Pin dev-playbook at {sha[:12]}\n\n"
        f"The pin cascade moved the standards pin {old[:12]} -> {sha[:12]}; "
        "the gate is red at the new pin and the findings follow.",
    )
    return path, old


def open_pr(repo: Path, branch: str) -> str | None:
    """The URL of the open PR whose head is ``branch``, or None.

    Read from GitHub, never from what an agent printed: the PR is the one fact
    about a red repo the ledger records, so it comes from the system of record.
    """
    try:
        result = subprocess.run(
            [
                *GH,
                "pr",
                "list",
                "--head",
                branch,
                "--state",
                "open",
                "--json",
                "url",
                "--jq",
                ".[0].url // empty",
            ],
            cwd=repo,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as err:
        raise ToolError(f"{GH[0]} not found on PATH") from err
    if result.returncode != 0:
        raise ToolError(f"gh pr list --head {branch} failed: {result.stderr.strip()}")
    url = result.stdout.strip()
    return url or None


def agent_prompt(
    repo: str,
    worktree: Path,
    branch: str,
    old: str,
    sha: str,
    ids: tuple[str, ...],
    branches: list[Branch],
    findings: str,
) -> str:
    """The task the headless agent is handed for one red repo."""
    report = "\n".join(f"- {branch.render()}" for branch in branches) or "- none"
    return f"""You are the pin-cascade agent for the consumer repo {repo}. No user is present: every decision is yours, nothing you print is read, and your result is the pull request you open, which the cascade reads back with `gh pr list --head {branch}`.

State: the working directory is the worktree {worktree} on branch {branch}, cut from origin/main. Its last commit moves the dev-playbook pin in .pre-commit-config.yaml from {old} to {sha} and sets its hook ids to {", ".join(ids)}. At that pin the gate `uvx pre-commit run --all-files` is red; its output is at the end of this prompt.

Do, in order:

1. Read the skill at {SKILL} and follow its sections 6 and 7 here, in this worktree: work every finding to an empty gate, taking each fix from the rule the finding names rather than from the check's message, and commit as you go with --no-verify.
2. Make the last commit without --no-verify, so the commit gate runs at the new pin and its green result is the verification.
3. Push the branch: `git push -u origin {branch}`. If the push is rejected because the token cannot write .github/workflows, stop and print the rejection verbatim: the user widens the token by hand.
4. Open the PR: `gh pr create --base main --head {branch}` with the title "Pin dev-playbook at {sha[:12]}" and a body that names the sha move {old[:12]} -> {sha[:12]}, each adaptation and the rule it serves, whether .github/workflows/ci.yml changed, and this list of remote branches not merged to main as of this run:

{report}

Never merge the PR, approve it, or enable auto-merge; the user merges every PR by hand.

Where a fix would change what the repo does rather than how it conforms — deleting a file whose content has no obvious new home, renaming something other tooling may reference — do not decide it: finish everything else, open the PR anyway, and list each open choice in the PR body under a heading "Escalations".

Gate output at {sha[:12]}:

{findings}
"""


def require_subscription_billing() -> None:
    """Refuse to launch the agent while a metered credential would outrank the login."""
    present = [name for name in METERED_VARS if os.environ.get(name)]
    if present:
        raise ToolError(
            f"{', '.join(present)} set in the environment; a headless run would "
            "bill the metered API instead of the subscription (docs/headless.md)"
        )


def run_agent(worktree: Path, prompt: str, log: Path) -> None:
    """Run the headless agent in ``worktree``, its whole output to ``log``.

    The exit code is not the verdict — the PR's existence is — so a non-zero
    exit is recorded in the log and nothing more. A timeout is a refusal: an
    agent still running after an hour is not working the findings.
    """
    require_subscription_billing()
    log.parent.mkdir(parents=True, exist_ok=True)
    argv = [
        *CLAUDE,
        "-p",
        prompt,
        "--model",
        AGENT_MODEL,
        "--effort",
        AGENT_EFFORT,
        "--permission-mode",
        "bypassPermissions",
        "--output-format",
        "json",
    ]
    with log.open("w", encoding="utf-8") as sink:
        try:
            result = subprocess.run(
                argv,
                cwd=worktree,
                stdout=sink,
                stderr=subprocess.STDOUT,
                timeout=AGENT_TIMEOUT,
            )
        except FileNotFoundError as err:
            raise ToolError(f"{CLAUDE[0]} not found on PATH") from err
        except subprocess.TimeoutExpired as err:
            raise ToolError(
                f"the agent did not finish in {AGENT_TIMEOUT}s; its log is {log}"
            ) from err
        sink.write(f"\n[cascade] claude exited {result.returncode}\n")


# --- one repo ---


def cascade_repo(
    repo: Path,
    url: str,
    sha: str,
    ids: tuple[str, ...],
    *,
    now: str,
    run_dir: Path,
    dry_run: bool,
) -> Row:
    """One governed repo's row at release head ``sha``.

    Every refusal below the fetch becomes a ``failed`` row rather than ending
    the run, so one repo's trouble never stops the others from being moved.
    """
    name = repo.name
    try:
        fetch_all(repo)
        old = pinned_on_main(repo, url)
        notes = branch_notes(unmerged_branches(repo))
        if old == sha:
            return Row(now, sha, name, CURRENT, f"main pins {sha[:12]}", notes)

        branch = branch_name(sha)
        already = open_pr(repo, branch)
        if already is not None:
            return Row(now, sha, name, PENDING, f"PR {already}", notes)

        print(f"cascade: {name}: {old[:12]} -> {sha[:12]}, probing", file=sys.stderr)
        with probe_worktree(repo) as tree:
            config = tree / ".pre-commit-config.yaml"
            updated, _ = rewritten(config.read_text(encoding="utf-8"), url, sha, ids)
            config.write_text(updated, encoding="utf-8")
            passed, output = run_gate(tree)
            if passed and not dry_run:
                landed = land_green(tree, old, sha)
                return Row(now, sha, name, GREEN, f"main {landed[:12]}", notes)
        if passed:
            return Row(now, sha, name, GREEN, "dry run: not landed", notes)

        findings = run_dir / f"{name}.findings.txt"
        findings.parent.mkdir(parents=True, exist_ok=True)
        findings.write_text(output, encoding="utf-8")
        if dry_run:
            print(output)
            return Row(now, sha, name, RED, "dry run: no branch cut", notes)

        worktree, old = red_worktree(repo, url, sha, ids)
        branches = unmerged_branches(repo)
        prompt = agent_prompt(name, worktree, branch, old, sha, ids, branches, output)
        run_agent(worktree, prompt, run_dir / f"{name}.log")
        pr = open_pr(repo, branch)
        if pr is None:
            raise ToolError(
                f"the agent opened no PR; worktree kept at {worktree}, "
                f"log at {run_dir / f'{name}.log'}"
            )
        return Row(now, sha, name, RED, f"PR {pr}", notes)
    except ToolError as err:
        return Row(now, sha, name, FAILED, str(err).replace("\n", " "), "")


# --- the run ---


def main(argv: list[str] | None = None) -> int:
    """The ``cascade`` command-line entry point.

    Returns the process exit code: 0 nothing to do or every row landed; 1 a
    row failed; 2 the run could not start.
    """
    parser = argparse.ArgumentParser(
        prog="cascade",
        description=(
            "Move every governed repo's dev-playbook pin to the release head, "
            "landing green on main and red on a PR, and record the run in the ledger."
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
        help="comma-separated repo names (default: the governed roster)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="probe and report; push nothing, cut nothing, run no agent, record nothing",
    )
    args = parser.parse_args(argv)

    started = datetime.datetime.now(datetime.UTC)
    now = started.strftime("%Y-%m-%d %H:%M")
    run_dir = STATE_DIR / started.strftime("%Y%m%dT%H%M%SZ")

    try:
        repos, absent = workspace_repos(args.workspace.resolve(), args.repos)
        workspace_lint.check_auth()
        url = hook_repo_url()
        sha = release_head()
        ids = published_hook_ids(sha)
        ledger = published_ledger(required=not args.dry_run)
    except ToolError as err:
        print(f"cascade: {err}", file=sys.stderr)
        return 2

    done = recorded(ledger, sha)
    consumers = [repo for repo in repos if not is_hook_repo(repo)]
    todo = [repo for repo in consumers if repo.name not in done]
    if absent:
        print(
            f"cascade: not on this machine, not moved: {', '.join(absent)}",
            file=sys.stderr,
        )
    if not todo:
        print(f"cascade: every repo recorded at {sha[:12]}; nothing to do")
        return 0

    print(
        f"cascade: release head {sha[:12]} ({', '.join(ids)}); "
        f"{len(todo)} repo(s) to move" + (" [dry run]" if args.dry_run else ""),
        file=sys.stderr,
    )
    rows = []
    for repo in todo:
        row = cascade_repo(
            repo, url, sha, ids, now=now, run_dir=run_dir, dry_run=args.dry_run
        )
        print(f"{row.repo}: {row.verdict} — {row.landing}")
        if row.notes and row.notes != "no unmerged branches":
            print(f"  {row.notes}")
        rows.append(row)

    if args.dry_run:
        print("cascade: dry run, nothing recorded", file=sys.stderr)
    else:
        try:
            commit = record(rows)
            print(f"cascade: {len(rows)} row(s) recorded in {LEDGER} at {commit[:12]}")
        except ToolError as err:
            print(f"cascade: rows landed but not recorded: {err}", file=sys.stderr)
            for row in rows:
                print(row.render(), file=sys.stderr)
            return 1
    return 1 if any(row.verdict == FAILED for row in rows) else 0
