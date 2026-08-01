"""Behavioral tests for the four row-cleaning techniques.

Frames are built in memory here rather than through a fixture database: the
loader has its own tests, and these are about what each technique removes. The
one thing borrowed from the loader is `event_row`, so a frame under test has
exactly the shape `load_events` produces.
"""

import json
from collections.abc import Callable

import pandas as pd
import pytest

from dev_playbook.measure import clean, store

BASE = pd.Timestamp("2026-07-28T19:00:00Z")

# The three fields a typed slash command puts on its expansion row.
A_COMMAND = {"command_name": "commit", "command_args": "now", "prompt": "/commit now"}


def a_payload(event: str, session: str = "5b1f", **fields: object) -> dict:
    """One hook payload with the envelope every real row carries."""
    return {
        "hook_event_name": event,
        "session_id": session,
        "transcript_path": f"/home/geoff/.claude/projects/p/{session}.jsonl",
        "cwd": "/home/geoff/workspace/dev-playbook",
        **fields,
    }


def a_frame(payloads: list[dict]) -> pd.DataFrame:
    """The loader's output shape, one row per payload, a second apart in order."""
    records = [
        store.event_row(
            index, (BASE + pd.Timedelta(seconds=index)).isoformat(), json.dumps(payload)
        )
        for index, payload in enumerate(payloads, start=1)
    ]
    frame = pd.DataFrame(records, columns=list(store.COLUMNS), dtype=object)
    frame["received_at"] = pd.to_datetime(
        frame["received_at"], utc=True, format="ISO8601"
    )
    frame["id"] = frame["id"].astype("int64")
    return frame


# --- collapsing expansion/submit pairs ---------------------------------------


def test_collapse_expansions_leaves_one_row_per_slash_command() -> None:
    events = a_frame(
        [
            a_payload("UserPromptExpansion", prompt_id="p-1", **A_COMMAND),
            a_payload("UserPromptSubmit", prompt_id="p-1", prompt="/commit now"),
        ]
    )

    cleaning = clean.collapse_expansions(events)

    assert list(cleaning.frame["event"]) == ["UserPromptSubmit"]
    assert cleaning.removed == 1


def test_collapse_expansions_moves_the_structured_command_onto_the_submit() -> None:
    events = a_frame(
        [
            a_payload("UserPromptExpansion", prompt_id="p-1", **A_COMMAND),
            a_payload("UserPromptSubmit", prompt_id="p-1", prompt="/commit now"),
        ]
    )

    payload = clean.collapse_expansions(events).frame.iloc[0]["payload"]

    assert payload["command_name"] == "commit"
    assert payload["command_args"] == "now"


def test_collapse_expansions_keeps_the_text_the_human_submitted() -> None:
    events = a_frame(
        [
            a_payload(
                "UserPromptExpansion",
                prompt_id="p-1",
                command_name="commit",
                command_args="now",
                prompt="/commit now — expanded",
            ),
            a_payload("UserPromptSubmit", prompt_id="p-1", prompt="/commit now"),
        ]
    )

    payload = clean.collapse_expansions(events).frame.iloc[0]["payload"]

    assert payload["prompt"] == "/commit now"


def test_collapse_expansions_leaves_the_stop_sharing_the_prompt_id_alone() -> None:
    events = a_frame(
        [
            a_payload("UserPromptExpansion", prompt_id="p-1", **A_COMMAND),
            a_payload("UserPromptSubmit", prompt_id="p-1", prompt="/commit now"),
            a_payload("Stop", prompt_id="p-1", last_assistant_message="done"),
        ]
    )

    stop = clean.collapse_expansions(events).frame.iloc[1]["payload"]

    assert "command_name" not in stop


def test_collapse_expansions_keeps_an_expansion_with_no_submit_beside_it() -> None:
    events = a_frame([a_payload("UserPromptExpansion", prompt_id="p-1", **A_COMMAND)])

    cleaning = clean.collapse_expansions(events)

    assert list(cleaning.frame["event"]) == ["UserPromptExpansion"]
    assert cleaning.removed == 0


def test_collapse_expansions_does_not_touch_the_frame_it_was_given() -> None:
    events = a_frame(
        [
            a_payload("UserPromptExpansion", prompt_id="p-1", **A_COMMAND),
            a_payload("UserPromptSubmit", prompt_id="p-1", prompt="/commit now"),
        ]
    )

    clean.collapse_expansions(events)

    assert len(events) == 2
    assert "command_name" not in events.iloc[1]["payload"]


# --- phantom subagent stops --------------------------------------------------


def test_drop_phantom_subagent_stops_drops_a_stop_with_no_agent_type() -> None:
    events = a_frame(
        [
            a_payload("SubagentStop", agent_id="a-1", agent_type=""),
            a_payload("UserPromptSubmit", prompt_id="p-1", prompt="go"),
        ]
    )

    cleaning = clean.drop_phantom_subagent_stops(events)

    assert list(cleaning.frame["event"]) == ["UserPromptSubmit"]
    assert cleaning.removed == 1


def test_drop_phantom_subagent_stops_keeps_a_stop_matching_a_dispatch() -> None:
    events = a_frame(
        [
            a_payload("SubagentStart", agent_id="a-1", agent_type="general-purpose"),
            a_payload("SubagentStop", agent_id="a-1", agent_type="general-purpose"),
        ]
    )

    cleaning = clean.drop_phantom_subagent_stops(events)

    assert list(cleaning.frame["event"]) == ["SubagentStart", "SubagentStop"]
    assert cleaning.removed == 0


def test_drop_phantom_subagent_stops_drops_a_stop_matching_no_dispatch() -> None:
    events = a_frame(
        [
            a_payload("SubagentStart", agent_id="a-1", agent_type="general-purpose"),
            a_payload("SubagentStop", agent_id="a-2", agent_type="general-purpose"),
        ]
    )

    cleaning = clean.drop_phantom_subagent_stops(events)

    assert list(cleaning.frame["event"]) == ["SubagentStart"]


def test_drop_phantom_subagent_stops_matches_a_dispatch_in_the_same_session() -> None:
    events = a_frame(
        [
            a_payload(
                "SubagentStart", session="aaa", agent_id="a-1", agent_type="Explore"
            ),
            a_payload(
                "SubagentStop", session="bbb", agent_id="a-1", agent_type="Explore"
            ),
        ]
    )

    cleaning = clean.drop_phantom_subagent_stops(events)

    assert list(cleaning.frame["event"]) == ["SubagentStart"]
    assert cleaning.technique == "drop phantom SubagentStop"


# --- task-notification pseudo-prompts ----------------------------------------


def test_drop_task_notifications_drops_a_submit_the_harness_made() -> None:
    events = a_frame(
        [
            a_payload(
                "UserPromptSubmit",
                prompt_id="p-1",
                prompt="<task-notification>\n<task-id>a92</task-id>\n",
            ),
            a_payload("UserPromptSubmit", prompt_id="p-2", prompt="carry on"),
        ]
    )

    cleaning = clean.drop_task_notifications(events)

    assert [payload["prompt"] for payload in cleaning.frame["payload"]] == ["carry on"]
    assert cleaning.removed == 1


def test_drop_task_notifications_keeps_a_prompt_that_mentions_the_marker() -> None:
    events = a_frame(
        [
            a_payload(
                "UserPromptSubmit",
                prompt_id="p-1",
                prompt="what does <task-notification> mean?",
            )
        ]
    )

    cleaning = clean.drop_task_notifications(events)

    assert len(cleaning.frame) == 1
    assert cleaning.removed == 0


# --- ghost sessions ----------------------------------------------------------


def test_drop_ghost_sessions_drops_every_row_of_a_silent_session() -> None:
    events = a_frame(
        [
            a_payload("SessionStart", session="ghost", source="startup"),
            a_payload("Notification", session="ghost", notification_type="idle_prompt"),
            a_payload("SessionStart", session="real", source="startup"),
            a_payload("UserPromptSubmit", session="real", prompt_id="p-1", prompt="go"),
        ]
    )

    cleaning = clean.drop_ghost_sessions(events)

    assert set(cleaning.frame["session_id"]) == {"real"}
    assert cleaning.removed == 2


def test_drop_ghost_sessions_counts_rows_not_sessions() -> None:
    events = a_frame(
        [
            a_payload("SessionStart", session="ghost", source="startup"),
            a_payload("SessionEnd", session="ghost", reason="other"),
            a_payload("SessionStart", session="other-ghost", source="startup"),
        ]
    )

    cleaning = clean.drop_ghost_sessions(events)

    assert len(cleaning.frame) == 0
    assert cleaning.removed == 3


# --- the four together -------------------------------------------------------


@pytest.mark.parametrize(
    "technique",
    [
        clean.collapse_expansions,
        clean.drop_phantom_subagent_stops,
        clean.drop_task_notifications,
        clean.drop_ghost_sessions,
    ],
)
def test_a_technique_over_an_empty_window_removes_nothing(
    technique: Callable[[pd.DataFrame], clean.Cleaning],
) -> None:
    cleaning = technique(a_frame([]))

    assert len(cleaning.frame) == 0
    assert cleaning.removed == 0


def test_the_four_in_order_leave_what_a_human_and_a_real_agent_did() -> None:
    events = a_frame(
        [
            a_payload("SessionStart", session="ghost", source="startup"),
            a_payload(
                "UserPromptSubmit",
                session="ghost",
                prompt_id="p-0",
                prompt="<task-notification>\n<task-id>a92</task-id>\n",
            ),
            a_payload("UserPromptExpansion", prompt_id="p-1", **A_COMMAND),
            a_payload("UserPromptSubmit", prompt_id="p-1", prompt="/commit now"),
            a_payload("SubagentStop", agent_id="a-9", agent_type=""),
            a_payload("Stop", prompt_id="p-1", last_assistant_message="done"),
        ]
    )

    collapsed = clean.collapse_expansions(events).frame
    dispatched = clean.drop_phantom_subagent_stops(collapsed).frame
    typed = clean.drop_task_notifications(dispatched).frame
    cleaned = clean.drop_ghost_sessions(typed).frame

    assert list(cleaned["event"]) == ["UserPromptSubmit", "Stop"]
    assert cleaned.iloc[0]["payload"]["command_name"] == "commit"
