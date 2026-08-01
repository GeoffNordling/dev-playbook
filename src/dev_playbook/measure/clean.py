"""The four row adjustments a reader of the hook-event store generally wants.

The store records what the harness emitted, which is not the same as what
happened: one skill invocation fires two events, hidden model calls emit
subagent stops for subagents that never ran, the harness submits prompts the
human never typed, and session slots that never materialize still leave a
`SessionStart`. Each technique here removes one of those distortions
([Measurement Prototype](/docs/measurement-prototype.md) names all four and
why).

They are four separate functions rather than one pass because each one is a
judgement a caller may not want, and because each one's count is itself a
finding — the number of phantom stops in a window says something about the
window. Every function returns a `Cleaning`: the frame that survived, and how
many rows it took out. Compose them in the order they appear here; ghost
sessions are only visible once the pseudo-prompts are gone.

Nothing here is destructive to the caller's frame — each function returns a new
one, and none of them ever touches the store.
"""

from dataclasses import dataclass

import pandas as pd

EXPANSION = "UserPromptExpansion"
SUBMIT = "UserPromptSubmit"
SUBAGENT_START = "SubagentStart"
SUBAGENT_STOP = "SubagentStop"

# The two fields an expansion carries and its submit does not: the human's own
# words, already structured. Folding them onto the submit is what makes
# collapsing the pair lossless.
EXPANSION_FIELDS = ("command_name", "command_args")

# The opening marker on a prompt the harness submitted on the human's behalf to
# report a finished background task.
TASK_NOTIFICATION_MARKER = "<task-notification>"


@dataclass(frozen=True)
class Cleaning:
    """What one technique left behind, and what it took out.

    `removed` is a row count, not a count of the things removed: dropping one
    ghost session removes every row that session ever wrote. A caller reporting
    its own blind spots wants both `technique` and `removed`.
    """

    technique: str
    frame: pd.DataFrame
    removed: int


def collapse_expansions(events: pd.DataFrame) -> Cleaning:
    """Fold each `UserPromptExpansion` into the submit that shares its prompt id.

    A typed slash command fires both events, so counting both doubles every
    skill invocation. The submit is the row that survives — it is what proves
    the human was there at that instant, and what a `Stop` pairs with — and it
    gains the expansion's `command_name` and `command_args`. Its own `prompt`
    is left alone, so the literal text stays the text the human submitted.

    An expansion whose submit is not in the frame is left as it is. That is a
    real state, not a defect: a window can cut between the two events, which
    fire microseconds apart, and the expansion is still evidence of one
    submission.
    """
    submitted = set(events.loc[events["event"] == SUBMIT, "prompt_id"])
    expansions = events[events["event"] == EXPANSION]
    paired = expansions[expansions["prompt_id"].isin(submitted)]
    folded = {
        row.prompt_id: {field: row.payload[field] for field in EXPANSION_FIELDS}
        for row in paired.itertuples()
    }
    collapsed = events.drop(index=paired.index).reset_index(drop=True)
    collapsed["payload"] = [
        {**payload, **folded[prompt_id]}
        if event == SUBMIT and prompt_id in folded
        else payload
        for event, prompt_id, payload in zip(
            collapsed["event"],
            collapsed["prompt_id"],
            collapsed["payload"],
            strict=True,
        )
    ]
    return Cleaning("collapse expansion/submit pairs", collapsed, len(paired))


def drop_phantom_subagent_stops(events: pd.DataFrame) -> Cleaning:
    """Drop `SubagentStop` rows that no dispatched subagent produced.

    A phantom is either a stop with an empty `agent_type`, or one whose
    `agent_id` matches no `SubagentStart` in the same session — hidden
    auxiliary model calls emit both shapes, each with its own distinct
    `agent_id` and an `agent_transcript_path` pointing at nothing on disk.

    A window that opens between a real dispatch and its stop strands that stop
    on the second test and drops it. That is the cost of the rule: the store
    carries no other way to tell a stranded stop from a phantom.
    """
    dispatched = {
        (row.session_id, row.payload["agent_id"])
        for row in events[events["event"] == SUBAGENT_START].itertuples()
    }
    stops = events[events["event"] == SUBAGENT_STOP]
    phantoms = [
        row.Index
        for row in stops.itertuples()
        if not row.payload["agent_type"]
        or (row.session_id, row.payload["agent_id"]) not in dispatched
    ]
    kept = events.drop(index=phantoms).reset_index(drop=True)
    return Cleaning("drop phantom SubagentStop", kept, len(phantoms))


def drop_task_notifications(events: pd.DataFrame) -> Cleaning:
    """Drop the submits the harness made on the human's behalf.

    A finished background task is reported by submitting a `<task-notification>`
    prompt into the session, which fires a real `UserPromptSubmit` that no human
    typed. Left in, every one of them is counted as proof the human was at the
    machine at that instant.
    """
    submits = events[events["event"] == SUBMIT]
    notifications = [
        row.Index
        for row in submits.itertuples()
        if row.payload["prompt"].startswith(TASK_NOTIFICATION_MARKER)
    ]
    kept = events.drop(index=notifications).reset_index(drop=True)
    return Cleaning("drop task-notification pseudo-prompts", kept, len(notifications))


def drop_ghost_sessions(events: pd.DataFrame) -> Cleaning:
    """Drop every row of any session that shows no human submission.

    `SessionStart` fires for session slots that never materialize, leaving a
    session id with events but no submission behind it. Run this last: a
    session whose only submits were task notifications is a ghost, and only
    looks like one once those are gone.
    """
    alive = set(events.loc[events["event"] == SUBMIT, "session_id"])
    ghosts = events.index[~events["session_id"].isin(alive)]
    kept = events.drop(index=ghosts).reset_index(drop=True)
    return Cleaning("drop ghost sessions", kept, len(ghosts))
