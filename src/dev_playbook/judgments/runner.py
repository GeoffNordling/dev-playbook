"""The judgments-run CLI: deterministic plan / render / record over declarations.

Every subcommand reads the repo's declarations through the loader and drives the
two already-built dependencies -- ``judgments.core.prepare`` (claim + files +
bench -> content key and judge prompt) and the ``skipcache`` seen-set. No
LLM, no network: this is the deterministic half the judge skill stands on.

- ``plan``  -- key every judgment, partition by cache membership, emit one JSON
  object ``{cli, schema, seen_count, unseen}`` with ``unseen`` ordered by id.
- ``render <id>`` -- print exactly the judge prompt for one judgment.
- ``record <id>...`` -- record the passing judgments' keys idempotently.
- ``--root <path>`` -- name the repo root explicitly instead of resolving it from
  the current directory, so a fully-specified command works from anywhere.
- ``--list-rules`` -- print nothing and exit 0: this CLI records passing verdicts
  but emits no findings, so it answers the detector protocol with an empty rule set.
"""

import argparse
import json
import sys
from pathlib import Path

from dev_playbook.findings import print_rules
from dev_playbook.judgments.core import SCHEMA, Prepared, prepare
from dev_playbook.judgments.loader import Declaration, by_id, load, resolve_root
from dev_playbook.skipcache import seen

_DISPATCH_PROMPT = (
    "Run this exact command: {cli} render {id}\n"
    "Its stdout is your complete instructions and the material to judge -- follow "
    "it and return your verdict. The command is absolute and needs no PATH lookup, "
    "no virtualenv activation, and no particular working directory; run it "
    "verbatim and do not substitute a shorter spelling."
)


def invocation(root: Path) -> str:
    """The absolute, fully-specified command that re-invokes this CLI over ``root``.

    Judge agents are handed this string inside their prompt and consumers append a
    subcommand to it. It names the running interpreter by absolute path and reaches
    the CLI as a module, so it resolves without a PATH lookup, without an activated
    virtualenv, and without ``uv run`` -- the three ways a bare ``judgments-run``
    has been observed to fail in a worktree. ``--root`` is baked in for the same
    reason: the command must not depend on the caller's working directory. The root
    only locates files and never enters a content key, so naming it explicitly
    cannot change a verdict's identity.
    """
    return f"{sys.executable} -m dev_playbook.judgments.runner --root {root}"


def plan(declarations: list[Declaration], root: Path | None) -> dict[str, object]:
    """Partition by cache membership into a ``{cli, schema, seen_count, unseen}``.

    ``seen_count`` is how many judgments are already cached -- a count, not a list,
    because no caller needs the ids and every one of them costs an orchestrating
    agent context. ``unseen`` is the sorted-by-id list of ``{id, model, effort,
    prompt}`` the judge skill must still run -- each a ready-to-dispatch job whose
    ``prompt`` bootstraps a judge agent. ``cli`` is the absolute invocation a caller
    appends ``record <id>...`` to, so it never has to spell the command itself.
    """
    keyed = [(d, _prepared(d, root)) for d in declarations]
    cached = set(seen.filter([prepared.key for _, prepared in keyed]).seen)
    resolved = root if root is not None else Path.cwd()
    cli = invocation(resolved)
    unseen = sorted(
        (
            {
                "id": d.id,
                "model": d.model,
                "effort": d.effort,
                "prompt": _DISPATCH_PROMPT.format(cli=cli, id=d.id),
            }
            for d, prepared in keyed
            if prepared.key not in cached
        ),
        key=lambda entry: entry["id"],
    )
    seen_count = sum(1 for _, prepared in keyed if prepared.key in cached)
    return {
        "cli": cli,
        "schema": SCHEMA,
        "seen_count": seen_count,
        "unseen": unseen,
    }


def render_prompt(declaration: Declaration, root: Path | None) -> str:
    """The judge prompt for one judgment -- the XML input a judge agent runs."""
    return _prepared(declaration, root).prompt


def record(declarations: list[Declaration], root: Path | None) -> None:
    """Record the given judgments' content keys in the seen-set, idempotently."""
    seen.record([_prepared(d, root).key for d in declarations])


def _prepared(declaration: Declaration, root: Path | None) -> Prepared:
    """Key-and-prompt one declaration; a declaration implies a resolved root."""
    assert root is not None  # declarations exist only under a resolved root
    return prepare(
        declaration.claim,
        declaration.evidence,
        declaration.reference,
        declaration.model,
        declaration.effort,
        root,
    )


def run_cli() -> int:
    """Console-script entry point: run the CLI over this process's own argv.

    Registered as the ``judgments-run`` console script and called by the
    ``scripts/judgments-run`` pre-commit shim, so both channels run the same
    ``main`` over ``sys.argv``.
    """
    return main(sys.argv[1:])


def main(argv: list[str]) -> int:
    """Parse the subcommand, load declarations, and run it; nonzero on any error."""
    args = _parse_args(argv)
    if args.list_rules:
        return print_rules(())
    if args.command is None:
        print("judgments-run: a subcommand is required", file=sys.stderr)
        return 2
    # An explicit --root wins over the walk-up search, so a command generated for
    # a judge agent runs identically from any working directory.
    root: Path | None
    if args.root is not None:
        root = Path(args.root)
        if not (root / "pyproject.toml").is_file():
            print(
                f"judgments-run: --root {args.root!r} has no pyproject.toml",
                file=sys.stderr,
            )
            return 1
    else:
        root = resolve_root()
    try:
        declarations = load(root)
        if args.command == "plan":
            print(json.dumps(plan(declarations, root)))
        elif args.command == "render":
            print(render_prompt(by_id(declarations, args.id), root))
        elif args.command == "record":
            if not args.ids:
                print(
                    "judgments-run record: at least one id is required",
                    file=sys.stderr,
                )
                return 2
            record([by_id(declarations, id) for id in args.ids], root)
    except (ValueError, OSError) as error:
        print(f"judgments-run: {error}", file=sys.stderr)
        return 1
    return 0


def _parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse ``--list-rules`` or the plan / render / record subcommand.

    ``--list-rules`` is a top-level flag so the detector answers it with no
    repository and no subcommand (format.md §Detectors); the subparser is
    therefore optional, and a bare invocation with neither is an error.
    """
    parser = argparse.ArgumentParser(
        prog="judgments-run",
        description="Deterministic plan/render/record over judgment declarations.",
    )
    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="print the rule ids this detector can emit, one per line, and exit",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="repo root to operate on (default: resolve it from the current directory)",
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("plan", help="emit {schema, seen, unseen} as JSON")
    render_parser = sub.add_parser("render", help="print one judgment's judge prompt")
    render_parser.add_argument("id", help="the judgment id to render")
    record_parser = sub.add_parser("record", help="record verdicts over judgments")
    record_parser.add_argument(
        "ids", nargs="*", help="the passing judgment ids to record"
    )
    return parser.parse_args(argv)


# Makes `python -m dev_playbook.judgments.runner` a first-class entry point, which
# is the spelling invocation() hands to judge agents: it needs only an interpreter
# that can import the package, never a console script on PATH.
if __name__ == "__main__":  # pragma: no cover - exercised as a subprocess
    sys.exit(run_cli())
