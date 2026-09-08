"""The server: the page, the view files, the schemas, and the event stream.

Two of the server's four jobs live here, serve and watch the state directory
([Server and Stack](/worktree-cloa-viewer-tool-working-docs/server-and-stack.md)).
The routes under ``/api`` hand the page everything the contract puts on disk:
the registered kinds, the schemas, the checkouts, each checkout's view files,
and the refresh record. ``/`` and ``/assets`` serve the built page itself.

Live update is one-way, server to page. ``watch_state`` watches the whole state
directory and turns every view file written or removed into one message; the
subscribers, one queue per open page, carry it to a server-sent events stream.
The page then fetches that one file and re-renders that one panel, so a refresh
that rewrote two hundred files still moves only what changed on screen.
"""

import asyncio
import contextlib
import json
import re
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import watchfiles
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, Response, StreamingResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from dev_playbook.cloa_viewer import refresh, registry, state

CHECKOUT_FILE = "checkout.json"
EVENT_CHANGED = "changed"
EVENT_CONNECTED = "connected"
EVENT_REFRESHED = "refreshed"
EVENT_REMOVED = "removed"
INDEX_FILE = "index.html"
SCHEMA_NAME = re.compile(r"[a-z][a-z0-9-]*")
# A refresh has already settled by the time it writes, so this watcher waits
# only long enough to batch one refresh's files. watchfiles defaults to 1600ms,
# which alone would spend most of the budget for an edit reaching the screen.
STATE_DEBOUNCE_MS = 200
VIEW_SUFFIX = ".json"

# --- subscribers: one queue per open page ---

SUBSCRIBERS: set[asyncio.Queue[dict[str, Any]]] = set()


def subscribe() -> asyncio.Queue[dict[str, Any]]:
    """Register a new subscriber, and return the queue its messages arrive on."""
    queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
    SUBSCRIBERS.add(queue)
    return queue


def unsubscribe(queue: asyncio.Queue[dict[str, Any]]) -> None:
    """Drop ``queue``; raises unless it is a registered subscriber."""
    SUBSCRIBERS.remove(queue)


def publish(message: dict[str, Any]) -> None:
    """Put ``message`` on every subscriber's queue.

    Nothing awaits, so a page that has stopped reading its queue delays no
    other page and no watcher.
    """
    for queue in SUBSCRIBERS:
        queue.put_nowait(message)


# --- the state watcher ---


async def watch_state() -> None:
    """Publish one message for every view file the state directory changes.

    This is the whole of the push: it runs for as long as the server does, and
    it watches the state root rather than one checkout directory, so a checkout
    added to a running server needs no new watcher.
    """
    root = state.state_root()
    # The server can start before any refresh has made the directory, and
    # awatch raises on a path that is not there.
    root.mkdir(parents=True, exist_ok=True)
    async for changes in watchfiles.awatch(root, debounce=STATE_DEBOUNCE_MS):
        # One refresh reaches this loop as a directory event and as the stale
        # per-file events the rename left behind, so the same view file is named
        # several times in one batch and the page would fetch it several times.
        seen: set[tuple[str, ...]] = set()
        for change, raw in changes:
            for message in messages_for(change, Path(raw), root):
                key = tuple(str(value) for value in message.values())
                if key not in seen:
                    seen.add(key)
                    publish(message)


def messages_for(
    change: watchfiles.Change, path: Path, root: Path
) -> list[dict[str, Any]]:
    """The messages ``change`` to ``path`` deserves, which is often none.

    Three things under the state root carry no view message: the staging tree a
    refresh writes through, ``checkout.json``, and ``refresh.json``, which
    announces a finished refresh instead.

    A directory carries one message per view file below it. A per-subject kind
    is published by renaming its whole directory into place, and the kernel
    reports that as one event on the directory and none at all on the files
    inside, so fanning out here is the only way the page hears about them.

    A delete of a path that is there again is a republish, not a removal. The
    kernel reports a deletion inside a directory that was just renamed under
    the directory's old name, so the two are indistinguishable from the event
    alone; asking the filesystem tells them apart, and the panel the user has
    open survives a refresh that rewrote its file.
    """
    relative = path.relative_to(root)
    if len(relative.parts) < 2 or relative.parts[1] == refresh.STAGING_DIR:
        return []
    checkout = relative.parts[0]
    relpath = Path(*relative.parts[1:])
    if str(relpath) == CHECKOUT_FILE:
        return []
    if str(relpath) == refresh.RECORD_FILE:
        return [{"event": EVENT_REFRESHED, "checkout": checkout}]
    if path.is_dir():
        return [
            {
                "event": EVENT_CHANGED,
                "checkout": checkout,
                "path": str(relpath / found.relative_to(path)),
            }
            for found in sorted(path.rglob(f"*{VIEW_SUFFIX}"))
        ]
    if path.suffix != VIEW_SUFFIX:
        return []
    gone = change is watchfiles.Change.deleted and not path.exists()
    event = EVENT_REMOVED if gone else EVENT_CHANGED
    return [{"event": event, "checkout": checkout, "path": str(relpath)}]


# --- routes ---


def _checkout_path(request: Request) -> Path:
    """The checkout the request's ``dir`` names, or a 404 when it names none."""
    checkouts: dict[str, Path] = request.app.state.checkouts
    name = request.path_params["dir"]
    if name not in checkouts:
        raise HTTPException(status_code=404, detail=f"no checkout {name}")
    return checkouts[name]


async def index(request: Request) -> FileResponse:
    """Serve the built page."""
    dist: Path = request.app.state.dist
    return FileResponse(dist / INDEX_FILE)


async def kinds(request: Request) -> JSONResponse:
    """The registered kinds, so the page can tell a missing renderer from a typo."""
    return JSONResponse(
        [
            {
                "name": kind.name,
                "version": kind.version,
                "per_subject": kind.per_subject,
            }
            for kind in registry.KINDS
        ]
    )


async def schema(request: Request) -> JSONResponse:
    """One schema by name, the same file the server validates against."""
    name = request.path_params["name"]
    # The name arrives from a URL, so it reaches the filesystem only after it
    # is shown to be a bare kind name.
    if not SCHEMA_NAME.fullmatch(name):
        raise HTTPException(status_code=404, detail=f"no schema {name}")
    try:
        return JSONResponse(state.load_schema(name))
    except FileNotFoundError:
        # An unregistered name is a question the page may ask, not a defect.
        raise HTTPException(status_code=404, detail=f"no schema {name}") from None


async def checkout_list(request: Request) -> JSONResponse:
    """Every checkout on this server, with the facts ``checkout.json`` holds."""
    directories: dict[str, Path] = request.app.state.checkouts
    listed = []
    for name, checkout in directories.items():
        facts = json.loads((state.checkout_dir(checkout) / CHECKOUT_FILE).read_text())
        listed.append({"dir": name, **facts})
    return JSONResponse(listed)


async def files(request: Request) -> JSONResponse:
    """The relative paths of one checkout's view files, sorted."""
    directory = state.checkout_dir(_checkout_path(request))
    listed = []
    for path in directory.rglob(f"*{VIEW_SUFFIX}"):
        relpath = path.relative_to(directory)
        if relpath.parts[0] == refresh.STAGING_DIR:
            continue
        if str(relpath) in (CHECKOUT_FILE, refresh.RECORD_FILE):
            continue
        listed.append(str(relpath))
    return JSONResponse(sorted(listed))


async def view(request: Request) -> Response:
    """One view file, exactly as it sits on disk, or a 404."""
    directory = state.checkout_dir(_checkout_path(request)).resolve()
    # The relative path arrives from a URL, so a "../" in it must not escape
    # the checkout directory.
    path = (directory / request.path_params["relpath"]).resolve()
    if not path.is_relative_to(directory) or not path.is_file():
        raise HTTPException(status_code=404, detail=f"no view {request.url.path}")
    return Response(content=path.read_text(), media_type="application/json")


async def refresh_record(request: Request) -> JSONResponse:
    """The record of this checkout's last refresh."""
    directory = state.checkout_dir(_checkout_path(request))
    record: dict[str, Any] = json.loads((directory / refresh.RECORD_FILE).read_text())
    return JSONResponse(record)


async def run_refresh(request: Request) -> JSONResponse:
    """Refresh this checkout now, and answer with the record it wrote.

    The generators are ordinary blocking code, so they run on a worker thread
    and the event loop keeps serving every other page while they do.
    """
    checkout = _checkout_path(request)
    return JSONResponse(await asyncio.to_thread(refresh.refresh, checkout))


async def events(request: Request) -> StreamingResponse:
    """The server-sent events stream one open page listens on."""
    return StreamingResponse(_stream(), media_type="text/event-stream")


async def _stream() -> AsyncIterator[str]:
    """Yield the connected message, then every message published from now on."""
    queue = subscribe()
    try:
        yield _frame({"event": EVENT_CONNECTED})
        while True:
            yield _frame(await queue.get())
    finally:
        unsubscribe(queue)


def _frame(message: dict[str, Any]) -> str:
    """``message`` as one server-sent events frame."""
    return f"data: {json.dumps(message, sort_keys=True)}\n\n"


# --- the application ---


@contextlib.asynccontextmanager
async def _lifespan(app: Starlette) -> AsyncIterator[None]:
    """Run the state watcher for as long as the server serves."""
    watcher = asyncio.create_task(watch_state())
    try:
        yield
    finally:
        watcher.cancel()


def build_app(checkouts: list[Path], dist: Path) -> Starlette:
    """The application serving ``checkouts`` and the page built into ``dist``.

    A checkout is addressed by its state directory's name, never by its path,
    so the page names a checkout the same way the state directory does.
    """
    routes = [
        Route("/", index),
        Route("/api/kinds", kinds),
        Route("/api/schemas/{name}", schema),
        Route("/api/checkouts", checkout_list),
        Route("/api/checkouts/{dir}/files", files),
        Route("/api/checkouts/{dir}/view/{relpath:path}", view),
        Route("/api/checkouts/{dir}/refresh", refresh_record, methods=["GET"]),
        Route("/api/checkouts/{dir}/refresh", run_refresh, methods=["POST"]),
        Route("/api/events", events),
        Mount("/assets", StaticFiles(directory=dist / "assets")),
    ]
    app = Starlette(routes=routes, lifespan=_lifespan)
    app.state.checkouts = {
        state.checkout_dir(checkout).name: checkout.resolve() for checkout in checkouts
    }
    app.state.dist = dist
    return app
