"""Live-daemon integration tests: render real sessions end to end.

Unlike every other transcript_export test (which mocks the `agentsview`
subprocess), these drive the always-on local AgentsView daemon for real. They
exercise the three read commands the tool uses — `session list` / `get` /
`messages` — and assert *structural* invariants only (well-formed XML, header
present, ord attributes integral), never exact content: real sessions change.

This machine always runs the AgentsView daemon, so an unreachable daemon means
something is actually wrong. These tests therefore **fail loudly** rather than
skip — a skip here would hide a real breakage behind a green gate.
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from transcript_export.cli import main
from transcript_export.client import session_get, session_list, session_messages
from transcript_export.transcript import render_session


def _recent_ids(limit: int) -> list[str]:
    """The newest session ids from the live daemon.

    No defensive guard: if the daemon is unreachable this raises, and the live
    suite fails loudly, because on this machine an unreachable daemon is a real
    fault, not an expected absence.
    """
    return [s["id"] for s in session_list()["sessions"][:limit]]


_RECENT = _recent_ids(3)


def test_session_list_get_messages_round_trip() -> None:
    sid = _RECENT[0]

    listing = session_list()
    assert any(s["id"] == sid for s in listing["sessions"])

    meta = session_get(sid)
    assert meta["id"] == sid

    rows = session_messages(sid)
    assert isinstance(rows, list)
    assert all("ordinal" in row for row in rows)


def test_render_recent_session_is_well_formed_xml() -> None:
    sid = _RECENT[0]

    xml = render_session(sid)
    root = ET.fromstring(xml)  # raises on malformed output

    assert root.tag == "session"
    assert root.attrib["id"] == sid
    # Every element that carries an ord must hold an integer ordinal.
    for el in root.iter():
        if "ord" in el.attrib:
            int(el.attrib["ord"])


def test_render_several_recent_sessions_all_parse() -> None:
    # Rendering a handful of real sessions exercises the messy realities (forks,
    # compaction, sub-agents, tool output with ANSI control bytes) that hand-built
    # fixtures cannot, and asserts each still produces valid XML.
    for sid in _RECENT:
        root = ET.fromstring(render_session(sid))
        assert root.attrib["id"] == sid


def test_real_interrupt_session_renders_interrupted_tag() -> None:
    # Real interrupt rows are source_type="system", source_subtype="interrupted".
    # The system->DROP rule used to swallow them before the interrupt check, so no
    # <interrupted/> ever rendered. Find a live session that has one and assert the
    # tag survives into the export.
    sid = next(
        (
            s["id"]
            for s in session_list()["sessions"]
            if any(
                row.get("source_subtype") == "interrupted"
                for row in session_messages(s["id"])
            )
        ),
        None,
    )
    if sid is None:
        pytest.fail("no live session has an interrupt row to verify against")
    assert "<interrupted" in render_session(sid)


def test_real_bare_marker_session_renders_without_leaking_marker() -> None:
    # claude-haiku-4-5 / plan-mode turns emit a bare `[ToolName]` marker (no
    # colon-detail). The stripper used to miss these and silently leak them into
    # prose. Find a live session whose assistant turn ends in a bare marker, render
    # it, and assert that exact line is gone from the export.
    bare = re.compile(r"^\[[A-Z][A-Za-z0-9_]*( [A-Za-z0-9_]+)*\]$")
    target: tuple[str, str] | None = None
    for s in session_list()["sessions"]:
        sid = s["id"]
        for row in session_messages(sid):
            if not row.get("tool_calls"):
                continue
            last = (row.get("content") or "").rstrip().split("\n")[-1]
            if bare.match(last):
                target = (sid, last)
                break
        if target is not None:
            break
    if target is None:
        pytest.fail("no live session has a bare tool marker to verify against")
    sid, marker_line = target
    rendered = render_session(sid)  # raises if the marker model is wrong (F4)
    assert f"\n{marker_line}\n" not in rendered


def test_cli_writes_well_formed_file_for_recent_session(tmp_path: Path) -> None:
    code = main([str(tmp_path), "--recent", "1"])

    assert code == 0
    written = list(tmp_path.glob("*.xml"))
    assert len(written) == 1
    ET.fromstring(written[0].read_text())  # the file on disk parses
