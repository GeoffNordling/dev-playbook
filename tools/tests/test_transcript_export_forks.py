"""Tests for transcript_export.forks — live path and abandoned branches.

Fixtures are small hand-authored dicts shaped like the documented `messages`
fields, never trimmed real sessions. A fork is two messages sharing a
`source_parent_uuid` with different `source_uuid`s.
"""

import pytest

from transcript_export.forks import reconstruct_forks
from transcript_export.model import Message, message_from_row


def msg(ordinal: int, uuid: str, parent: str | None = None) -> Message:
    """A message at `ordinal` with `source_uuid`/`source_parent_uuid` set."""
    raw: dict = {
        "ordinal": ordinal,
        "role": "assistant",
        "source_type": "assistant",
        "source_uuid": uuid,
        "content": "c",
    }
    if parent is not None:
        raw["source_parent_uuid"] = parent
    return message_from_row(raw)


def uuids(messages: tuple[Message, ...]) -> list[str | None]:
    return [m.source_uuid for m in messages]


def test_empty_input_yields_empty_reconstruction() -> None:
    result = reconstruct_forks([])

    assert result.live_path == ()
    assert result.abandoned_branches == {}


def test_linear_chain_is_all_live_no_branches() -> None:
    messages = [msg(0, "r"), msg(1, "a", "r"), msg(2, "b", "a")]

    result = reconstruct_forks(messages)

    assert uuids(result.live_path) == ["r", "a", "b"]
    assert result.abandoned_branches == {}


def test_live_path_is_root_to_tip_of_highest_ordinal() -> None:
    # The abandoned branch (b, ord 5) freezes below the live tip (live, ord 20).
    messages = [msg(0, "r"), msg(5, "b", "r"), msg(10, "a", "r"), msg(20, "live", "a")]

    result = reconstruct_forks(messages)

    assert uuids(result.live_path) == ["r", "a", "live"]


def test_simple_fork_collects_abandoned_branch_at_parent() -> None:
    messages = [msg(0, "r"), msg(5, "b", "r"), msg(10, "a", "r"), msg(20, "live", "a")]

    result = reconstruct_forks(messages)

    assert set(result.abandoned_branches) == {"r"}
    (head,) = result.abandoned_branches["r"]
    assert head.message.source_uuid == "b"
    assert head.children == ()


def test_three_way_rewind_keeps_two_abandoned_at_one_fork_point() -> None:
    # One fork point (r) with three children: one live, two abandoned.
    messages = [
        msg(0, "r"),
        msg(5, "b1", "r"),
        msg(8, "b2", "r"),
        msg(20, "live", "r"),
    ]

    result = reconstruct_forks(messages)

    assert uuids(result.live_path) == ["r", "live"]
    heads = result.abandoned_branches["r"]
    # Sorted by ordinal: b1 (5) before b2 (8).
    assert [h.message.source_uuid for h in heads] == ["b1", "b2"]


def test_root_level_fork_with_no_parent_keys_under_none() -> None:
    # Two roots, no parent; the higher-ordinal one is the live branch head.
    messages = [msg(5, "r1"), msg(10, "r2")]

    result = reconstruct_forks(messages)

    assert uuids(result.live_path) == ["r2"]
    (head,) = result.abandoned_branches[None]
    assert head.message.source_uuid == "r1"


def test_root_level_fork_with_absent_parent_keys_under_that_uuid() -> None:
    # The shared parent "P" is absent from the payload (truncated history); each
    # present child roots its own branch.
    messages = [msg(5, "c1", "P"), msg(10, "c2", "P")]

    result = reconstruct_forks(messages)

    assert uuids(result.live_path) == ["c2"]
    (head,) = result.abandoned_branches["P"]
    assert head.message.source_uuid == "c1"


def test_nested_fork_inside_abandoned_branch_is_preserved() -> None:
    # The abandoned branch b1 itself forks into b1a and b1b.
    messages = [
        msg(0, "r"),
        msg(5, "b1", "r"),
        msg(6, "b1a", "b1"),
        msg(7, "b1b", "b1"),
        msg(10, "a", "r"),
        msg(20, "live", "a"),
    ]

    result = reconstruct_forks(messages)

    assert uuids(result.live_path) == ["r", "a", "live"]
    (head,) = result.abandoned_branches["r"]
    assert head.message.source_uuid == "b1"
    # The nested fork survives as the abandoned head's children, ordinal-sorted.
    assert [child.message.source_uuid for child in head.children] == ["b1a", "b1b"]
    assert all(child.children == () for child in head.children)


def test_stacked_forks_collect_one_branch_per_live_fork_point() -> None:
    # Fork points at r (-> x) and at a (-> y), both along the live path.
    messages = [
        msg(0, "r"),
        msg(5, "x", "r"),
        msg(10, "a", "r"),
        msg(15, "y", "a"),
        msg(20, "live", "a"),
    ]

    result = reconstruct_forks(messages)

    assert uuids(result.live_path) == ["r", "a", "live"]
    assert set(result.abandoned_branches) == {"r", "a"}
    assert result.abandoned_branches["r"][0].message.source_uuid == "x"
    assert result.abandoned_branches["a"][0].message.source_uuid == "y"


def test_uuidless_message_fails_loud() -> None:
    # keep_messages drops the uuid-less queued_command previews before fork
    # reconstruction; one reaching here means that contract was broken upstream,
    # so reconstruct_forks raises rather than inventing an identity for it.
    uuidless = message_from_row(
        {"ordinal": 3, "role": "user", "source_type": "user", "content": "orphan"}
    )

    with pytest.raises(ValueError, match="uuid-less"):
        reconstruct_forks([msg(0, "r"), uuidless])


@pytest.mark.xfail(
    reason="KNOWN DEFECT (T12): on the real parsed messages API source_parent_uuid "
    "points to raw sub-records (tool results) that are folded into messages and "
    "never surfaced, so the parent->uuid tree never connects. The live-path walk "
    "then collapses to the single highest-ordinal message and every other message "
    "is mis-rendered as a <rewound-branch>. A fork-free stream must yield a full "
    "live path and zero abandoned branches; reconstruct_forks needs an "
    "ordinal-spine redesign. See PLAN.md T12.",
    strict=True,
)
def test_forkfree_stream_with_nonresolving_parents_is_all_live() -> None:
    # Mirrors real data: every message has a distinct parent uuid that resolves to
    # NO message in the set (the parent is an unsurfaced raw record). With no
    # shared parent there is no fork, so the whole stream is the live path.
    messages = [
        msg(0, "m0", "p0"),
        msg(1, "m1", "p1"),
        msg(2, "m2", "p2"),
        msg(3, "m3", "p3"),
    ]

    result = reconstruct_forks(messages)

    assert uuids(result.live_path) == ["m0", "m1", "m2", "m3"]
    assert result.abandoned_branches == {}
