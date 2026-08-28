"""Run one probe command: python3 -m probe <command>."""

import sys

from probe import commands

COMMANDS = {
    "build-image": commands.build_image,
    "check-tools": commands.check_tools,
    "check-fence": commands.check_fence,
    "check-claude": commands.check_claude,
    "check-billing": commands.check_billing,
    "check-config": commands.check_config,
    "run-task": commands.run_task,
    "check-cleanup": commands.check_cleanup,
}


def main(args: list[str]) -> int:
    """Look up one command by name and run it."""
    if len(args) != 1 or args[0] not in COMMANDS:
        print("commands:", *COMMANDS, sep="\n  ", file=sys.stderr)
        return 2

    COMMANDS[args[0]]()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
