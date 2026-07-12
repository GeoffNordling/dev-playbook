"""The sole live-daemon drift canary: render recent real sessions, check well-formed.

Every other transcript_export test is deterministic — hand-built rows through a fake
`agentsview` subprocess, frozen at the daemon's `v0.34.5` shapes. That suite pins
behaviour but can never notice the daemon's output *drifting*: a new version that
changed the marker format or row schema would pass it unchanged. This test is the
one thing that runs the real pipeline over real, current daemon output, so a drift
that breaks a fail-loud guard surfaces here (and, in production, on the first real
export).

It is deliberately **content-independent**: it renders the few most-recent sessions
and asserts only that each is well-formed XML with integral `ord`s — never that a
specific kind of message exists — so it can't flake on which sessions happen to be
in local history. Behavioural assertions (interrupts, bare markers, forks) live in
the deterministic suites, where they can be pinned exactly.

The daemon runs locally only; on GH CI `agentsview` isn't installed, so CI sets
`SKIP_LIVE_TRANSCRIPT=1` and the `pytestmark` below skips this canary (see
.github/workflows/ci.yml). Locally the var is unset, so it runs and fails loud —
an unreachable daemon on this machine is a real fault, not an expected absence.
"""

import os
import xml.etree.ElementTree as ET

import pytest

from dev_playbook.transcript_export.client import session_list
from dev_playbook.transcript_export.transcript import render_session

pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_LIVE_TRANSCRIPT") == "1",
    reason="live transcript tests run locally only; agentsview isn't on GH CI",
)


@pytest.fixture(scope="module")
def recent_ids() -> list[str]:
    """The three newest session ids from the live daemon.

    No defensive guard: if the daemon is unreachable this raises, and the canary
    fails loudly, because on this machine an unreachable daemon is a real fault.
    """
    return [s["id"] for s in session_list(limit=3)]


def test_recent_real_sessions_render_well_formed(recent_ids: list[str]) -> None:
    # Rendering a handful of real sessions exercises the messy realities (forks,
    # compaction, sub-agents, tool output with ANSI control bytes) that hand-built
    # fixtures cannot, and asserts each still produces valid XML with integral ords.
    for sid in recent_ids:
        root = ET.fromstring(render_session(sid))  # raises on malformed output
        assert root.tag == "session"
        assert root.attrib["id"] == sid
        # Every `ord` attribute parses as an int (a comprehension filter, not an
        # `if` branch — see testing.no-logic); int() raises on a malformed value.
        assert all(
            isinstance(int(el.attrib["ord"]), int)
            for el in root.iter()
            if "ord" in el.attrib
        )
