"""The judgments-run CLI: deterministic plan / render / record over declarations.

Every subcommand reads the repo's declarations through the loader and drives the
two already-built dependencies -- ``judgments.core.prepare`` (claim + files +
bench -> content key and judge prompt) and the ``skipcache`` seen-set. No
LLM, no network: this is the deterministic half the judge skill stands on.

- ``plan``  -- key every judgment, partition by cache membership, emit one JSON
  object ``{schema, seen, unseen}`` with both lists ordered by id.
- ``render <id>`` -- print exactly the judge prompt for one judgment.
- ``record <id>... [--refuted <id>...]`` -- record the passing judgments' keys
  idempotently, and report each refuted judgment as a ``judgments.refuted``
  finding (never cached, so the gate stays red).
- ``--list-rules`` -- print the ``judgments.refuted`` rule id and exit; this is
  the read-only Audit detector behind the judgments card's judgments-run pointer.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import NamedTuple

from dev_playbook.findings import print_rules, render
from dev_playbook.judgments.core import SCHEMA, Prepared, prepare
from dev_playbook.judgments.loader import Declaration, by_id, load, resolve_root
from dev_playbook.skipcache import seen

# judgments-run is the detector behind the judgments card's second Audit pointer:
# recording a batch of verdicts is a read-only audit (it mutates only the
# content-addressed cache outside the repo, never anything git tracks), so a
# refuted verdict in that batch is a finding. This one rule id is a module-level
# constant so the emission site references it, not a raw literal, and RULES (what
# --list-rules prints) cannot drift from what the code emits.
REFUTED = "judgments.refuted"
RULES = (REFUTED,)

_DISPATCH_PROMPT = (
    "Run the shell command `judgments-run render {id}`. Its stdout is your complete "
    "instructions and the material to judge -- follow it and return your verdict."
)


class RefutedFinding(NamedTuple):
    """One refuted judgment, located at its id and rendered as a GNU finding."""

    location: str  # the judgment id -- the addressable thing under judgment
    rule: str  # REFUTED
    message: str


def plan(declarations: list[Declaration], root: Path | None) -> dict[str, object]:
    """Partition the judgments by cache membership into a ``{schema, seen, unseen}``.

    ``seen`` is the sorted ids whose key is already cached; ``unseen`` is the
    sorted-by-id list of ``{id, model, effort, prompt}`` the judge skill must still
    run -- each a ready-to-dispatch job whose ``prompt`` bootstraps a judge agent.
    """
    keyed = [(d, _prepared(d, root)) for d in declarations]
    cached = set(seen.filter([prepared.key for _, prepared in keyed]).seen)
    seen_ids = sorted(d.id for d, prepared in keyed if prepared.key in cached)
    unseen = sorted(
        (
            {
                "id": d.id,
                "model": d.model,
                "effort": d.effort,
                "prompt": _DISPATCH_PROMPT.format(id=d.id),
            }
            for d, prepared in keyed
            if prepared.key not in cached
        ),
        key=lambda entry: entry["id"],
    )
    return {"schema": SCHEMA, "seen": seen_ids, "unseen": unseen}


def render_prompt(declaration: Declaration, root: Path | None) -> str:
    """The judge prompt for one judgment -- the XML input a judge agent runs.

    Named ``render_prompt`` (not ``render``) so it does not shadow the shared GNU
    finding renderer this module imports for the refuted-verdict finding.
    """
    return _prepared(declaration, root).prompt


def record(declarations: list[Declaration], root: Path | None) -> None:
    """Record the given judgments' content keys in the seen-set, idempotently."""
    seen.record([_prepared(d, root).key for d in declarations])


def refutations(declarations: list[Declaration]) -> list[RefutedFinding]:
    """One ``judgments.refuted`` finding per refuted judgment in the batch.

    A refuted verdict is never cached (the gate stays red until the claim is
    judged-and-passed); recording the batch surfaces it as a finding instead.
    """
    return [
        RefutedFinding(d.id, REFUTED, "recorded verdict is refuted")
        for d in declarations
    ]


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
        return print_rules(RULES)
    if args.command is None:
        print("judgments-run: a subcommand is required", file=sys.stderr)
        return 2
    root = resolve_root()
    try:
        declarations = load(root)
        if args.command == "plan":
            print(json.dumps(plan(declarations, root)))
        elif args.command == "render":
            print(render_prompt(by_id(declarations, args.id), root))
        elif args.command == "record":
            record([by_id(declarations, id) for id in args.ids], root)
            findings = refutations([by_id(declarations, id) for id in args.refuted])
            for finding in findings:
                print(render(finding.location, finding.rule, finding.message))
            if findings:
                return 1
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
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("plan", help="emit {schema, seen, unseen} as JSON")
    render_parser = sub.add_parser("render", help="print one judgment's judge prompt")
    render_parser.add_argument("id", help="the judgment id to render")
    record_parser = sub.add_parser("record", help="record verdicts over judgments")
    record_parser.add_argument(
        "ids", nargs="*", help="the passing judgment ids to record"
    )
    record_parser.add_argument(
        "--refuted",
        action="append",
        default=[],
        metavar="ID",
        help="a refuted judgment id, reported as a judgments.refuted finding",
    )
    return parser.parse_args(argv)
