import pytest

from dev_playbook.cloa_viewer import registry
from dev_playbook.cloa_viewer.kinds import index_tree, markdown_file


def test_the_registry_lists_its_kinds_in_build_order() -> None:
    assert [kind.name for kind in registry.KINDS] == ["index-tree", "markdown-file"]


def test_a_per_checkout_kind_carries_its_version_and_scope() -> None:
    kind = registry.kind_by_name("index-tree")
    assert (kind.version, kind.per_subject) == (1, False)
    assert kind.generate is index_tree.generate


def test_a_per_subject_kind_carries_its_version_and_scope() -> None:
    kind = registry.kind_by_name("markdown-file")
    assert (kind.version, kind.per_subject) == (1, True)
    assert kind.generate is markdown_file.generate


def test_an_unregistered_name_raises_naming_it() -> None:
    with pytest.raises(KeyError, match="force-graph"):
        registry.kind_by_name("force-graph")
