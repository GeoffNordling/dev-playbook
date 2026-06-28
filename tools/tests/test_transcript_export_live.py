"""Live-daemon integration tests: render real sessions end to end.

Unlike every other transcript_export test (which mocks the `agentsview`
subprocess), these drive the always-on local AgentsView daemon for real. They
exercise the three read commands the tool uses — `session list` / `get` /
`messages` — and assert *structural* invariants only (well-formed XML, header
present, ord attributes integral), never exact content: real sessions change.

The whole module skips when no daemon is reachable, so the check gate stays green
on a machine without AgentsView (e.g. CI). That is an explicit, reasoned skip —
the data genuinely is not available — not a silent fallback.
"""

import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from transcript_export.cli import main
from transcript_export.client import session_get, session_list, session_messages
from transcript_export.transcript import render_session


def _recent_ids(limit: int) -> list[str]:
    """The newest session ids from the live daemon, or [] if it is unreachable."""
    if shutil.which("agentsview") is None:
        return []
    try:
        sessions = session_list()["sessions"]
    except Exception:
        return []
    return [s["id"] for s in sessions[:limit]]


_RECENT = _recent_ids(3)

pytestmark = pytest.mark.skipif(
    not _RECENT, reason="AgentsView daemon not reachable; skipping live integration"
)


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


def test_cli_writes_well_formed_file_for_recent_session(tmp_path: Path) -> None:
    code = main([str(tmp_path), "--recent", "1"])

    assert code == 0
    written = list(tmp_path.glob("*.xml"))
    assert len(written) == 1
    ET.fromstring(written[0].read_text())  # the file on disk parses
