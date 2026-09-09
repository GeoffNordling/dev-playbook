"""The server: the page, the view files, the schemas, and the event stream.

Three of the server's five jobs live here, discover, serve, and watch the state
directory.
The routes under ``/api`` hand the page everything the contract puts on disk:
the registered kinds, the schemas, the checkouts, each checkout's view files,
and the refresh record. ``/`` and ``/assets`` serve the built page itself.

The server is given the paths the command was given, not a fixed list of
checkouts. ``rescan`` turns those paths into checkouts again on every checkout
list request, so a worktree added or removed while the server runs reaches the
page without a restart: the new one is refreshed and watched, and the gone one
loses its watcher and its state directory.

Live update is one-way, server to page. ``watch_state`` watches the whole state
directory and turns every view file written or removed into one message; the
subscribers, one queue per open page, carry it to a server-sent events stream.
The page then fetches that one file and re-renders that one panel, so a refresh
that rewrote two hundred files still moves only what changed on screen.

The other two jobs are started here but written elsewhere: ``rescan`` runs one
``watch.watch_checkout`` task per checkout, and each of those calls the refresh
in ``refresh``.
"""

import asyncio
import contextlib
import json
import re
import shutil
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

from dev_playbook.cloa_viewer import discover, refresh, registry, state, watch

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
# A stopped watcher returns as soon as watchfiles reads the event, far inside
# this. The bound is here so a watcher that never returns fails the request or
# the shutdown that waited for it instead of hanging the server.
WATCHER_STOP_SECONDS = 10.0

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


# --- discovery: the checkouts this server shows ---

# One running checkout watcher: the task, and the event that stops it.
Watcher = tuple[asyncio.Task[None], asyncio.Event]


def _start_watcher(checkout: Path, found: list[Path]) -> Watcher:
    """Start watching ``checkout``, ignoring every discovered checkout inside it."""
    inside = [
        other for other in found if other != checkout and other.is_relative_to(checkout)
    ]
    stop = asyncio.Event()
    task = asyncio.create_task(watch.watch_checkout(checkout, ignore=inside, stop=stop))
    return task, stop


async def _stop_watcher(watcher: Watcher) -> None:
    """Stop one checkout watcher, and wait for its task to finish."""
    task, stop = watcher
    stop.set()
    await asyncio.wait_for(task, WATCHER_STOP_SECONDS)


async def rescan(app: Starlette) -> list[Path]:
    """Discover the checkouts again, and make the running server match.

    This is the first of the server's five jobs. The command hands the server
    the paths it was given rather than a settled list, so a worktree added or
    removed while the server runs shows up on the page the next time it asks
    for the checkout list: a checkout that appeared is refreshed and watched,
    and one that vanished loses its watcher and its state directory.

    A checkout already refreshed keeps the view files it has, so the answer to
    a page load costs a discovery and nothing more.

    Discovery runs git once per repo, and a refresh runs every generator, so
    both go to a worker thread and the server keeps answering while they do.
    """
    sources: list[Path] = app.state.sources
    current: list[Path] = app.state.checkouts
    watchers: dict[Path, Watcher] = app.state.watchers
    found: list[Path] = await asyncio.to_thread(discover.checkouts, sources)
    for checkout in found:
        if checkout in current:
            continue
        if not (state.checkout_dir(checkout) / refresh.RECORD_FILE).exists():
            await asyncio.to_thread(refresh.refresh, checkout)
        watchers[checkout] = _start_watcher(checkout, found)
    for checkout in current:
        if checkout in found:
            continue
        await _stop_watcher(watchers.pop(checkout))
        directory = state.checkout_dir(checkout)
        if directory.exists():
            shutil.rmtree(directory)
    app.state.checkouts = found
    return found


# --- routes ---


def _checkout_path(request: Request) -> Path:
    """The checkout the request's ``dir`` names, or a 404 when it names none."""
    checkouts: list[Path] = request.app.state.checkouts
    name = request.path_params["dir"]
    for checkout in checkouts:
        if state.checkout_dir(checkout).name == name:
            return checkout
    raise HTTPException(status_code=404, detail=f"no checkout {name}")


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
    """Every checkout on this server, with the facts ``checkout.json`` holds.

    Discovery runs first, so this one request is also how the page learns that
    a worktree was added or removed since it last asked.
    """
    listed = []
    for checkout in await rescan(request.app):
        directory = state.checkout_dir(checkout)
        facts = json.loads((directory / CHECKOUT_FILE).read_text())
        listed.append({"dir": directory.name, **facts})
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
    """Discover the checkouts, then run the watchers for as long as it serves.

    One state watcher for the whole state directory, and one checkout watcher
    per checkout, started by ``rescan``: together they close the loop from an
    edit in a checkout to a message on an open page. The discovery runs first,
    because the state watcher has nothing to report until a refresh has written
    something.
    """
    await rescan(app)
    state_watcher = asyncio.create_task(watch_state())
    try:
        yield
    finally:
        state_watcher.cancel()
        watchers: dict[Path, Watcher] = app.state.watchers
        for watcher in watchers.values():
            await _stop_watcher(watcher)
        watchers.clear()


def build_app(sources: list[Path], dist: Path) -> Starlette:
    """The application serving whatever ``sources`` discovers, and ``dist``'s page.

    ``sources`` is what the command was given, a checkout or a directory of
    repos, kept rather than resolved into checkouts once: the list of checkouts
    is ``rescan``'s answer and changes while the server runs. Every source must
    already be an absolute resolved path, because ``state.checkout_dir`` names a
    directory from the path it is given and two spellings of one checkout would
    be two checkouts here.

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
    app.state.sources = sources
    app.state.checkouts = []
    app.state.watchers = {}
    app.state.dist = dist
    return app
