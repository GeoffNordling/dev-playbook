"""The ``playbook`` console script: ``check`` runs the checks, ``checks`` lists them.

``playbook check [DIR]`` builds the model once, runs every registered check
function, prints each finding in GNU format with its rule id, and exits 1 on
any finding, 2 when the model cannot be built. ``--without TAG`` leaves out
the checks tagged as needing that environment; CI runs
``playbook check --without workspace``.

``playbook checks`` prints the registry: id, module, and the hook or tag,
computed live. ``--family`` and ``--without`` filter it.
"""

import argparse
import subprocess
import sys
from pathlib import Path

from dev_playbook import check_registry, findings
from dev_playbook.model import ModelError, Repo


def main(argv: list[str] | None = None) -> int:
    """Run one subcommand; return its exit code."""
    parser = argparse.ArgumentParser(prog="playbook")
    commands = parser.add_subparsers(dest="command", required=True)

    run = commands.add_parser("check", help="run every check over a repository")
    run.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="repository root to audit (default: current directory)",
    )
    run.add_argument(
        "--without",
        action="append",
        default=[],
        metavar="TAG",
        help="leave out checks that need this environment",
    )

    listing = commands.add_parser("checks", help="list the registered checks")
    listing.add_argument("--family", help="only this family")
    listing.add_argument(
        "--without",
        action="append",
        default=[],
        metavar="TAG",
        help="leave out checks that need this environment",
    )

    args = parser.parse_args(argv)
    if args.command == "check":
        return run_check(Path(args.directory).resolve(), frozenset(args.without))
    return list_checks(args.family, frozenset(args.without))


def selected(
    without: frozenset[str], family: str | None = None
) -> list[check_registry.Check]:
    """The registered checks in id order, minus the filtered ones."""
    return [
        c
        for c in sorted(check_registry.load().values(), key=lambda c: c.id)
        if not (c.needs & without) and (family is None or c.family == family)
    ]


def run_check(root: Path, without: frozenset[str]) -> int:
    """Build the model, run the checks, print the findings; exit 0, 1, or 2."""
    try:
        repo = Repo.from_git(root)
    except (ModelError, subprocess.CalledProcessError) as err:
        print(f"playbook check: cannot build the model: {err}", file=sys.stderr)
        return 2
    enabled = [c for c in selected(without) if c.function is not None]
    count = 0
    for c in enabled:
        assert c.function is not None
        for f in sorted(c.function(repo), key=lambda f: (f.path, f.line or 0)):
            print(findings.render(f.path, c.id, f.message, f.line))
            count += 1
    sys.stdout.flush()
    print(
        f"playbook check: {len(enabled)} check(s) over {len(repo.files)} files, "
        f"{count} finding(s)",
        file=sys.stderr,
    )
    return 1 if count else 0


def list_checks(family: str | None, without: frozenset[str]) -> int:
    """Print one line per check: id, module, and its hook or tags."""
    for c in selected(without, family):
        how = c.hook if c.hook else ",".join(sorted(c.needs)) or "-"
        print(f"{c.id}\t{c.module}\t{how}")
    return 0
