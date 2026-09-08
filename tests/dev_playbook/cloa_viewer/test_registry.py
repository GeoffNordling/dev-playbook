import pytest

from dev_playbook.cloa_viewer import registry
from dev_playbook.cloa_viewer.kinds import index_tree


def test_the_registry_lists_the_index_tree_kind() -> None:
    assert [kind.name for kind in registry.KINDS] == ["index-tree"]


def test_a_kind_carries_its_version_and_scope() -> None:
    kind = registry.kind_by_name("index-tree")
    assert (kind.version, kind.per_subject) == (1, False)
    assert kind.generate is index_tree.generate


def test_an_unregistered_name_raises_naming_it() -> None:
    with pytest.raises(KeyError, match="force-graph"):
        registry.kind_by_name("force-graph")
