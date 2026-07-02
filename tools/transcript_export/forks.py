"""Rewind-fork reconstruction over the normalized message list.

Claude Code records an edit/rewind as a *fork*. On the parsed AgentsView messages
API the fork surfaces as a **shared `source_parent_uuid`**: two or more messages
name the same parent. The parent itself is usually an *unsurfaced raw sub-record*
(a tool result folded into the previous message), so it is NOT a message we can
see — an earlier design that chased a `source_parent_uuid`→`source_uuid` tree
never connected on real data (the parent resolved to a message ~0% of the time)
and is abandoned.

The live transcript is therefore just the messages in **ordinal order**: writing
only ever continues on the live branch with ever-increasing global ordinals, so
the most recent write under any fork — the **highest-ordinal sibling** — is the
one that stayed live. Each *lower*-ordinal sibling heads an abandoned branch that
occupies the contiguous ordinal range from that sibling up to the next sibling
under the same parent. Those ranges are carved out of the spine and render as
`<rewound-branch>` just before the live sibling that superseded them. A fork
nested inside an abandoned range is handled by the same logic recursively and is
preserved as the branch head's `children`.
"""

from dataclasses import dataclass

from transcript_export.model import Message


@dataclass(frozen=True)
class MessageNode:
    """A message and the branch that continues from it, for an abandoned branch.

    Abandoned branches render in full fidelity. The `children` are ordinal-sorted:
    the highest-ordinal child is the inline continuation of this branch, and every
    lower-ordinal child is a fork *nested inside* the abandoned branch (a rewind
    within a rewound branch), which renders as its own nested `<rewound-branch>`.
    A linear branch is a chain of single-child nodes.
    """

    message: Message
    children: tuple[MessageNode, ...]


@dataclass(frozen=True)
class ForkReconstruction:
    """The live path plus the abandoned branches that fork off it.

    `live_path` is the messages in ordinal order with every abandoned range removed
    — the transcript a reader follows top to bottom. `abandoned_branches` maps a
    **live message's `source_uuid`** to the abandoned branch heads that converged
    on it (the lower-ordinal siblings it superseded), ordinal-ordered; each renders
    as a `<rewound-branch>` immediately *before* that live message.
    """

    live_path: tuple[Message, ...]
    abandoned_branches: dict[str, tuple[MessageNode, ...]]


@dataclass(frozen=True)
class _AbandonedRange:
    """One abandoned branch: a lower-ordinal sibling and the ordinal range it owns.

    `head` is the abandoned sibling; the branch is every message with ordinal in
    `[start, end)` (`start` = `head.ordinal`, `end` = the next sibling's ordinal
    under the same parent). `live_uuid` is the `source_uuid` of the highest-ordinal
    sibling — the live message this branch was abandoned in favour of.
    """

    head: Message
    start: int
    end: int
    live_uuid: str


def _uuid(message: Message) -> str:
    """The message's `source_uuid`, failing loud if it is absent.

    Fork reconstruction runs on the kept list, where the uuid-less
    `queued_command` previews have already been dropped (`keep_messages`). A None
    here means that contract was violated upstream, so we raise rather than invent
    an identity — a uuid-less node would otherwise masquerade as a branch head and
    render as a spurious rewound branch.
    """
    if message.source_uuid is None:
        raise ValueError(
            f"reconstruct_forks got a uuid-less message at ordinal "
            f"{message.ordinal}; queued_command rows must be dropped first"
        )
    return message.source_uuid


def reconstruct_forks(messages: list[Message]) -> ForkReconstruction:
    """Split the message list into its live path and abandoned branches.

    Expects the kept list from `keep_messages` (one message per `source_uuid`,
    uuid-less `queued_command` previews already dropped). Sorts by ordinal — the
    live spine — and carves out the abandoned ranges that fork off it. Returns an
    empty reconstruction for an empty list.
    """
    if not messages:
        return ForkReconstruction(live_path=(), abandoned_branches={})

    for message in messages:
        _uuid(message)
    ordered = sorted(messages, key=lambda m: (m.ordinal, _uuid(m)))

    spine, abandoned = _segment(ordered)
    reconstruction = ForkReconstruction(
        live_path=tuple(spine),
        abandoned_branches={uuid: tuple(heads) for uuid, heads in abandoned.items()},
    )
    _assert_conserved(reconstruction, ordered)
    return reconstruction


def _branch_uuids(node: MessageNode) -> list[str]:
    """Every `source_uuid` in an abandoned branch, head plus all descendants."""
    result = [_uuid(node.message)]
    for child in node.children:
        result.extend(_branch_uuids(child))
    return result


def _assert_conserved(
    reconstruction: ForkReconstruction, inputs: list[Message]
) -> None:
    """Fail loud unless every input message lands in exactly one output slot.

    Partitioning into the live path and abandoned branches must neither drop nor
    duplicate any message: the multiset of output `source_uuid`s must equal the
    input set exactly. A mis-partition (an unexpected/crossing fork shape) would
    otherwise silently lose or repeat messages — raise instead.
    """
    output: list[str] = [_uuid(m) for m in reconstruction.live_path]
    for heads in reconstruction.abandoned_branches.values():
        for head in heads:
            output.extend(_branch_uuids(head))

    expected = sorted(_uuid(m) for m in inputs)
    if sorted(output) != expected:
        raise ValueError(
            "reconstruct_forks dropped or duplicated messages: "
            f"input uuids {expected} != output uuids {sorted(output)}"
        )


def _segment(
    ordered: list[Message],
) -> tuple[list[Message], dict[str, list[MessageNode]]]:
    """Split an ordinal-sorted message slice into its live spine and branches.

    `ordered` is already sorted by ordinal. Returns the live messages (ordinal
    order, every abandoned range removed) and a map from each live sibling's
    `source_uuid` to the abandoned branch heads that converged on it, ordinal
    ordered. Used both at the top level and recursively inside an abandoned range,
    where a *nested* fork is detected and split out the same way.
    """
    ranges = _outermost(_abandoned_ranges(ordered))

    def is_covered(ordinal: int) -> bool:
        return any(rng.start <= ordinal < rng.end for rng in ranges)

    spine = [message for message in ordered if not is_covered(message.ordinal)]

    abandoned: dict[str, list[MessageNode]] = {}
    for rng in sorted(ranges, key=lambda r: r.head.ordinal):
        branch_msgs = [m for m in ordered if rng.start <= m.ordinal < rng.end]
        abandoned.setdefault(rng.live_uuid, []).append(_build_branch(branch_msgs))
    return spine, abandoned


def _abandoned_ranges(ordered: list[Message]) -> list[_AbandonedRange]:
    """The abandoned ranges implied by every shared-parent fork in `ordered`.

    A *concrete* parent shared by ≥2 messages is a fork; its highest-ordinal
    sibling stays live and each lower sibling heads a range running up to the
    next sibling. Parentless messages (`source_parent_uuid is None`) are skipped:
    they are sequential session-roots that name *no* parent, not rewind siblings
    of one another, so treating them as a fork would bury the opening message in
    a `<rewound-branch>`. A genuine root-level fork still shares a concrete parent
    uuid even when that parent is absent from the payload.
    """
    siblings_by_parent: dict[str | None, list[Message]] = {}
    for message in ordered:
        siblings_by_parent.setdefault(message.source_parent_uuid, []).append(message)

    ranges: list[_AbandonedRange] = []
    for parent, siblings in siblings_by_parent.items():
        if parent is None or len(siblings) < 2:
            continue
        ordered_siblings = sorted(siblings, key=lambda m: m.ordinal)
        live_uuid = _uuid(ordered_siblings[-1])
        for head, nxt in zip(ordered_siblings, ordered_siblings[1:], strict=False):
            ranges.append(
                _AbandonedRange(
                    head=head,
                    start=head.ordinal,
                    end=nxt.ordinal,
                    live_uuid=live_uuid,
                )
            )
    return ranges


def _outermost(ranges: list[_AbandonedRange]) -> list[_AbandonedRange]:
    """The ranges not nested inside another range (by head ordinal).

    A range whose head falls within another range belongs to that outer branch and
    is rebuilt when that branch recurses, so only the outermost ranges are carved
    out of this level's spine. The outermost ranges are pairwise disjoint.
    """
    return [
        rng
        for rng in ranges
        if not any(
            other is not rng and other.start <= rng.head.ordinal < other.end
            for other in ranges
        )
    ]


def _build_branch(branch_msgs: list[Message]) -> MessageNode:
    """Build the `MessageNode` for one abandoned branch (a contiguous ordinal range).

    The range's lowest-ordinal message is the branch head. Recurses to split out
    any fork nested inside the range, then threads the sub-spine into one chain
    whose nested forks hang as the appropriate node's earlier children.
    """
    spine, abandoned = _segment(branch_msgs)
    return _chain(spine, abandoned)


def _chain(
    spine: list[Message], abandoned: dict[str, list[MessageNode]]
) -> MessageNode:
    """Link an ordinal-ordered spine into one `MessageNode` chain.

    Each spine message continues into the next as that node's highest-ordinal
    child; the abandoned branches keyed at the next message hang as the earlier
    children, so they render as `<rewound-branch>` right before the continuation —
    the same live/abandoned split as the top level, one level down. The spine is
    non-empty (its head is the branch head) and the head never carries branches
    before it.
    """
    node: MessageNode | None = None
    for index in range(len(spine) - 1, -1, -1):
        message = spine[index]
        children: list[MessageNode] = []
        if node is not None:
            children.extend(abandoned.get(_uuid(spine[index + 1]), []))
            children.append(node)
        node = MessageNode(message, tuple(children))
    if node is None:
        raise ValueError("cannot build a branch from an empty range")
    return node
