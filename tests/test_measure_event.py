"""Behavioral tests for the measure-event capture hook's storage trim.

The hook is an extensionless script that runs on every event of every session,
so it is loaded from its path rather than imported. What these cover is
`for_storage`: the payload text one event leaves behind in the store, and in
particular which tools keep an identifier and which keep nothing.
"""

import json
from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import ModuleType

HOOK = (
    Path(__file__).resolve().parents[1]
    / "dotfiles"
    / "dot-claude"
    / "hooks"
    / "measure-event"
)


def load_hook() -> ModuleType:
    """The hook script loaded as a module, by path — it has no `.py` suffix."""
    loader = SourceFileLoader("measure_event", str(HOOK))
    module = ModuleType(loader.name)
    loader.exec_module(module)
    return module


hook = load_hook()


def a_tool_use(tool_name: str, tool_input: object, response: object = "output") -> str:
    """One `PostToolUse` payload as JSON text, with the envelope a real row has."""
    return json.dumps(
        {
            "hook_event_name": "PostToolUse",
            "session_id": "5b1f",
            "cwd": "/home/geoff/workspace/dev-playbook",
            "tool_name": tool_name,
            "duration_ms": 12,
            "tool_input": tool_input,
            "tool_response": response,
        }
    )


# --- tools whose content is kept -------------------------------------------


def test_bash_row_is_stored_verbatim() -> None:
    payload = a_tool_use("Bash", {"command": "gh issue view 272"}, "the output")

    assert hook.for_storage(payload) == payload


# --- tools whose identifier is kept ----------------------------------------


def test_read_row_keeps_the_file_path_and_drops_the_file_text() -> None:
    payload = a_tool_use(
        "Read",
        {"file_path": "/repo/src/a.py", "offset": 1, "limit": 200},
        "line one\nline two\n",
    )

    stored = json.loads(hook.for_storage(payload))

    assert stored["tool_input"] == {"file_path": "/repo/src/a.py"}
    assert "tool_response" not in stored


def test_edit_row_keeps_the_file_path_and_drops_both_sides_of_the_diff() -> None:
    payload = a_tool_use(
        "Edit",
        {"file_path": "/repo/src/a.py", "old_string": "before", "new_string": "after"},
    )

    stored = json.loads(hook.for_storage(payload))

    assert stored["tool_input"] == {"file_path": "/repo/src/a.py"}
    assert "tool_response" not in stored


def test_write_row_keeps_the_file_path_and_drops_the_contents() -> None:
    payload = a_tool_use(
        "Write", {"file_path": "/repo/notes.md", "content": "# notes\n\nbody\n"}
    )

    stored = json.loads(hook.for_storage(payload))

    assert stored["tool_input"] == {"file_path": "/repo/notes.md"}


def test_skill_row_keeps_its_tool_input_whole() -> None:
    payload = a_tool_use("Skill", {"skill": "commit", "args": "--amend"}, "the skill")

    stored = json.loads(hook.for_storage(payload))

    assert stored["tool_input"] == {"skill": "commit", "args": "--amend"}
    assert "tool_response" not in stored


def test_trimmed_row_keeps_every_envelope_key() -> None:
    payload = a_tool_use("Read", {"file_path": "/repo/src/a.py"})

    stored = json.loads(hook.for_storage(payload))

    assert stored["hook_event_name"] == "PostToolUse"
    assert stored["session_id"] == "5b1f"
    assert stored["cwd"] == "/home/geoff/workspace/dev-playbook"
    assert stored["tool_name"] == "Read"
    assert stored["duration_ms"] == 12


# --- tools whose input is dropped whole ------------------------------------


def test_other_tool_row_keeps_the_envelope_alone() -> None:
    payload = a_tool_use("Grep", {"pattern": "def for_storage"}, "12 matches")

    stored = json.loads(hook.for_storage(payload))

    assert "tool_input" not in stored
    assert "tool_response" not in stored
    assert stored["tool_name"] == "Grep"


def test_path_tool_row_keeps_no_input_that_is_not_an_object() -> None:
    payload = a_tool_use("Read", "/repo/src/a.py")

    stored = json.loads(hook.for_storage(payload))

    assert "tool_input" not in stored


def test_path_tool_row_keeps_an_empty_input_when_it_names_no_file() -> None:
    payload = a_tool_use("Read", {"offset": 1})

    stored = json.loads(hook.for_storage(payload))

    assert stored["tool_input"] == {}


# --- payloads no trim applies to -------------------------------------------


def test_non_tool_event_is_stored_verbatim() -> None:
    payload = json.dumps(
        {
            "hook_event_name": "UserPromptSubmit",
            "session_id": "5b1f",
            "prompt": "run the loop",
        }
    )

    assert hook.for_storage(payload) == payload


def test_tool_use_without_a_string_tool_name_is_stored_verbatim() -> None:
    payload = json.dumps(
        {
            "hook_event_name": "PostToolUse",
            "tool_input": {"file_path": "/repo/src/a.py"},
            "tool_response": "line one\n",
        }
    )

    assert hook.for_storage(payload) == payload


def test_unparsable_payload_is_stored_verbatim() -> None:
    payload = '{"hook_event_name": "PostToolUse", truncated'

    assert hook.for_storage(payload) == payload
