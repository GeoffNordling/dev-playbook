"""The judgments-run CLI: deterministic plan / render / record over declarations.

Every subcommand reads the repo's declarations through the loader and drives the
two already-built dependencies -- ``judgments.core.prepare`` (claim + files +
instrument -> content key and judge prompt) and the ``skipcache`` seen-set. No
LLM, no network: this is the deterministic half the judge skill stands on.

- ``plan``  -- key every judgment, partition by cache membership, emit one JSON
  object ``{schema, seen, unseen}`` with both lists ordered by id.
- ``render <id>`` -- print exactly the judge prompt for one judgment.
- ``record <id>...`` -- record the passing judgments' keys, idempotently.
"""

import argparse
import json
import sys
from pathlib import Path

from judgments.core import SCHEMA, Prepared, prepare
from judgments.loader import Declaration, by_id, load, resolve_root
from skipcache import seen

_DISPATCH_PROMPT = (
    "Run the shell command `judgments-run render {id}`. Its stdout is your complete "
    "instructions and the material to judge -- follow it and return your verdict."
)


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


def render(declaration: Declaration, root: Path | None) -> str:
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


def main(argv: list[str]) -> int:
    """Parse the subcommand, load declarations, and run it; nonzero on any error."""
    args = _parse_args(argv)
    root = resolve_root()
    try:
        declarations = load(root)
        if args.command == "plan":
            print(json.dumps(plan(declarations, root)))
        elif args.command == "render":
            print(render(by_id(declarations, args.id), root))
        elif args.command == "record":
            record([by_id(declarations, id) for id in args.ids], root)
    except (ValueError, OSError) as error:
        print(f"judgments-run: {error}", file=sys.stderr)
        return 1
    return 0


def _parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse the plan / render / record subcommand and its arguments."""
    parser = argparse.ArgumentParser(
        prog="judgments-run",
        description="Deterministic plan/render/record over judgment declarations.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("plan", help="emit {schema, seen, unseen} as JSON")
    render_parser = sub.add_parser("render", help="print one judgment's judge prompt")
    render_parser.add_argument("id", help="the judgment id to render")
    record_parser = sub.add_parser("record", help="record passing judgments' keys")
    record_parser.add_argument("ids", nargs="+", help="the judgment ids to record")
    return parser.parse_args(argv)
