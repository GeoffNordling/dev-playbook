"""Refresh: run every registered generator and rewrite one checkout's state.

A refresh is the only path from a checkout to view files
([Contract](/worktree-cloa-viewer-tool-working-docs/contract.md)). It writes
``checkout.json``, then walks the registry: each kind's views are validated
against the envelope schema and the kind's own schema before any of them lands,
staged inside the checkout directory, and moved into place in one step. The
viewer watches that directory, so a reader sees the last good files or the new
ones and never a half-written kind.

A generator replaces its kind's files whole or changes nothing at all. When one
raises, its files stay as the last good run left them and the record carries the
traceback, by the fail loud principle: a broken generator shows on screen as a
red refresh status, never as a kind that quietly went missing.
"""

import os
import shutil
import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dev_playbook.cloa_viewer import registry, state
from dev_playbook.cloa_viewer.entry import Kind, View

ENVELOPE_SCHEMA = "envelope"
RECORD_FILE = "refresh.json"
RECORD_SCHEMA = "refresh"
RETIRED_DIR = "retired"
STAGING_DIR = ".staging"
STATUS_FAILED = "failed"
STATUS_OK = "ok"


def _now() -> str:
    """The current time, UTC RFC 3339 with a ``Z`` suffix."""
    return datetime.now(UTC).strftime(state.RFC_3339_UTC)


def _clear(path: Path) -> None:
    """Remove ``path`` and everything under it, when it is there."""
    if path.exists():
        shutil.rmtree(path)


def _stage(kind: Kind, checkout: Path, staging: Path) -> list[View]:
    """Validate every view ``kind`` builds for ``checkout``, and write it staged.

    Both schemas run before the first write, so a generator that produces one
    bad view among many publishes none of them.
    """
    views = kind.generate(checkout)
    envelope_schema = state.load_schema(ENVELOPE_SCHEMA)
    payload_schema = state.load_schema(kind.name)
    for view in views:
        state.validate(view.envelope, envelope_schema)
        state.validate(view.envelope["payload"], payload_schema)
    for view in views:
        state.write_json(staging / view.relpath, view.envelope)
    return views


def _publish(kind: Kind, views: list[View], staging: Path, target: Path) -> None:
    """Move ``kind``'s staged files into ``target``, replacing what it wrote before.

    A per-subject kind replaces its whole directory, so a subject the checkout
    no longer holds leaves no view file behind; a per-checkout kind replaces its
    one file. Staging and target sit in the same tree, so every move is an
    ``os.replace`` and no reader sees a partial kind.

    The last run's directory is renamed into staging rather than deleted where
    it stands. Deleting it in place would reach the state watcher as one
    removed view file per subject, and the viewer would close every panel of
    that kind a moment before the replacement arrived.
    """
    if not kind.per_subject:
        for view in views:
            os.replace(staging / view.relpath, target / view.relpath)
        return
    # A kind that found no subjects still replaces its directory: an empty
    # directory is the honest answer, and last run's files are not.
    (staging / kind.name).mkdir(parents=True, exist_ok=True)
    live = target / kind.name
    if live.exists():
        os.replace(live, staging / RETIRED_DIR)
    os.replace(staging / kind.name, live)


def refresh(checkout: Path) -> dict[str, Any]:
    """Rewrite ``checkout``'s state directory, and return the refresh record.

    The record says when the run started and finished, which commit it
    describes, and for every registered kind whether its generator succeeded,
    how many view files it wrote, and the error text when it failed.
    """
    target = state.checkout_dir(checkout)
    state.write_checkout_json(checkout)
    started = _now()
    commit = state.head_commit(checkout)
    staging_root = target / STAGING_DIR
    # A refresh killed mid-flight leaves staged files behind, and they would
    # otherwise ride into this run's publish.
    _clear(staging_root)
    generators: list[dict[str, Any]] = []
    for kind in registry.KINDS:
        staging = staging_root / kind.name
        try:
            views = _stage(kind, checkout, staging)
            _publish(kind, views, staging, target)
        except Exception:
            generators.append(
                {
                    "kind": kind.name,
                    "status": STATUS_FAILED,
                    "count": 0,
                    "error": traceback.format_exc(),
                }
            )
        else:
            generators.append(
                {
                    "kind": kind.name,
                    "status": STATUS_OK,
                    "count": len(views),
                    "error": None,
                }
            )
    _clear(staging_root)
    record = {
        "started": started,
        "finished": _now(),
        "commit": commit,
        "generators": generators,
    }
    state.validate(record, state.load_schema(RECORD_SCHEMA))
    state.write_json(target / RECORD_FILE, record)
    return record
