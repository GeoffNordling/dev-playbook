"""End-to-end tests: a whole synthetic session through `render_session` / the CLI.

The per-module suites pin each pipeline stage in isolation; these drive a complete
session — interrupt, compaction, a rewind fork, tool output with ANSI + truncation,
and a nested sub-agent — through the impure orchestrator against a fake AgentsView
daemon, asserting the assembled document is well-formed and its parts land in order.
Fixtures are hand-authored rows in the documented shape, never trimmed real sessions.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

from transcript_fakes import (
    INTERRUPT_CONTENT,
    assistant_row,
    fake_daemon,
    system_row,
    tc_row,
    user_row,
)

from transcript_export.cli import main
from transcript_export.transcript import render_session

# A long tool body prefixed with a raw ANSI escape: it trips truncation (> 2000)
# and forces the illegal-byte strip. `chars` must still report the true length.
_ANSI_LONG_OUTPUT = "\x1b[31m" + "z" * 2100
_ANSI_LONG_LENGTH = len(_ANSI_LONG_OUTPUT)


def rich_session() -> dict[str, dict]:
    """One session that exercises every timeline element plus a nested sub-agent.

    Ordinals are sparse (as in real data). `f_old`/`f_live` share the concrete
    parent `P` — a rewind — so `f_old` (lower ordinal) is the abandoned branch and
    `f_live` (higher) stays live and spawns the child. Every other row is parentless
    and stays on the live spine in ordinal order.
    """
    return {
        "parent": {
            "meta": {"id": "parent", "project": "demo", "message_count": 7},
            "rows": [
                user_row(ordinal=1, source_uuid="u0", content="start the task"),
                assistant_row(
                    ordinal=2,
                    source_uuid="a1",
                    source_parent_uuid="u0",
                    content="Planning, then running.",
                    thinking_text="which file first",
                    tool_calls=[
                        tc_row(
                            tool_name="Bash",
                            tool_use_id="t_bash",
                            input_json='{"command": "./run"}',
                            result_content=_ANSI_LONG_OUTPUT,
                        )
                    ],
                ),
                system_row(
                    ordinal=3,
                    source_uuid="i1",
                    source_subtype="interrupted",
                    content=INTERRUPT_CONTENT,
                ),
                assistant_row(
                    ordinal=5,
                    source_uuid="f_old",
                    source_parent_uuid="P",
                    content="first attempt",
                ),
                assistant_row(
                    ordinal=6,
                    source_uuid="f_live",
                    source_parent_uuid="P",
                    content="second attempt",
                    tool_calls=[tc_row(tool_name="Agent", subagent_session_id="child")],
                ),
                system_row(
                    ordinal=7,
                    source_uuid="c1",
                    source_subtype="compact_boundary",
                    content="summary so far",
                ),
                assistant_row(ordinal=8, source_uuid="a2", content="done"),
            ],
        },
        "child": {
            "meta": {"id": "child", "message_count": 1},
            "rows": [assistant_row(ordinal=1, source_uuid="c0", content="child reply")],
        },
    }


def test_full_session_renders_every_element_in_order() -> None:
    el = ET.fromstring(render_session("parent", runner=fake_daemon(rich_session())))

    assert el.tag == "session"
    assert el.attrib["id"] == "parent"
    assert [k.tag for k in el] == [
        "user",
        "assistant",
        "interrupted",
        "rewound-branch",
        "assistant",
        "compaction",
        "assistant",
    ]


def test_full_session_assistant_carries_thinking_and_truncated_ansi_output() -> None:
    el = ET.fromstring(render_session("parent", runner=fake_daemon(rich_session())))
    assistant = el.findall("assistant")[0]

    # With a <thinking> child, the prose is that element's tail, not assistant.text.
    assert assistant.find("thinking").text == "which file first"  # type: ignore[union-attr]
    assert assistant.find("thinking").tail == "Planning, then running."  # type: ignore[union-attr]
    out = assistant.find("tool-call/output")
    assert out is not None
    assert out.attrib["truncated"] == "true"
    assert out.attrib["chars"] == str(_ANSI_LONG_LENGTH)
    assert "\x1b" not in (out.text or "")  # the raw ANSI escape was stripped


def test_full_session_interrupt_and_compaction_survive() -> None:
    el = ET.fromstring(render_session("parent", runner=fake_daemon(rich_session())))

    assert el.find("interrupted").attrib == {"ord": "3"}  # type: ignore[union-attr]
    assert el.find("compaction").text == "summary so far"  # type: ignore[union-attr]


def test_full_session_rewound_branch_precedes_its_live_sibling() -> None:
    el = ET.fromstring(render_session("parent", runner=fake_daemon(rich_session())))

    # The abandoned attempt renders as <rewound-branch> just before the live sibling.
    assert el.find("rewound-branch/assistant").text == "first attempt"  # type: ignore[union-attr]
    live = el.findall("assistant")[1]
    assert live.text == "second attempt"


def test_full_session_nests_subagent_under_the_live_sibling() -> None:
    el = ET.fromstring(render_session("parent", runner=fake_daemon(rich_session())))

    sub = el.findall("assistant")[1].find("tool-call/subagent")
    assert sub is not None
    assert sub.attrib == {"id": "child", "messages": "1"}
    assert sub.find("assistant").text == "child reply"  # type: ignore[union-attr]


def test_cli_writes_a_real_rendered_file(tmp_path: Path) -> None:
    # main() with the real render_session and a fake daemon: the file on disk must
    # parse and carry the interrupt + sub-agent the pipeline produced.
    code = main([str(tmp_path), "parent"], runner=fake_daemon(rich_session()))

    assert code == 0
    written = (tmp_path / "parent.xml").read_text()
    root = ET.fromstring(written)
    assert root.attrib["id"] == "parent"
    assert "<interrupted" in written
    assert "<subagent" in written


def test_resume_reemissions_collapse_across_the_whole_pipeline() -> None:
    # A resumed session replays earlier rows with the *same* source_uuid at higher
    # ordinals; rule 1 must drop them so each turn renders once.
    sessions = {
        "s1": {
            "meta": {"id": "s1", "message_count": 2},
            "rows": [
                user_row(ordinal=1, source_uuid="u0", content="hello"),
                assistant_row(
                    ordinal=2, source_uuid="a1", source_parent_uuid="u0", content="hi"
                ),
                # Resume replays both verbatim under the same uuids.
                user_row(ordinal=8, source_uuid="u0", content="hello"),
                assistant_row(
                    ordinal=9, source_uuid="a1", source_parent_uuid="u0", content="hi"
                ),
            ],
        }
    }

    el = ET.fromstring(render_session("s1", runner=fake_daemon(sessions)))

    assert [k.tag for k in el] == ["user", "assistant"]
    assert el.find("user").text == "hello"  # type: ignore[union-attr]
    assert el.find("assistant").text == "hi"  # type: ignore[union-attr]
