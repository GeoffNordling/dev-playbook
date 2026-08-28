"""Read what a headless run writes back.

Run with `--output-format stream-json --verbose`, Claude writes one JSON object
per line. The first describes the session it is about to run, and is the only
place it says which account will be billed.
"""

import json
from dataclasses import dataclass


def messages(stdout: str) -> list[dict]:
    """Every JSON object the run wrote, in order."""
    lines = stdout.strip().splitlines()
    if not lines:
        raise ValueError("the run wrote nothing")
    return [json.loads(line) for line in lines]


def find_message(stdout: str, type_: str, subtype: str | None = None) -> dict:
    """The first message of one kind, or a loud failure naming what was there.

    Leave subtype out to match on type alone. The final message is always
    type "result", but its subtype says how the run ended, which is the thing
    being asked about rather than a thing to filter on.
    """
    for message in messages(stdout):
        if message.get("type") != type_:
            continue
        if subtype is None or message.get("subtype") == subtype:
            return message

    kinds = {f"{m.get('type')}/{m.get('subtype')}" for m in messages(stdout)}
    wanted = type_ if subtype is None else f"{type_}/{subtype}"
    raise ValueError(f"no {wanted} message. The run wrote: {sorted(kinds)}")


@dataclass(frozen=True)
class Init:
    """The first line of a run: what the session was set up to be."""

    api_key_source: str
    session_id: str
    model: str
    tools: tuple[str, ...]
    agents: tuple[str, ...]
    skills: tuple[str, ...]


def parse_init(stdout: str) -> Init:
    """The init line of a run.

    Found by searching rather than by position: a session with SessionStart
    hooks reports each one before it reports itself.

    Every field is read by subscript rather than .get(), so a renamed key
    raises here instead of quietly reporting the wrong thing about billing.
    """
    message = find_message(stdout, "system", "init")

    return Init(
        api_key_source=message["apiKeySource"],
        session_id=message["session_id"],
        model=message["model"],
        tools=tuple(message["tools"]),
        agents=tuple(message["agents"]),
        skills=tuple(message["skills"]),
    )


@dataclass(frozen=True)
class Result:
    """The last line of a run: how it ended."""

    subtype: str
    is_error: bool
    num_turns: int
    duration_ms: int
    text: str


def parse_result(stdout: str) -> Result:
    """The result line of a run.

    A run that fails on its own terms — refused a tool, ran out of turns —
    still exits zero, so this is the only place that failure shows up.
    """
    message = find_message(stdout, "result")

    return Result(
        subtype=message["subtype"],
        is_error=message["is_error"],
        num_turns=message["num_turns"],
        duration_ms=message["duration_ms"],
        # Absent when the run ended badly enough to have no answer to give.
        text=message.get("result", ""),
    )


def billed_subscription(init: Init) -> bool:
    """True when the run drew on the subscription rather than a metered key.

    "none" means no API key was in play, which is what a subscription login
    looks like from here.
    """
    return init.api_key_source == "none"
