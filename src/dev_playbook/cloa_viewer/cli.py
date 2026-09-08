"""The ``cloa-viewer`` command: argument parsing and the process entry point.

``cloa-viewer [checkout ...] [--port N]`` is the only command the tool has. It
refreshes each checkout, starts the server, and prints the address to open
([Server and Stack](/worktree-cloa-viewer-tool-working-docs/server-and-stack.md)).
This module carries the argument surface; the refresh and serve behavior lands
in a later task.
"""

import argparse

DEFAULT_PORT = 8765


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the command line into ``checkout`` (a list) and ``port``."""
    parser = argparse.ArgumentParser(
        prog="cloa-viewer",
        description="Serve one checkout's markdown as a browser page.",
    )
    parser.add_argument(
        "checkout",
        nargs="*",
        help="checkout to show; defaults to the repo holding the current directory",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"port to serve on (default: {DEFAULT_PORT})",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the command, returning the process exit status."""
    parse_args(argv)
    return 0
