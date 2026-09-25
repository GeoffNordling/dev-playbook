"""The ``stint`` command: run an unattended stint in sealed containers.

    stint setup --playbook PATH --claude PATH
    stint run REPO --base REF --workstream DIR --check CMD --budget N
              --name NAME --home DIR --playbook PATH --model MODEL

Every argument is required; none has a default. Exit codes:

    0   done: the principal said done, and the branch landed
    1   any other end: a stop rule, the principal's stuck, or a copy kept
    2   the tool could not run: not set up, a bad argument, a failed step
"""

import argparse
import sys
from pathlib import Path

from dev_playbook.errors import ToolError
from dev_playbook.stint import install
from dev_playbook.stint.call import run_node
from dev_playbook.stint.launch import Host, Order, launch
from dev_playbook.stint.receiver import EVENTS_DB
from dev_playbook.stint.workcopy import CopyFault

CREDENTIALS = Path("~/.claude/.credentials.json").expanduser()


def parser() -> argparse.ArgumentParser:
    """The command's arguments."""
    top = argparse.ArgumentParser(prog="stint", description=__doc__.split("\n")[0])
    commands = top.add_subparsers(dest="command", required=True)

    setup = commands.add_parser("setup", help="install Sandcastle and build the image")
    setup.add_argument(
        "--playbook", type=Path, required=True, help="dev-playbook checkout"
    )
    setup.add_argument(
        "--claude", type=Path, required=True, help="the claude binary to install"
    )

    run = commands.add_parser("run", help="run one stint to its end")
    run.add_argument("repo", type=Path, help="the repository the stint changes")
    run.add_argument("--base", required=True, help="the ref the branch starts at")
    run.add_argument(
        "--workstream", required=True, help="the workstream folder, repo-relative"
    )
    run.add_argument(
        "--check",
        required=True,
        help="the target check: a command whose exit 0 is zero findings",
    )
    run.add_argument(
        "--budget", type=int, required=True, help="the most iterations to spend"
    )
    run.add_argument("--name", required=True, help="the stint's name and branch")
    run.add_argument(
        "--home", type=Path, required=True, help="where stint folders live"
    )
    run.add_argument(
        "--playbook", type=Path, required=True, help="dev-playbook checkout"
    )
    run.add_argument("--model", required=True, help="the Claude model for every call")
    return top


def main(argv: list[str] | None = None) -> int:
    """Run one subcommand; return its exit code."""
    args = parser().parse_args(argv)
    try:
        if args.command == "setup":
            install.setup(args.playbook, args.claude)
            print(f"stint: set up, image {install.IMAGE}")
            return 0
        install.check_installed()
        order = Order(
            repo=args.repo,
            base=args.base,
            workstream=args.workstream,
            check=args.check,
            budget=args.budget,
            name=args.name,
            home=args.home,
            playbook=args.playbook,
            model=args.model,
        )
        host = Host(
            image=install.IMAGE,
            credentials=CREDENTIALS,
            events=EVENTS_DB,
            runner=run_node,
            workspace=Path.home() / "workspace",
        )
        record = launch(order, host)
    except (ToolError, CopyFault) as err:
        print(f"stint: {err}", file=sys.stderr)
        return 2
    return 0 if record.reason == "done" and record.closed else 1
