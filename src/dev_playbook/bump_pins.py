"""Move the dev-playbook pin across the governed consumer repos.

The library behind the ``bump-pins`` shim — the release step of
[distribution.md](/standards/build/distribution.md), where *the rev bump is the
release*. A consumer runs the standard as of its pinned ``rev`` and nothing
else: a detector added upstream, a rule tightened, a canonical artifact
changed, none of it reaches that repo until its pin moves. Moving the pin is
therefore the whole delivery mechanism, and it is mechanical.

The fallout is not mechanical. A bump can newly redden a repo — a detector that
never ran there before now runs, a canonical artifact it copies has changed —
and deciding what each finding means is a judgment call per repo. So this tool
owns the mechanical half end to end and stops at the report: it resolves the
target sha, refuses one GitHub has never seen, rewrites each pin, and re-runs
each consumer's commit gate. Fixing what the gate says belongs to whoever reads
the output.

Per repo, in order, with the refusal each step carries:

  - **preflight** — the repo sits on ``main`` with a clean working tree. A dirty
    tree holds someone else's uncommitted work, and this tool would bury its own
    one-line change inside it.
  - **baseline** — the commit gate is already green at the *current* pin.
    Bumping a red repo makes the new findings indistinguishable from the ones
    that were already there, so a red baseline is reported and the pin is left
    alone.
  - **bump** — rewrite the one ``rev:`` line. Nothing else in the config moves.
  - **verify** — run the commit gate again. pre-commit clones the new rev during
    this run, so this is the moment the new standard takes effect in that repo.

Nothing is committed and nothing is pushed. The bumped config and whatever the
gate found are left in the working tree for review.

The audited population is ``workspace_lint.GOVERNED``, read from there rather
than restated, so the roster stays declared in exactly one place.

Output:
    stdout — one ``repo: status`` line per repo, then each red repo's gate output.
    stderr — per-repo progress and one summary line.
    exit   — 0 every repo green at the new pin, 1 some repo needs work,
             2 cannot run.
"""

import argparse
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from dev_playbook import gitrepo, workspace_lint
from dev_playbook.workspace_lint import GOVERNED, HOOK_REPO_ROOT, ToolError

# The consumer's commit gate, verbatim as the canonical Makefile's `check`
# target spells it. This is the surface the pin controls: every dev-playbook
# detector reaches a consumer through pre-commit and nothing else. The repo's
# own mypy/pytest targets are unaffected by the pin and are left to `make check`.
GATE = ("uvx", "pre-commit", "run", "--all-files")

# A cold `uvx` download plus a fresh clone of the new rev plus every hook over
# every file. Generous, because expiry here is a hang, not a slow repo.
GATE_TIMEOUT = 900

CLEAN = "green"
NEEDS_WORK = "needs work"
CURRENT = "already current"
DIRTY = "skipped — uncommitted changes"
OFF_MAIN = "skipped — not on main"
RED_BASELINE = "skipped — already red at its current pin"
NO_PIN = "skipped — no dev-playbook pin"


@dataclass(frozen=True)
class Outcome:
    """What happened to one consumer repo."""

    repo: str
    status: str
    detail: str = ""
    gate_output: str = ""
    # Whether this repo ends the run needing a human or an agent to act on it.
    open_work: bool = False

    def render(self) -> str:
        """The one-line verdict, ``repo: status`` with any detail appended."""
        suffix = f" ({self.detail})" if self.detail else ""
        return f"{self.repo}: {self.status}{suffix}"


@dataclass
class Plan:
    """The resolved inputs one run operates on."""

    sha: str
    url: str
    repos: list[Path] = field(default_factory=list)


def git_out(repo: Path, *args: str) -> str:
    """One read-only git command's stdout in ``repo``, stripped.

    Raises ToolError rather than returning a sentinel: every caller here is
    asking a question whose unanswerability means the run cannot continue.
    """
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        env=gitrepo.no_git_env(),
    )
    if result.returncode != 0:
        raise ToolError(
            f"git {' '.join(args)} failed in {repo}: {result.stderr.strip()}"
        )
    return result.stdout.strip()


def rewritten(text: str, url: str, sha: str) -> tuple[str, str]:
    """``text`` with ``url``'s pin moved to ``sha``, and the rev it replaced.

    Only the one ``rev:`` line changes — its indentation is preserved and every
    other byte of the config, including the trailing newline, is carried through
    untouched. A config with no such pin raises rather than growing one: adding a
    dev-playbook block to a repo is adoption, a different act from a bump.
    """
    lines = text.splitlines()
    index = workspace_lint.rev_line(lines, url)
    if index is None:
        raise ToolError(f"no {url} pin to move")
    line = lines[index]
    old = line.split(":", 1)[1].strip()
    indent = line[: len(line) - len(line.lstrip())]
    lines[index] = f"{indent}rev: {sha}"
    tail = "\n" if text.endswith("\n") else ""
    return "\n".join(lines) + tail, old


def run_gate(repo: Path) -> tuple[bool, str]:
    """The commit gate's (passed, combined output) for one repo.

    A timeout is a tool error, not a red gate: an expired run has produced no
    verdict, and reporting one would be a guess.
    """
    try:
        result = subprocess.run(
            GATE,
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=GATE_TIMEOUT,
        )
    except FileNotFoundError as err:
        raise ToolError(f"{GATE[0]} not found on PATH") from err
    except subprocess.TimeoutExpired as err:
        raise ToolError(
            f"the gate did not finish in {GATE_TIMEOUT}s in {repo}"
        ) from err
    return result.returncode == 0, result.stdout + result.stderr


def resolve(workspace: Path, roster: tuple[str, ...], sha: str | None) -> Plan:
    """The target sha, the hook-repo URL, and the consumer repos to visit.

    The sha must exist on the remote before anything downstream can use it:
    pre-commit installs a pin by fetching that object from the hook repo's URL,
    so a pin at a local-only commit is not stale, it is uninstallable. Checking
    it here turns a confusing fetch failure inside pre-commit into one refusal
    naming the cause.
    """
    url = workspace_lint.hook_repo_url()
    target = sha or workspace_lint.hook_repo_main()
    slug = workspace_lint.origin_slug(HOOK_REPO_ROOT)
    if slug is None:
        raise ToolError(f"no GitHub origin in {HOOK_REPO_ROOT}; cannot verify {target}")
    if workspace_lint.gh_api(f"repos/{slug}/commits/{target}") is None:
        raise ToolError(
            f"{target} is not on {slug}; push dev-playbook before bumping consumers"
        )
    repos = [
        repo
        for repo in workspace_lint.workspace_repos(workspace, roster)
        if repo.resolve() != HOOK_REPO_ROOT
    ]
    return Plan(sha=target, url=url, repos=repos)


def preflight(repo: Path, url: str, sha: str) -> Outcome | None:
    """The reason this repo is not bumpable, or None when it is.

    Every refusal is a skip rather than an abort: one repo mid-review must not
    cost the sweep the repos that are ready.
    """
    name = repo.name
    branch = git_out(repo, "branch", "--show-current")
    if branch != "main":
        return Outcome(name, OFF_MAIN, f"on {branch}")
    if git_out(repo, "status", "--porcelain"):
        return Outcome(name, DIRTY)
    config = repo / ".pre-commit-config.yaml"
    if not config.is_file():
        return Outcome(name, NO_PIN, "no .pre-commit-config.yaml", open_work=True)
    pinned = workspace_lint.pinned_rev(config.read_text(encoding="utf-8"), url)
    if pinned is None:
        return Outcome(name, NO_PIN, open_work=True)
    if pinned == sha:
        return Outcome(name, CURRENT)
    return None


def bump(repo: Path, plan: Plan, *, dry_run: bool) -> Outcome:
    """One consumer repo through the whole sequence, reported as one outcome."""
    name = repo.name
    skip = preflight(repo, plan.url, plan.sha)
    if skip is not None:
        return skip

    config = repo / ".pre-commit-config.yaml"
    text = config.read_text(encoding="utf-8")
    updated, old = rewritten(text, plan.url, plan.sha)
    move = f"{old[:12]} -> {plan.sha[:12]}"
    if dry_run:
        return Outcome(name, "would bump", move)

    print(f"bump-pins: {name}: checking baseline at {old[:12]}", file=sys.stderr)
    baseline_ok, baseline_output = run_gate(repo)
    if not baseline_ok:
        return Outcome(name, RED_BASELINE, old[:12], baseline_output, open_work=True)

    config.write_text(updated, encoding="utf-8")
    print(f"bump-pins: {name}: {move}, verifying", file=sys.stderr)
    passed, output = run_gate(repo)
    if passed:
        return Outcome(name, CLEAN, move)
    return Outcome(name, NEEDS_WORK, move, output, open_work=True)


def main(argv: list[str] | None = None) -> int:
    """The ``bump-pins`` command-line entry point.

    Returns the process exit code: 0 every repo green at the new pin, 1 some
    repo needs work, 2 cannot run.
    """
    parser = argparse.ArgumentParser(
        prog="bump-pins",
        description=(
            "Move the dev-playbook rev pin in each governed consumer repo and "
            "re-run its commit gate. Commits nothing."
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
        help="comma-separated repo names to bump (default: the governed roster)",
    )
    parser.add_argument(
        "--sha",
        help="the rev to pin (default: the hook repo's local main)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="report the moves and skips without writing or running any gate",
    )
    args = parser.parse_args(argv)

    try:
        plan = resolve(args.workspace.resolve(), args.repos, args.sha)
        print(f"bump-pins: target {plan.sha}", file=sys.stderr)
        outcomes = [bump(repo, plan, dry_run=args.dry_run) for repo in plan.repos]
    except ToolError as err:
        print(f"bump-pins: {err}", file=sys.stderr)
        return 2

    for outcome in outcomes:
        print(outcome.render())
    for outcome in outcomes:
        if outcome.gate_output:
            print(f"\n--- {outcome.repo} ---\n{outcome.gate_output}")

    open_work = sum(1 for outcome in outcomes if outcome.open_work)
    print(
        f"bump-pins: {len(outcomes)} consumer(s), {open_work} needing work",
        file=sys.stderr,
    )
    return 1 if open_work else 0
