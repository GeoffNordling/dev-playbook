"""Tests for transcript_export.forks — live path and abandoned branches.

Fixtures are small hand-authored dicts shaped like the documented `messages`
fields, never trimmed real sessions. A fork is two messages sharing a
`source_parent_uuid` with different `source_uuid`s.
"""

import pytest

import transcript_export.forks as forks
from transcript_export.forks import MessageNode, reconstruct_forks
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


def test_simple_fork_collects_abandoned_branch_at_live_sibling() -> None:
    # b and a share parent r; a (ord 10) outranks b (ord 5), so a is the live
    # sibling b was abandoned for. The branch keys under a's uuid, not the parent's.
    messages = [msg(0, "r"), msg(5, "b", "r"), msg(10, "a", "r"), msg(20, "live", "a")]

    result = reconstruct_forks(messages)

    assert set(result.abandoned_branches) == {"a"}
    (head,) = result.abandoned_branches["a"]
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
    # Both abandoned heads converged on the live sibling, so they key under it.
    heads = result.abandoned_branches["live"]
    # Sorted by ordinal: b1 (5) before b2 (8).
    assert [h.message.source_uuid for h in heads] == ["b1", "b2"]


def test_parentless_roots_both_stay_live_not_a_fork() -> None:
    # Two parentless messages are sequential session-roots (e.g. the opening
    # prompt and a first follow-up), NOT a root-level rewind of each other: they
    # name no parent rather than a shared one. Both must stay on the live path,
    # else the first is buried in a <rewound-branch>. A real session that opened
    # with two parentless user rows hit exactly this (see KNOWN-ISSUES).
    messages = [msg(5, "r1"), msg(10, "r2")]

    result = reconstruct_forks(messages)

    assert uuids(result.live_path) == ["r1", "r2"]
    assert result.abandoned_branches == {}


def test_root_level_fork_with_absent_parent_keys_under_live_sibling() -> None:
    # The shared parent "P" is absent from the payload (truncated history); c2
    # (ord 10) is the live sibling, so c1 keys under c2's uuid.
    messages = [msg(5, "c1", "P"), msg(10, "c2", "P")]

    result = reconstruct_forks(messages)

    assert uuids(result.live_path) == ["c2"]
    (head,) = result.abandoned_branches["c2"]
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
    # The outer fork (b1 vs a) keys under its live sibling a.
    (head,) = result.abandoned_branches["a"]
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
    # Each fork keys under its own live sibling: x abandoned for a, y for live.
    assert set(result.abandoned_branches) == {"a", "live"}
    assert result.abandoned_branches["a"][0].message.source_uuid == "x"
    assert result.abandoned_branches["live"][0].message.source_uuid == "y"


def test_conservation_holds_on_multifork_input() -> None:
    # Two forks plus a nested fork: every input uuid must surface exactly once
    # across the live path and the abandoned-branch trees.
    messages = [
        msg(0, "r"),
        msg(5, "b1", "r"),
        msg(6, "b1a", "b1"),
        msg(7, "b1b", "b1"),
        msg(10, "a", "r"),
        msg(15, "y", "a"),
        msg(20, "live", "a"),
    ]

    result = reconstruct_forks(messages)

    seen: list[str] = [u for u in uuids(result.live_path) if u is not None]

    def collect(node: MessageNode) -> None:
        if node.message.source_uuid is not None:
            seen.append(node.message.source_uuid)
        for child in node.children:
            collect(child)

    for heads in result.abandoned_branches.values():
        for head in heads:
            collect(head)

    expected = [m.source_uuid for m in messages if m.source_uuid is not None]
    assert sorted(seen) == sorted(expected)


def test_conservation_violation_fails_loud(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Force the internal segmenter to drop a message; reconstruct_forks must catch
    # the broken partition and raise rather than silently lose it.
    def dropping_segment(
        ordered: list[Message],
    ) -> tuple[list[Message], dict[str, list[MessageNode]]]:
        return ordered[:-1], {}

    monkeypatch.setattr(forks, "_segment", dropping_segment)

    with pytest.raises(ValueError, match="dropped or duplicated"):
        reconstruct_forks([msg(0, "r"), msg(1, "a", "r")])


def test_uuidless_message_fails_loud() -> None:
    # keep_messages drops the uuid-less queued_command previews before fork
    # reconstruction; one reaching here means that contract was broken upstream,
    # so reconstruct_forks raises rather than inventing an identity for it.
    uuidless = message_from_row(
        {"ordinal": 3, "role": "user", "source_type": "user", "content": "orphan"}
    )

    with pytest.raises(ValueError, match="uuid-less"):
        reconstruct_forks([msg(0, "r"), uuidless])


def test_forkfree_stream_with_nonresolving_parents_is_all_live() -> None:
    # Mirrors real data: every message has a distinct parent uuid that resolves to
    # NO message in the set (the parent is an unsurfaced raw record). With no
    # shared parent there is no fork, so the whole stream is the live path. (Under
    # the abandoned parent->uuid tree design this collapsed to one live message and
    # mis-rendered the rest as rewound branches; the ordinal spine fixes it.)
    messages = [
        msg(0, "m0", "p0"),
        msg(1, "m1", "p1"),
        msg(2, "m2", "p2"),
        msg(3, "m3", "p3"),
    ]

    result = reconstruct_forks(messages)

    assert uuids(result.live_path) == ["m0", "m1", "m2", "m3"]
    assert result.abandoned_branches == {}


def test_real_fork_shape_only_shared_parent_amid_nonresolving_parents() -> None:
    # The realistic shape: most messages carry a distinct, non-resolving parent
    # uuid (an unsurfaced raw sub-record); a fork shows up *only* as a parent shared
    # by two messages. Parent "P" is shared by f_old (ord 2) and f_live (ord 4);
    # f_old_kid (ord 3) was written on the abandoned attempt and falls in its range
    # [2, 4). Everything else stays on the live spine in ordinal order.
    messages = [
        msg(0, "m0", "x0"),
        msg(1, "m1", "x1"),
        msg(2, "f_old", "P"),
        msg(3, "f_old_kid", "x2"),
        msg(4, "f_live", "P"),
        msg(5, "m5", "x3"),
    ]

    result = reconstruct_forks(messages)

    assert uuids(result.live_path) == ["m0", "m1", "f_live", "m5"]
    assert set(result.abandoned_branches) == {"f_live"}
    (head,) = result.abandoned_branches["f_live"]
    assert head.message.source_uuid == "f_old"
    # The message written on the abandoned attempt rides the branch as its child.
    assert [child.message.source_uuid for child in head.children] == ["f_old_kid"]
