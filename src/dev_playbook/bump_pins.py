"""Move one consumer repo's dev-playbook pin, or check whether it can move.

The mechanical half of the release described by
[Distribution Channel](/standards/distribution/channel.md), where *the rev bump
is the release*. A consumer runs the standard as of its pinned ``rev`` and
nothing else: a check added upstream, a rule tightened, a canonical artifact
changed, none of it reaches that repo until its pin moves.

The fallout is not mechanical. A bump can newly redden a repo — a check that
never ran there before now runs, a canonical artifact it copies has changed —
and deciding what each finding means is a judgment call. So this tool answers
one question and makes one edit, and stops there:

  ``--check``   Can this repo's pin move to the published head without going red?
  ``--write``   Move it.

``--check`` is a probe: it runs the gate at the current pin, rewrites the pin,
runs the gate again, and puts the config back however that second run went.
Restoring is what lets the caller choose where the durable edit lands — a green
probe can be committed straight to ``main``, while a red one belongs on a branch
where the findings can be worked, and neither choice is made here. The steps,
with the refusal each one carries:

  - **preflight** — the repo is a consumer carrying a dev-playbook pin, sits on
    ``main`` with a clean working tree, and its ``main`` matches ``origin/main``.
    A dirty tree makes the baseline meaningless, and a ``main`` behind the remote
    probes a tree the caller is not about to branch from.
  - **baseline** — the gate is already green at the *current* pin. Bumping a red
    repo makes the new findings indistinguishable from the ones that were
    already there, so a red baseline refuses rather than reporting a verdict
    this release has not earned.
  - **verify** — rewrite the pin and run the gate again. pre-commit clones the
    new rev during this run, so this is both the moment the new standard takes
    effect in that repo and the only step that touches the network. A gate that
    dies rather than judging refuses too: "could not check" reported as "needs
    work" would name a repo for a problem it does not have.

``--write`` makes the durable edit — the one ``rev:`` line, nothing else — and
runs no gate. It asks only for a clean working tree, so it serves the worktree
a caller cuts after a red probe as readily as ``main`` after a green one.

The target is always the hook repo's ``main`` as GitHub has it. pre-commit
installs a pin by fetching that object from the hook repo's URL, so the
published head is the only sha a consumer can pin at all; reading it from the
remote is what makes the pin installable rather than merely recent.

Nothing is committed and nothing is pushed.

Output:
    stdout — the verdict line, then the gate output when the repo goes red.
    stderr — progress, and the refusal when the run cannot proceed.
    exit   — 0 green, written, or already current; 1 needs work; 2 cannot run.
"""

import argparse
import subprocess
import sys
from pathlib import Path

from dev_playbook import gitrepo, workspace_lint
from dev_playbook.workspace_lint import HOOK_REPO_ROOT, ToolError

# The consumer's commit gate, verbatim as the canonical Makefile's `check`
# target spells it. This is the surface the pin controls: every dev-playbook
# check reaches a consumer through pre-commit and nothing else. The repo's
# own mypy/pytest targets are unaffected by the pin and are left to `make check`.
GATE = ("uvx", "pre-commit", "run", "--all-files")

# A cold `uvx` download plus a fresh clone of the new rev plus every hook over
# every file. Generous, because expiry here is a hang, not a slow repo.
GATE_TIMEOUT = 900

# pre-commit's own exit codes: 0 clean, 1 a hook reported findings, 3 an
# internal error, 130 interrupted. Only 0 and 1 are verdicts about the repo.
# Anything else — and either banner pre-commit's error handler prints, which
# covers the internal error it reports as 1 — means the gate never ran, which
# must never be reported as findings.
GATE_VERDICT_CODES = frozenset({0, 1})
GATE_ERROR_BANNERS = ("An error has occurred:", "An unexpected error has occurred:")

CLEAN = "green"
NEEDS_WORK = "needs work"
CURRENT = "already current"


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

    Only a run that reached a verdict returns. A missing runner, a timeout, and
    a pre-commit that died before judging the repo all raise instead, because
    "the gate could not run" and "the gate found something" are different facts
    and reporting the first as the second names a repo for a problem it does not
    have. The verify run at a *new* pin is the one most likely to hit this: it is
    where pre-commit clones the rev, so it is the only step that needs the
    network.
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
    output = result.stdout + result.stderr
    died = result.returncode not in GATE_VERDICT_CODES or any(
        banner in output for banner in GATE_ERROR_BANNERS
    )
    if died:
        raise ToolError(
            f"the gate could not run in {repo} — pre-commit exited "
            f"{result.returncode} without judging it:\n{output}"
        )
    return result.returncode == 0, output


def published_head() -> str:
    """The hook repo's ``main`` head sha, as GitHub has it.

    Read from the remote rather than from the publisher's disk. pre-commit
    installs a pin by fetching that object, so a sha the remote has never seen is
    not stale, it is uninstallable; and a consumer's release should not depend on
    what happens to be checked out elsewhere on the machine.
    """
    slug = workspace_lint.origin_slug(HOOK_REPO_ROOT)
    if slug is None:
        raise ToolError(f"no GitHub origin in {HOOK_REPO_ROOT}")
    match workspace_lint.gh_api(f"repos/{slug}/branches/main"):
        case {"commit": {"sha": str(sha)}}:
            return sha
    raise ToolError(f"cannot read main's head sha from {slug}")


def consumer_root(start: Path) -> Path:
    """The git root holding ``start``, refusing the hook repo itself.

    dev-playbook runs the published hook from its own working tree through its
    ``repo: local`` block, so it carries no pin and there is nothing here to
    move. Identity is the test, exactly as it is in workspace-lint.
    """
    root = Path(git_out(start, "rev-parse", "--show-toplevel"))
    if root.resolve() == HOOK_REPO_ROOT:
        raise ToolError("dev-playbook dogfoods from its working tree and pins nothing")
    return root


def pinned(repo: Path, url: str) -> str:
    """The dev-playbook rev ``repo`` currently pins."""
    config = repo / ".pre-commit-config.yaml"
    if not config.is_file():
        raise ToolError(f"no .pre-commit-config.yaml in {repo}")
    rev = workspace_lint.pinned_rev(config.read_text(encoding="utf-8"), url)
    if rev is None:
        raise ToolError(f"no {url} pin in {repo}; wiring one is adoption, not a bump")
    return rev


def require_clean(repo: Path) -> None:
    """Refuse a repo whose working tree already holds someone's changes."""
    if git_out(repo, "status", "--porcelain"):
        raise ToolError(f"uncommitted changes in {repo}")


def require_fresh_main(repo: Path) -> None:
    """Refuse a repo not sitting on a ``main`` that matches the remote.

    Both halves serve the probe. Off ``main``, or behind it, the gate judges a
    tree that is not the one the caller will commit to or branch from, so a
    verdict about this release would be a verdict about something else.
    """
    branch = git_out(repo, "branch", "--show-current")
    if branch != "main":
        raise ToolError(f"{repo} is on {branch}; the baseline is only honest on main")
    if git_out(repo, "rev-parse", "main") != git_out(repo, "rev-parse", "origin/main"):
        raise ToolError(f"main in {repo} is not at origin/main; fast-forward it first")


def check(repo: Path, url: str, sha: str) -> int:
    """Probe the bump and restore the config; the exit code is the verdict."""
    require_fresh_main(repo)
    require_clean(repo)
    old = pinned(repo, url)
    if old == sha:
        print(f"{repo.name}: {CURRENT} ({sha[:12]})")
        return 0

    config = repo / ".pre-commit-config.yaml"
    text = config.read_text(encoding="utf-8")
    print(f"bump-pin: {repo.name}: checking baseline at {old[:12]}", file=sys.stderr)
    baseline_ok, baseline_output = run_gate(repo)
    if not baseline_ok:
        raise ToolError(
            f"{repo.name} is already red at its current pin ({old[:12]}), so these "
            f"findings are not this release's:\n{baseline_output}"
        )

    updated, _ = rewritten(text, url, sha)
    config.write_text(updated, encoding="utf-8")
    print(
        f"bump-pin: {repo.name}: {old[:12]} -> {sha[:12]}, verifying", file=sys.stderr
    )
    try:
        passed, output = run_gate(repo)
    finally:
        # However the verify run went — verdict, crash, interrupt — the tree goes
        # back exactly as found. The caller has yet to decide where the durable
        # edit lands, and an uncommitted pin sitting in main is not a tree anyone
        # can branch cleanly from.
        config.write_text(text, encoding="utf-8")

    if passed:
        print(f"{repo.name}: {CLEAN} at {sha[:12]}")
        return 0
    print(f"{repo.name}: {NEEDS_WORK} at {sha[:12]}\n\n{output}")
    return 1


def write(repo: Path, url: str, sha: str) -> int:
    """Move the pin for real, running no gate."""
    require_clean(repo)
    old = pinned(repo, url)
    if old == sha:
        print(f"{repo.name}: {CURRENT} ({sha[:12]})")
        return 0
    config = repo / ".pre-commit-config.yaml"
    updated, _ = rewritten(config.read_text(encoding="utf-8"), url, sha)
    config.write_text(updated, encoding="utf-8")
    print(f"{repo.name}: pinned {old[:12]} -> {sha[:12]}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """The ``bump-pin`` command-line entry point.

    Returns the process exit code: 0 green, written, or already current; 1 the
    repo needs work at the new pin; 2 the run could not reach a verdict.
    """
    parser = argparse.ArgumentParser(
        prog="bump-pin",
        description=(
            "Check whether one consumer repo's dev-playbook pin can move to the "
            "published head, or move it. Commits nothing."
        ),
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--check",
        action="store_true",
        help="probe the bump, restore the config, and report the verdict",
    )
    mode.add_argument(
        "--write",
        action="store_true",
        help="rewrite the rev line, running no gate",
    )
    parser.add_argument(
        "repo",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="the consumer repo (default: the repo the working directory sits in)",
    )
    args = parser.parse_args(argv)

    try:
        repo = consumer_root(args.repo)
        url = workspace_lint.hook_repo_url()
        sha = published_head()
        print(f"bump-pin: target {sha}", file=sys.stderr)
        return check(repo, url, sha) if args.check else write(repo, url, sha)
    except ToolError as err:
        print(f"bump-pin: {err}", file=sys.stderr)
        return 2
