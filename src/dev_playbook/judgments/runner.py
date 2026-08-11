"""The judgments-run CLI: deterministic plan / render / record over declarations.

Every subcommand reads the repo's declarations through the loader and drives the
two already-built dependencies -- ``judgments.core.prepare`` (claim + files +
bench -> content key and judge prompt) and the ``skipcache`` seen-set. No
LLM, no network: this is the deterministic half the judge skill stands on.

- ``plan`` -- key every judgment across one or more roots, partition by cache
  membership, and emit the ``judgments`` workflow's entire argument payload as
  one JSON object. The orchestrating agent copies that object into its
  ``Workflow`` call verbatim; it never parses, reshapes, or composes anything,
  so no model stands between the cache and the fan-out. :func:`plan` documents
  the fields.
- ``render <id>`` -- print exactly the judge prompt for one judgment.
- ``record <id>...`` -- record the passing judgments' keys idempotently.
- ``--root <path>`` -- name a repo root explicitly instead of resolving it from
  the current directory, so a fully-specified command works from anywhere.
  ``plan`` accepts it repeated and sweeps every named root in one docket;
  ``render`` and ``record`` take at most one.
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

# The judge prompt is one template for the whole run rather than one copy per
# judgment: the only parts that vary are the invocation, the root, and the id,
# and repeating the rest across a docket of judgments would multiply the payload
# the orchestrating agent carries by roughly ten for nothing. The three
# placeholders are the substitution points, and the workflow fills them per job
# -- the wording stays here, with the CLI whose contract it describes, instead
# of being re-authored in JavaScript.
CLI_PLACEHOLDER = "{cli}"
ROOT_PLACEHOLDER = "{root}"
ID_PLACEHOLDER = "{id}"

_JUDGE_PROMPT_TAIL = (
    "Its stdout is your complete instructions and the material to judge -- follow "
    "it and return your verdict. The command is absolute and needs no PATH lookup, "
    "no virtualenv activation, and no particular working directory; run it "
    "verbatim and do not substitute a shorter spelling."
)


def invocation() -> str:
    """The absolute command that re-invokes this CLI, with no root baked in.

    Judge agents are handed this string inside their prompt and consumers append
    ``--root`` and a subcommand to it. It names the running interpreter by
    absolute path and reaches the CLI as a module, so it resolves without a PATH
    lookup, without an activated virtualenv, and without ``uv run`` -- the three
    ways a bare ``judgments-run`` has been observed to fail in a worktree. One
    invocation serves every root in a plan because ``--root`` is what retargets
    it; the root only locates files and never enters a content key, so
    retargeting cannot change a verdict's identity.
    """
    return f"{sys.executable} -m dev_playbook.judgments.runner"


def judge_prompt() -> str:
    """The judge-bootstrap prompt template, placeholders marking the moving parts.

    A judge is told to run one command and obey its stdout; that stdout -- the
    claim plus the full text of every evidence file -- is produced by ``render``
    inside the judge's own context, so the heavy bytes never cross the workflow
    script or the orchestrating agent's window. The workflow substitutes each
    job's invocation, root, and id at the three placeholders; the assembled
    command must not depend on the judge's working directory, which is why the
    template spells out an explicit ``--root``.
    """
    return (
        f"Run this exact command: {CLI_PLACEHOLDER} --root {ROOT_PLACEHOLDER} "
        f"render {ID_PLACEHOLDER}\n{_JUDGE_PROMPT_TAIL}"
    )


def plan(
    per_root: dict[Path, list[Declaration]], skip: list[str] | None = None
) -> dict[str, object]:
    """The ``judgments`` workflow's complete argument payload, ready to hand over.

    This is the whole planning step, done deterministically and across every
    root at once: each root's judgments are keyed, all the keys go to the shared
    seen-set in one query, and what comes back is exactly what the fan-out needs
    and nothing else. The orchestrating agent's entire involvement is copying
    this object into its ``Workflow`` call; a bulk sweep costs it no more pastes
    than a single-repo run.

    - ``cli`` -- the absolute, root-free invocation every later command is built
      from, so neither the workflow nor a judge ever spells one itself. One
      interpreter serves every root: ``--root`` is what retargets it, and the
      workflow appends it per command.
    - ``schema`` -- the fixed ``{verdict, opinion}`` structured-output contract
      every judge answers under. It is hashed into each judgment's content key, so
      shipping it here rather than mirroring it in the workflow keeps a single
      source: a judge cannot answer under a schema the cache did not record.
    - ``judge_prompt`` -- the one bootstrap template; the workflow substitutes
      each job's coordinates at :data:`CLI_PLACEHOLDER`, :data:`ROOT_PLACEHOLDER`,
      and :data:`ID_PLACEHOLDER`.
    - ``roots`` -- each swept root, in sorted order, mapped to how many of its
      judgments are already cached. Counts, not id lists: no caller needs the
      cached ids and every one of them costs agent context.
    - ``jobs`` -- the ``{id, root, model, effort}`` to judge, sorted by root then
      id, each pinned to the bench its own declaration names.
    - ``skipped`` -- the ``{id, root}`` pairs a ``skip`` id set aside; one id may
      cover several roots. Ids that are already cached are not "skipped" from
      anything and never appear here, so a non-empty list always means judgments
      that genuinely went unjudged.
    """
    roots = sorted(per_root, key=str)
    keyed = {root: [(d, _prepared(d, root)) for d in per_root[root]] for root in roots}
    cached = set(
        seen.filter(
            [prepared.key for pairs in keyed.values() for _, prepared in pairs]
        ).seen
    )
    set_aside = set(skip or ())
    uncached = [
        (root, d)
        for root in roots
        for d, prepared in keyed[root]
        if prepared.key not in cached
    ]
    return {
        "cli": invocation(),
        "schema": SCHEMA,
        "judge_prompt": judge_prompt(),
        "roots": {
            str(root): {
                "cached": sum(
                    1 for _, prepared in keyed[root] if prepared.key in cached
                )
            }
            for root in roots
        },
        "jobs": sorted(
            (
                {"id": d.id, "root": str(root), "model": d.model, "effort": d.effort}
                for root, d in uncached
                if d.id not in set_aside
            ),
            key=lambda job: (job["root"], job["id"]),
        ),
        "skipped": sorted(
            (
                {"id": d.id, "root": str(root)}
                for root, d in uncached
                if d.id in set_aside
            ),
            key=lambda entry: (entry["root"], entry["id"]),
        ),
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
    # a judge agent runs identically from any working directory. Each named root
    # must itself bear judgments: a target typo fails loudly here rather than
    # quietly planning an empty repo.
    roots: list[Path] = []
    for spec in args.root:
        named = Path(spec).resolve()
        if not (named / "pyproject.toml").is_file():
            print(
                f"judgments-run: --root {spec!r} has no pyproject.toml",
                file=sys.stderr,
            )
            return 1
        if resolve_root(named) != named:
            print(
                f"judgments-run: --root {spec!r} has no [tool.judgments] table",
                file=sys.stderr,
            )
            return 1
        roots.append(named)
    if args.command != "plan" and len(roots) > 1:
        print(
            f"judgments-run {args.command}: takes at most one --root",
            file=sys.stderr,
        )
        return 2
    try:
        if args.command == "plan":
            if roots:
                per_root = {root: load(root) for root in roots}
            else:
                resolved = resolve_root()
                per_root = {resolved or Path.cwd(): load(resolved)}
            # Resolving each --skip id here rejects a typo loudly instead of
            # quietly planning a judgment the caller believes it set aside; an
            # id needs to exist in at least one swept root.
            everywhere = [d for declarations in per_root.values() for d in declarations]
            for id in args.skip:
                by_id(everywhere, id)
            print(json.dumps(plan(per_root, args.skip)))
            return 0
        root = roots[0] if roots else resolve_root()
        declarations = load(root)
        if args.command == "render":
            print(render_prompt(by_id(declarations, args.id), root))
        elif args.command == "record":
            if not args.ids:
                print(
                    "judgments-run record: at least one id is required",
                    file=sys.stderr,
                )
                return 2
            record([by_id(declarations, id) for id in args.ids], root)
            # A silent success is indistinguishable from a command that never
            # ran, and the caller reports what was recorded to the user.
            print(f"judgments-run: recorded {len(args.ids)} judgment(s)")
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
        action="append",
        default=[],
        metavar="PATH",
        help="repo root to operate on (default: resolve it from the current "
        "directory); plan accepts it repeated, render/record at most once",
    )
    sub = parser.add_subparsers(dest="command")
    plan_parser = sub.add_parser(
        "plan", help="emit the judgments workflow's argument payload as JSON"
    )
    plan_parser.add_argument(
        "--skip",
        action="append",
        default=[],
        metavar="ID",
        help="a judgment to leave unjudged (repeatable); unknown ids are an error",
    )
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
