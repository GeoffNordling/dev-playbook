"""The ``cloa-viewer`` command: the process that makes the page exist.

``cloa-viewer [path ...] [--port N]`` is the only command the tool has. A path
that is a checkout is shown as it is; a path that is not one, ``~/workspace/``
being the case that matters, is scanned for the repos below it and their
worktrees
([Server](/worktree-cloa-viewer-tool-working-docs/server.md)).
The command refreshes each checkout it found, starts the server, and prints the
address to open.

The paths, not the checkouts, are what the server is given: the server rescans
them while it runs, so a worktree made after launch needs no restart.

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

from dev_playbook.cloa_viewer import discover, refresh, server
from dev_playbook.gitrepo import no_git_env

DEFAULT_PORT = 8765
DIST_DIR = "dist"
HOST = "127.0.0.1"
INDEX_FILE = "index.html"
LOG_LEVEL = "warning"
NO_CHECKOUT_STATUS = 2
NO_PAGE_STATUS = 2
SHUTDOWN_SECONDS = 2
WEB_DIR = "web"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the command line into ``path`` (a list) and ``port``."""
    parser = argparse.ArgumentParser(
        prog="cloa-viewer",
        description="Serve a workspace's markdown as a browser page.",
    )
    parser.add_argument(
        "path",
        nargs="*",
        help=(
            "a checkout, or a directory of repos to scan; defaults to the repo "
            "holding the current directory, else the current directory"
        ),
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


def default_source() -> Path:
    """The path to scan when the command was given none.

    The repo holding the current directory when there is one, so the command
    typed inside a checkout shows that checkout. The current directory itself
    when ``git rev-parse`` fails, which is the ``~/workspace`` case: a directory
    of repos is no repository, and scanning it is exactly what is wanted.
    """
    try:
        return current_checkout().resolve()
    except subprocess.CalledProcessError:
        return Path.cwd()


def serve(app: Starlette, port: int) -> None:
    """Serve ``app`` on the loopback address at ``port`` until it stops.

    A graceful shutdown waits for every open connection to close, and the
    page's event stream never closes on its own: without a limit, Ctrl-C leaves
    the server running for as long as one page is open. ``SHUTDOWN_SECONDS``
    cuts the wait short, so an interrupt stops the process.
    """
    uvicorn.run(
        app,
        host=HOST,
        port=port,
        log_level=LOG_LEVEL,
        timeout_graceful_shutdown=SHUTDOWN_SECONDS,
    )


def main(argv: list[str] | None = None) -> int:
    """Run the command, returning the process exit status."""
    args = parse_args(argv)
    sources = [Path(path).resolve() for path in args.path]
    if not sources:
        sources = [default_source()]
    dist = dist_dir()
    if not (dist / INDEX_FILE).is_file():
        print("page not built: run make web", file=sys.stderr)
        return NO_PAGE_STATUS
    try:
        checkouts = discover.checkouts(sources)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return NO_CHECKOUT_STATUS
    for checkout in checkouts:
        record = refresh.refresh(checkout)
        for generator in record["generators"]:
            if generator["status"] == refresh.STATUS_FAILED:
                print(
                    f"refresh failed: {generator['kind']} in {checkout}",
                    file=sys.stderr,
                )
    print(f"cloa-viewer at http://{HOST}:{args.port}/")
    serve(server.build_app(sources, dist), args.port)
    return 0
