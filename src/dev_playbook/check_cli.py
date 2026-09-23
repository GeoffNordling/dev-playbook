"""The ``playbook`` console script: ``check`` runs the checks, ``checks`` lists them.

``playbook check [DIR]`` builds the model once, runs every registered check
function, prints each finding in GNU format with its rule id, then runs the
two steps that are not functions over the model: the loop family's
``loop_lint`` module, kept whole for the loop workstream, and ``pre-commit
validate-manifest`` where the repo publishes a ``.pre-commit-hooks.yaml``.
It exits 1 on any finding, 2 when the model cannot be built or a step cannot
run. ``--without TAG`` leaves out the checks tagged as needing that
environment, and says so on stderr on every run, so a skip never goes
silent. ``SKIP``, the variable pre-commit reads for hook ids, is read
here for tag names too: ``SKIP=workspace`` is ``--without workspace``, so a
CI file leaves the tagged checks out with the one variable it already sets,
and pre-commit ignores a name that is no hook id of its own.

``playbook checks`` prints the registry: id, module, and the hook or tag,
computed live. ``--family`` and ``--without`` filter it.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from dev_playbook import check_registry, findings, loop_lint
from dev_playbook.model import ModelError, Repo

MANIFEST = ".pre-commit-hooks.yaml"


def main(argv: list[str] | None = None) -> int:
    """Run one subcommand; return its exit code."""
    parser = argparse.ArgumentParser(prog="playbook")
    commands = parser.add_subparsers(dest="command", required=True)

    run = commands.add_parser("check", help="run every check over a repository")
    run.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="repository root to check (default: current directory)",
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
        without = frozenset(args.without) | skipped_tags()
        return run_check(Path(args.directory).resolve(), without)
    return list_checks(args.family, frozenset(args.without))


def skipped_tags() -> frozenset[str]:
    """The environment tags ``SKIP`` names, each one a ``--without``."""
    names = {name.strip() for name in os.environ.get("SKIP", "").split(",")}
    return frozenset({check_registry.WORKSPACE} & names)


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
    """Build the model, run the checks and the two steps; exit 0, 1, or 2."""
    try:
        repo = Repo.from_git(root)
    except (ModelError, subprocess.CalledProcessError) as err:
        print(f"playbook check: cannot build the model: {err}", file=sys.stderr)
        return 2
    if without:
        print(
            f"playbook check: without {', '.join(sorted(without))}, the checks "
            "tagged so are left out",
            file=sys.stderr,
        )
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
    steps = [loop_lint.main([str(root)])]
    if (root / MANIFEST).is_file():
        steps.append(validate_manifest(root / MANIFEST))
    if 2 in steps:
        return 2
    return 1 if count or 1 in steps else 0


def validate_manifest(manifest: Path) -> int:
    """Run ``pre-commit validate-manifest`` over ``manifest``; 2 when it cannot run."""
    argv = ["uvx", "pre-commit", "validate-manifest", str(manifest)]
    try:
        return subprocess.run(argv, check=False).returncode
    except OSError as err:
        print(f"playbook check: cannot run {argv[0]}: {err}", file=sys.stderr)
        return 2


def list_checks(family: str | None, without: frozenset[str]) -> int:
    """Print one line per check: id, module, and its hook or tags."""
    for c in selected(without, family):
        how = c.hook if c.hook else ",".join(sorted(c.needs)) or "-"
        print(f"{c.id}\t{c.module}\t{how}")
    return 0
