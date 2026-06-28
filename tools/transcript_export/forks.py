"""Rewind-fork reconstruction over the normalized message list.

Claude Code records an edit/rewind as a *fork*: two messages share a
`source_parent_uuid` but carry different `source_uuid`s. Writing only ever
continues on the live branch, so the most-recently-written message (highest
ordinal) sits at the tip of the live path; every other subtree hanging off a
fork point is an abandoned branch that a later task renders inside
`<rewound-branch>`.

`reconstruct_forks` builds the `source_parent_uuid`→`source_uuid` tree, walks the
ancestor chain of the highest-ordinal message to get the live path, and groups
the abandoned branch heads by the fork point they hang from. A fork's common
parent may be absent from the payload (truncated history); each present child is
then rooted as its own branch head and the missing parent uuid becomes the group
key. It is a plain tree walk, so it generalizes to nested and stacked forks; see
PLAN.md for the authoritative design.
"""

from dataclasses import dataclass

from transcript_export.model import Message


@dataclass(frozen=True)
class MessageNode:
    """A message and its children in the `source_parent_uuid`→`source_uuid` tree.

    Used for abandoned branches, which render in full fidelity: a node's
    `children` preserve any forks *inside* the abandoned subtree (a nested fork),
    sorted by ordinal.
    """

    message: Message
    children: tuple[MessageNode, ...]


@dataclass(frozen=True)
class ForkReconstruction:
    """The live path plus the abandoned branches that fork off it.

    `live_path` is the root→tip ancestor chain of the highest-ordinal message.
    `abandoned_branches` maps a fork point to the abandoned subtree roots hanging
    there: the key is the `source_uuid` of the live-path message they fork off,
    or — when the common parent is absent from the payload — that absent parent
    uuid (`None` for messages with no parent at all). Each value is the abandoned
    branch heads at that fork point, as full `MessageNode` subtrees.
    """

    live_path: tuple[Message, ...]
    abandoned_branches: dict[str | None, tuple[MessageNode, ...]]


def _uuid(message: Message) -> str:
    """The message's `source_uuid`, failing loud if it is absent.

    Fork reconstruction runs on the kept list, where the uuid-less
    `queued_command` previews have already been dropped (`keep_messages`). A None
    here means that contract was violated upstream, so we raise rather than invent
    an identity — a uuid-less node would otherwise masquerade as a rootless branch
    head and render as a spurious rewound branch.
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
    uuid-less `queued_command` previews already dropped). Returns an empty
    reconstruction for an empty list.
    """
    if not messages:
        return ForkReconstruction(live_path=(), abandoned_branches={})

    by_uuid = {_uuid(message): message for message in messages}
    children_by_parent: dict[str | None, list[Message]] = {}
    for message in messages:
        children_by_parent.setdefault(message.source_parent_uuid, []).append(message)

    live_path = _live_path(messages, by_uuid)
    live_uuids = {_uuid(message) for message in live_path}

    building: set[str] = set()

    def build_node(message: Message) -> MessageNode:
        uuid = _uuid(message)
        if uuid in building:
            raise ValueError(f"cycle in message tree at {uuid}")
        building.add(uuid)
        children = sorted(
            children_by_parent.get(uuid, ()),
            key=lambda m: (m.ordinal, _uuid(m)),
        )
        return MessageNode(message, tuple(build_node(child) for child in children))

    abandoned: dict[str | None, list[MessageNode]] = {}
    for message in messages:
        if _uuid(message) in live_uuids:
            continue
        parent = message.source_parent_uuid
        is_branch_head = parent is None or parent in live_uuids or parent not in by_uuid
        if is_branch_head:
            abandoned.setdefault(parent, []).append(build_node(message))

    return ForkReconstruction(
        live_path=live_path,
        abandoned_branches={
            parent: tuple(heads) for parent, heads in abandoned.items()
        },
    )


def _live_path(
    messages: list[Message], by_uuid: dict[str, Message]
) -> tuple[Message, ...]:
    """Walk the ancestor chain of the highest-ordinal message, root→tip.

    Ties on ordinal break toward the later message in input order (the most
    recently written). Stops at a message whose parent is `None` or absent from
    the payload; raises on a parent cycle.
    """
    live_tip = messages[0]
    for message in messages[1:]:
        if message.ordinal >= live_tip.ordinal:
            live_tip = message

    chain: list[Message] = []
    seen: set[str] = set()
    current: Message | None = live_tip
    while current is not None:
        uuid = _uuid(current)
        if uuid in seen:
            raise ValueError(f"cycle in live path at {uuid}")
        seen.add(uuid)
        chain.append(current)
        parent_uuid = current.source_parent_uuid
        current = by_uuid.get(parent_uuid) if parent_uuid is not None else None
    chain.reverse()
    return tuple(chain)
