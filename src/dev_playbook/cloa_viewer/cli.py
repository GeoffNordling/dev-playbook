"""The ``cloa-viewer`` command: the process that makes the page exist.

``cloa-viewer [checkout ...] [--port N]`` is the only command the tool has. It
refreshes each checkout, starts the server, and prints the address to open
([Server and Stack](/worktree-cloa-viewer-tool-working-docs/server-and-stack.md)).
With no argument the checkout is the repo that contains the current directory.

The first refresh runs here, before the server starts, so the page has view
files to read the moment it loads; after that the checkout watcher inside the
server keeps them current. A generator that failed is named on stderr rather
than swallowed, and the page shows the same failure in its refresh status.

``uvicorn.run`` never returns until the server stops, so it sits alone in
``serve``: a test drives every other step of ``main`` by replacing that one
function.
"""

import argparse
import subprocess
import sys
from pathlib import Path

import uvicorn
from starlette.applications import Starlette

from dev_playbook.cloa_viewer import refresh, server
from dev_playbook.gitrepo import no_git_env

DEFAULT_PORT = 8765
DIST_DIR = "dist"
HOST = "127.0.0.1"
INDEX_FILE = "index.html"
LOG_LEVEL = "warning"
NO_PAGE_STATUS = 2
WEB_DIR = "web"


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


def dist_dir() -> Path:
    """The directory holding the page ``make web`` builds."""
    return Path(__file__).parent / WEB_DIR / DIST_DIR


def current_checkout() -> Path:
    """The root of the checkout holding the current directory.

    ``git rev-parse`` fails loudly when the directory is in no repository,
    which is the only honest answer: there is nothing to show.
    """
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
        env=no_git_env(),
    )
    return Path(result.stdout.strip())


def serve(app: Starlette, port: int) -> None:
    """Serve ``app`` on the loopback address at ``port`` until it stops."""
    uvicorn.run(app, host=HOST, port=port, log_level=LOG_LEVEL)


def main(argv: list[str] | None = None) -> int:
    """Run the command, returning the process exit status."""
    args = parse_args(argv)
    checkouts = [Path(path).resolve() for path in args.checkout]
    if not checkouts:
        checkouts = [current_checkout().resolve()]
    dist = dist_dir()
    if not (dist / INDEX_FILE).is_file():
        print("page not built: run make web", file=sys.stderr)
        return NO_PAGE_STATUS
    for checkout in checkouts:
        record = refresh.refresh(checkout)
        for generator in record["generators"]:
            if generator["status"] == refresh.STATUS_FAILED:
                print(
                    f"refresh failed: {generator['kind']} in {checkout}",
                    file=sys.stderr,
                )
    print(f"cloa-viewer at http://{HOST}:{args.port}/")
    serve(server.build_app(checkouts, dist), args.port)
    return 0
