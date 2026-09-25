"""The ``playbook`` console script: ``check`` runs the checks, ``checks`` lists them.

``playbook check [DIR]`` builds the model once, loads dev-playbook's checks,
runs every check function, prints each finding in GNU format with its rule
id, then runs the one step that is not a function over the model:
``pre-commit validate-manifest`` where the repo publishes a
``.pre-commit-hooks.yaml``. Over dev-playbook, whose checks are its own, the
layer test runs first.

``playbook check --local [DIR]`` runs a consumer repo's own layer instead:
the checks it hosts in ``src/<package>/checks/``, after the layer test holds
them and the repo's Standards together, and no steps. The two runs are the
consumer's two hooks. The pinned ``playbook-check`` runs in the environment
pre-commit builds for dev-playbook, which holds nothing of the consumer's;
the consumer's ``playbook-check-local`` runs ``--local`` in the consumer's
own environment, so its checks can import its package and its dependencies.

Either run exits 1 on any finding, 2 when the model or the checks cannot be
loaded, the layer test fails, or a step cannot run. ``--without TAG`` leaves
out the checks tagged as needing that environment, and says so on stderr on
every run, so a skip never goes silent. ``SKIP``, the variable pre-commit
reads for hook ids, is read here for tag names too: ``SKIP=workspace`` is
``--without workspace``, so a CI file leaves the tagged checks out with the
one variable it already sets, and pre-commit ignores a name that is no hook
id of its own.

``playbook checks [DIR]`` prints the registry: id, module, and the hook or
tag, computed live, of dev-playbook's layer, or with ``--local`` of the
repo's. ``--family`` and ``--without`` filter it.
"""

import argparse
import os
import subprocess
import sys
import tomllib
from pathlib import Path

from dev_playbook import check_registry, findings
from dev_playbook.model import ModelError, Repo

MANIFEST = ".pre-commit-hooks.yaml"

LOCAL_HELP = "run the repo's own checks, in src/<package>/checks/, instead"


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
    run.add_argument("--local", action="store_true", help=LOCAL_HELP)
    run.add_argument(
        "--without",
        action="append",
        default=[],
        metavar="TAG",
        help="leave out checks that need this environment",
    )

    listing = commands.add_parser("checks", help="list the registered checks")
    listing.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="repository whose checks to list (default: current directory)",
    )
    listing.add_argument("--local", action="store_true", help=LOCAL_HELP)
    listing.add_argument("--family", help="only this family")
    listing.add_argument(
        "--without",
        action="append",
        default=[],
        metavar="TAG",
        help="leave out checks that need this environment",
    )

    args = parser.parse_args(argv)
    root = Path(args.directory).resolve()
    if args.command == "check":
        without = frozenset(args.without) | skipped_tags()
        return run_check(root, args.local, without)
    return list_checks(root, args.local, args.family, frozenset(args.without))


def skipped_tags() -> frozenset[str]:
    """The environment tags ``SKIP`` names, each one a ``--without``."""
    names = {name.strip() for name in os.environ.get("SKIP", "").split(",")}
    return frozenset({check_registry.WORKSPACE} & names)


def selected(
    registry: dict[str, check_registry.Check],
    without: frozenset[str],
    family: str | None = None,
) -> list[check_registry.Check]:
    """The registered checks in id order, minus the filtered ones."""
    return [
        c
        for c in sorted(registry.values(), key=lambda c: c.id)
        if not (c.needs & without) and (family is None or c.family == family)
    ]


class CannotLoad(Exception):
    """The model or the checks cannot be loaded; each arg is one line to print."""


def load(root: Path, local: bool) -> tuple[Repo, dict[str, check_registry.Check]]:
    """The model of ``root`` and the layer of checks one run runs.

    Without ``local``, dev-playbook's layer, and over dev-playbook the layer
    test with it. With ``local``, the layer ``root`` hosts, after the layer
    test. Raises :class:`CannotLoad` when the model cannot be built, ``local``
    names dev-playbook itself, a module of the
    repo's checks cannot run or register, or the layer test fails
    (:func:`check_registry.layer_problems`).
    """
    try:
        repo = Repo.from_git(root)
    except (ModelError, subprocess.CalledProcessError) as err:
        raise CannotLoad(f"cannot build the model: {err}") from err
    try:
        package = check_registry.import_package(repo)
        if not local:
            registry = dict(check_registry.load())
            if package == "dev_playbook":
                check_layer(registry, repo)
            return repo, registry
        if package == "dev_playbook":
            raise CannotLoad(
                "--local runs a consumer repo's own checks; dev-playbook's "
                "checks are its own, so they run without --local"
            )
        both = check_registry.load(repo)
    except (
        check_registry.RegistryError,
        tomllib.TOMLDecodeError,
        SyntaxError,
        ImportError,
    ) as err:
        raise CannotLoad(f"cannot load {repo.name}'s checks: {err}") from err
    check_layer(both, repo)
    layer = {
        id: c
        for id, c in both.items()
        if package is not None and c.module.startswith(f"{package}.checks.")
    }
    return repo, layer


def check_layer(registry: dict[str, check_registry.Check], repo: Repo) -> None:
    """Raise :class:`CannotLoad` naming each place the layer test fails."""
    if problems := check_registry.layer_problems(registry, repo):
        raise CannotLoad(*problems)


def cannot_load(command: str, err: CannotLoad) -> int:
    """Print why ``command`` cannot run; return 2, its exit code."""
    for line in err.args:
        print(f"{command}: {line}", file=sys.stderr)
    return 2


def run_check(root: Path, local: bool, without: frozenset[str]) -> int:
    """Build the model and run one layer, then the two steps; exit 0, 1, or 2.

    The steps run with dev-playbook's layer only, so a consumer runs each
    once, in its pinned hook.
    """
    try:
        repo, registry = load(root, local)
    except CannotLoad as err:
        return cannot_load("playbook check", err)
    if without:
        print(
            f"playbook check: without {', '.join(sorted(without))}, the checks "
            "tagged so are left out",
            file=sys.stderr,
        )
    enabled = [c for c in selected(registry, without) if c.function is not None]
    count = 0
    for c in enabled:
        assert c.function is not None
        for f in sorted(c.function(repo), key=lambda f: (f.path, f.line or 0)):
            print(findings.render(f.path, c.id, f.message, f.line))
            count += 1
    sys.stdout.flush()
    print(
        f"playbook check: {len(enabled)} {'local ' if local else ''}check(s) over "
        f"{len(repo.files)} files, {count} finding(s)",
        file=sys.stderr,
    )
    if local:
        return 1 if count else 0
    steps: list[int] = []
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


def list_checks(
    root: Path, local: bool, family: str | None, without: frozenset[str]
) -> int:
    """Print one line per check of one layer: id, module, and its hook or tags."""
    try:
        _, registry = load(root, local)
    except CannotLoad as err:
        return cannot_load("playbook checks", err)
    for c in selected(registry, without, family):
        how = c.hook if c.hook else ",".join(sorted(c.needs)) or "-"
        print(f"{c.id}\t{c.module}\t{how}")
    return 0
