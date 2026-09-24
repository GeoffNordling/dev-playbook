"""Move every governed consumer's dev-playbook pin to the release head, and record the run.

``bump-pin`` moves one repo's pin and stops at the verdict; this command walks
the ``GOVERNED`` roster, lands each verdict, and writes one row per repo into
the ledger. A systemd user timer on the publishing machine runs it every
fifteen minutes, and the command itself decides whether there is anything to
do, so the timer needs no poller in front of it.

**The trigger is a repo without a ledger row at the release head.** For every
governed repo on this machine the ledger is searched for a row at that head; a
repo that has one, whatever its verdict, is done for this release, and a run in
which every repo has one prints one line and exits. So a fresh release moves
every repo once, a repo the last run could not finish is not retried until the
next release or a hand run of ``bump-pin``, and a ``--repos`` subset leaves the
rest to the next tick rather than marking them done.

**Per repo, in roster order, one at a time** — pre-commit's clone cache holds
one global lock — the run is:

  - Fetch, then read the pin on ``origin/main``; a pin already at the release
    head is the row ``current``. A PR already open on ``bump-pin-<sha12>`` is
    the row ``pending`` and nothing runs.
  - Report every remote branch with commits not on ``origin/main``. ``main``
    is bumped regardless of in-flight work — a branch meets the new pin when
    it merges, on its own PR — and the report is how the user spots a live
    branch and vetoes.
  - Probe in a throwaway worktree of ``origin/main``: rewrite the pin and the
    hook ids, run the gate once. No baseline run: the question is "green at
    the new pin", and every finding at that pin is worked, whichever release
    brought it.
  - **Green**: commit the one-file change and push it to ``main``. The
    consumer's commit hook runs the gate at the new pin and its pre-push hook
    runs ``make check``, so a landed commit is verified twice. A rejected push
    is the row ``failed`` with git's reason, never a retry.
  - **Red**: cut the persistent worktree, hand it to the headless agent
    (``agent``), and read the PR back from GitHub: the row is ``red`` with the
    PR's URL, or ``failed`` naming the kept worktree when no PR exists
    afterwards.

**Nothing here merges anything.** The skill the agent runs says so, and this
command reads back a PR, never a merge.

**Every run sweeps first.** A red repo's worktree and branch outlive the run
that cut them: the PR is merged or closed hours later, by the user, when no
process of ours is in that repo. So each run opens by asking GitHub, for every
``bump-pin-*`` branch in every governed repo, whether its PR is finished, and
removes the worktree, the local branch and the remote branch of each one that
is. An open PR, or a branch with no PR yet, is kept. Nothing else in the repo
is touched, and the sweep is reported on stdout, not in the ledger.

``--dry-run`` probes and reports, and lands nothing: no push, no worktree, no
agent, no ledger row. It treats a missing ledger as empty, so the first run can
be watched before the ledger is published.

**The package.** This is the top of ``dev_playbook.pins``, the distribution
channel's tooling — everything that reads, moves, and records a consumer's
pin, and nothing that checks a repo. The modules underneath, one concern each:

  - ``release`` — the hook repo as GitHub publishes it: its URL, its release
    head, the manifest at a sha, a file on ``main``.
  - ``config`` — a consumer's pinned block: locate the ``rev`` line, read the
    rev and hook ids, rewrite both.
  - ``gate`` — the consumer's commit gate, run to a verdict or a refusal.
  - ``worktree`` — git in a consumer: one command, a fetch, a throwaway
    detached worktree of ``origin/main``.
  - ``consumer`` — one consumer's state and landings: the pin on
    ``origin/main``, its unmerged branches, the green commit, the red
    worktree on ``bump-pin-<sha12>``.
  - ``ledger`` — the record of every run, appended to dev-playbook ``main``.
  - ``agent`` — the headless Claude a red repo is handed to, and the PR read
    back from GitHub afterwards.
  - ``bump`` — the ``bump-pin`` command: one consumer, probe or write.

Output:
    stdout — one line per repo as it is decided, then the rows written.
    stderr — progress, and the refusal when the run cannot start.
    exit   — 0 nothing to do or every row landed; 1 a ``failed`` row; 2 cannot run.
"""

import argparse
import datetime
import sys
from pathlib import Path

from dev_playbook.errors import ToolError
from dev_playbook.github import check_auth
from dev_playbook.pins import agent, consumer, ledger
from dev_playbook.pins.config import rewritten
from dev_playbook.pins.gate import run_gate
from dev_playbook.pins.release import (
    LEDGER,
    hook_repo_url,
    is_hook_repo,
    published_hook_ids,
    release_head,
)
from dev_playbook.pins.worktree import fetch_all, probe_worktree
from dev_playbook.workspace_lint import GOVERNED, workspace_repos

STATE_DIR = Path.home() / ".local" / "state" / "dev-playbook" / "update-pins"

CURRENT = "current"
GREEN = "green"
RED = "red"
PENDING = "pending"
FAILED = "failed"

FINISHED = ("MERGED", "CLOSED")


def sweep(repo: Path, *, dry_run: bool) -> list[str]:
    """Remove every bump whose PR is finished; ``branch (state)`` for each one.

    Under ``dry_run`` the list is what would be removed, and nothing is.
    """
    swept = []
    for branch in consumer.bump_branches(repo):
        state = agent.pr_state(repo, branch)
        if state not in FINISHED:
            continue
        if not dry_run:
            consumer.remove_bump(repo, branch)
        swept.append(f"{branch} ({state.lower()})")
    return swept


def update_repo(
    repo: Path,
    url: str,
    sha: str,
    ids: tuple[str, ...],
    *,
    now: str,
    run_dir: Path,
    dry_run: bool,
) -> ledger.Row:
    """One governed repo's row at release head ``sha``.

    Every refusal below the fetch becomes a ``failed`` row rather than ending
    the run, so one repo's trouble never stops the others from being moved.
    """
    name = repo.name
    try:
        fetch_all(repo)
        old = consumer.pinned_on_main(repo, url)
        branches = consumer.unmerged_branches(repo)
        notes = consumer.branch_notes(branches)
        if old == sha:
            return ledger.Row(now, sha, name, CURRENT, f"main pins {sha[:12]}", notes)

        branch = consumer.branch_name(sha)
        already = agent.open_pr(repo, branch)
        if already is not None:
            return ledger.Row(now, sha, name, PENDING, f"PR {already}", notes)

        print(
            f"update-pins: {name}: {old[:12]} -> {sha[:12]}, probing", file=sys.stderr
        )
        with probe_worktree(repo) as tree:
            config = tree / ".pre-commit-config.yaml"
            updated, _ = rewritten(config.read_text(encoding="utf-8"), url, sha, ids)
            config.write_text(updated, encoding="utf-8")
            passed, output = run_gate(tree)
            if passed and not dry_run:
                landed = consumer.land_green(tree, old, sha)
                return ledger.Row(now, sha, name, GREEN, f"main {landed[:12]}", notes)
        if passed:
            return ledger.Row(now, sha, name, GREEN, "dry run: not landed", notes)

        findings = run_dir / f"{name}.findings.txt"
        findings.parent.mkdir(parents=True, exist_ok=True)
        findings.write_text(output, encoding="utf-8")
        if dry_run:
            print(output)
            return ledger.Row(now, sha, name, RED, "dry run: no branch cut", notes)

        worktree, old = consumer.red_worktree(repo, url, sha, ids)
        task = agent.prompt(name, worktree, branch, old, sha, ids, branches, output)
        log = run_dir / f"{name}.log"
        agent.run(worktree, task, log)
        pr = agent.open_pr(repo, branch)
        if pr is None:
            raise ToolError(
                f"the agent opened no PR; worktree kept at {worktree}, log at {log}"
            )
        return ledger.Row(now, sha, name, RED, f"PR {pr}", notes)
    except ToolError as err:
        return ledger.Row(now, sha, name, FAILED, str(err).replace("\n", " "), "")


def main(argv: list[str] | None = None) -> int:
    """The ``update-pins`` command-line entry point.

    Returns the process exit code: 0 nothing to do or every row landed; 1 a
    row failed; 2 the run could not start.
    """
    parser = argparse.ArgumentParser(
        prog="update-pins",
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
        check_auth()
        url = hook_repo_url()
        sha = release_head()
        ids = published_hook_ids(sha)
        text = ledger.published(required=not args.dry_run)
    except ToolError as err:
        print(f"update-pins: {err}", file=sys.stderr)
        return 2

    done = ledger.recorded(text, sha)
    consumers = [repo for repo in repos if not is_hook_repo(repo)]
    verb = "would sweep" if args.dry_run else "swept"
    for repo in consumers:
        try:
            for entry in sweep(repo, dry_run=args.dry_run):
                print(f"{repo.name}: {verb} {entry}")
        except ToolError as err:
            print(f"update-pins: {repo.name}: sweep: {err}", file=sys.stderr)
    todo = [repo for repo in consumers if repo.name not in done]
    if absent:
        print(
            f"update-pins: not on this machine, not moved: {', '.join(absent)}",
            file=sys.stderr,
        )
    if not todo:
        print(f"update-pins: every repo recorded at {sha[:12]}; nothing to do")
        return 0

    print(
        f"update-pins: release head {sha[:12]} ({', '.join(ids)}); "
        f"{len(todo)} repo(s) to move" + (" [dry run]" if args.dry_run else ""),
        file=sys.stderr,
    )
    rows = []
    for repo in todo:
        row = update_repo(
            repo, url, sha, ids, now=now, run_dir=run_dir, dry_run=args.dry_run
        )
        print(f"{row.repo}: {row.verdict} — {row.landing}")
        if row.notes and row.notes != "no unmerged branches":
            print(f"  {row.notes}")
        rows.append(row)

    if args.dry_run:
        print("update-pins: dry run, nothing recorded", file=sys.stderr)
    else:
        try:
            commit = ledger.record(rows)
            print(
                f"update-pins: {len(rows)} row(s) recorded in {LEDGER} at {commit[:12]}"
            )
        except ToolError as err:
            print(f"update-pins: rows landed but not recorded: {err}", file=sys.stderr)
            for row in rows:
                print(row.render(), file=sys.stderr)
            return 1
    return 1 if any(row.verdict == FAILED for row in rows) else 0
