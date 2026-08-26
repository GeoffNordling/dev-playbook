"""Run every commit-gate detector from the one published hook.

The published manifest carries a single hook id, ``playbook-lint``, and the
roster below — shipped inside the pinned clone — decides what runs. The
roster is the enrollment: a detector added to it reaches every consumer at
that consumer's next pin bump, with no edit to any consumer's config.

Dispatch runs the detectors concurrently (each is an independent read-only
scan) and prints their output buffered, in roster order, so runs are
deterministic. Each detector keeps its own contract — findings to stdout one
per line, a summary to stderr, exit 0/1/2 — and this hook aggregates: exit 2
if any detector could not run, else 1 if any found findings, else 0.

``$SKIP`` is honored per detector name, announced on stderr. pre-commit's own
``SKIP`` keys on config hook ids, and no config hook id names a detector, so
a per-detector skip can only happen here (the canonical CI workflow skips
``ref-lint``). Names matching no roster entry are left alone: the variable is
shared vocabulary with pre-commit, which still reads it for the hooks outside
this one (shellcheck, ruff).
"""

import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from dev_playbook import gitrepo

# The dev-playbook checkout this module ships in — the pre-commit clone at the
# consumer's pinned rev, or the working tree when dev-playbook dogfoods it.
HOOK_REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = HOOK_REPO_ROOT / "scripts"

# The commit-gate roster: every detector the published hook runs, in output
# order. Each name is an executable ``scripts/<name>`` in this clone. Adding a
# detector here IS enrolling it workspace-wide — there is no per-consumer step.
DETECTORS = (
    "repo-lint",
    "python-lint",
    "testing-lint",
    "ref-lint",
    "okf-lint",
    "decisions-lint",
    "harness-files-lint",
    "judgments-lint",
    "prose-lint",
    "standards-lint",
)

# Audit scripts a card's Audit cell may cite that deliberately run outside the
# commit gate (enforcement.md — outside the gates). standards-lint's
# hook-surfaces closure accepts these as cited-but-unenrolled; anything else
# cited and missing from DETECTORS is an enrollment hole.
UNGATED_AUDITS = frozenset({"workspace-lint"})

# Manifest validation is not a scripts/ detector — it delegates to pre-commit's
# own validator and applies only where a repo publishes a manifest — so it
# joins the run as a conditional extra step, not a DETECTORS entry.
VALIDATE_MANIFEST = "validate-manifest"
MANIFEST = ".pre-commit-hooks.yaml"


@dataclass(frozen=True)
class DetectorResult:
    """One detector's captured run: exit code plus verbatim stdout/stderr."""

    name: str
    returncode: int
    stdout: str
    stderr: str


def _argv_for(name: str, root: Path) -> list[str]:
    if name == VALIDATE_MANIFEST:
        return ["uvx", "pre-commit", "validate-manifest", str(root / MANIFEST)]
    return [str(SCRIPTS_DIR / name), str(root)]


def _run_one(name: str, root: Path) -> DetectorResult:
    """One detector's captured run; a spawn failure is a loud tool error.

    The commit gate is a git hook, so an absolute ``GIT_DIR`` may be ambient;
    ``gitrepo.no_git_env()`` scrubs the repository-locating variables so each
    detector's git calls answer for the repo it was handed, not the hook's.
    """
    argv = _argv_for(name, root)
    try:
        proc = subprocess.run(
            argv, capture_output=True, text=True, env=gitrepo.no_git_env()
        )
    except OSError as err:
        return DetectorResult(
            name, 2, "", f"playbook-lint: cannot run {argv[0]}: {err}\n"
        )
    return DetectorResult(name, proc.returncode, proc.stdout, proc.stderr)


def main(argv: list[str] | None = None) -> int:
    """Dispatch the roster over the audited repo; return the aggregate exit."""
    parser = argparse.ArgumentParser(
        prog="playbook-lint",
        description="Run every commit-gate detector over a repository.",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="repository root to audit (default: current directory)",
    )
    args = parser.parse_args(argv)
    root = Path(args.directory).resolve()

    roster = list(DETECTORS)
    if (root / MANIFEST).is_file():
        roster.append(VALIDATE_MANIFEST)

    skip = {name.strip() for name in os.environ.get("SKIP", "").split(",")}
    for name in (n for n in roster if n in skip):
        print(f"playbook-lint: {name} skipped (SKIP)", file=sys.stderr)
    to_run = [name for name in roster if name not in skip]
    if not to_run:
        print("playbook-lint: every detector skipped", file=sys.stderr)
        return 0

    workers = min(len(to_run), os.process_cpu_count() or 1)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(partial(_run_one, root=root), to_run))

    # Findings first, then the summaries, each stream whole and flushed before
    # the next: the two streams are buffered differently once redirected, so
    # writing them per detector would let a pipe reorder findings after the
    # roll-up that describes them.
    for result in results:
        sys.stdout.write(result.stdout)
    sys.stdout.flush()
    for result in results:
        sys.stderr.write(result.stderr)

    errored = [r.name for r in results if r.returncode not in (0, 1)]
    red = [r.name for r in results if r.returncode == 1]
    if errored:
        print(f"playbook-lint: could not run: {', '.join(errored)}", file=sys.stderr)
        return 2
    if red:
        print(f"playbook-lint: findings from: {', '.join(red)}", file=sys.stderr)
        return 1
    print(f"playbook-lint: {len(results)} detector(s) clean", file=sys.stderr)
    return 0
