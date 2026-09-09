"""The registry: the kinds the tool knows, and so the kinds it can show.

Adding a view to the viewer is adding an entry here and nothing else, by the
known kinds only principle. A refresh
walks ``KINDS`` to write the state directory, and the page asks the server for
the same list, so a name on one side and not the other is visible rather than
silent.

``Kind`` and ``View`` are defined in ``entry`` and re-exported here: the
registry imports every kind module, so the kinds cannot import the registry
back.
"""

from dev_playbook.cloa_viewer.entry import Kind, View
from dev_playbook.cloa_viewer.kinds import index_tree, markdown_file

__all__ = ["KINDS", "Kind", "View", "kind_by_name"]

KINDS: tuple[Kind, ...] = (index_tree.KIND, markdown_file.KIND)


def kind_by_name(name: str) -> Kind:
    """The registered kind called ``name``, or ``KeyError`` naming what was asked."""
    for kind in KINDS:
        if kind.name == name:
            return kind
    raise KeyError(name)
