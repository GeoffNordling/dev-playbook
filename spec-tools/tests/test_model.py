"""Tests for spec_tools.model."""

from collections.abc import Iterable

import networkx
import pytest

from spec_tools.model import ItemId, SpecGraph, SpecItem


def make_item(
    name: str,
    artifact_type: str = "dsn",
    revision: int = 0,
    covers: Iterable[ItemId] = (),
) -> SpecItem:
    """Build a SpecItem with placeholder fields; override `name`, `artifact_type`, `revision`, `covers` as needed."""
    return SpecItem(
        heading=name,
        id=ItemId(artifact_type=artifact_type, name=name, revision=revision),
        description="",
        rationale=None,
        comment=None,
        covers=list(covers),
        depends=[],
        needs=[],
        tags=[],
        interface=[],
        agent_review=[],
    )


@pytest.mark.covers("dsn~model.item-id~0")
def test_item_id_exposes_constructor_fields():
    item_id = ItemId(artifact_type="dsn", name="model.item-id", revision=0)

    assert item_id.artifact_type == "dsn"
    assert item_id.name == "model.item-id"
    assert item_id.revision == 0


@pytest.mark.covers("dsn~model.item-id~0")
def test_item_id_compares_by_value():
    same_a = ItemId(artifact_type="dsn", name="model.item-id", revision=0)
    same_b = ItemId(artifact_type="dsn", name="model.item-id", revision=0)
    different_type = ItemId(artifact_type="req", name="model.item-id", revision=0)
    different_name = ItemId(artifact_type="dsn", name="model.spec-item", revision=0)
    different_revision = ItemId(artifact_type="dsn", name="model.item-id", revision=1)

    assert same_a == same_b
    assert same_a != different_type
    assert same_a != different_name
    assert same_a != different_revision


@pytest.mark.covers("dsn~model.item-id~0")
def test_item_id_rejects_negative_revision():
    with pytest.raises(ValueError, match="revision"):
        ItemId(artifact_type="dsn", name="model.item-id", revision=-1)


@pytest.mark.covers("dsn~model.spec-item~0")
def test_spec_item_exposes_constructor_fields():
    item_id = ItemId(artifact_type="dsn", name="model.spec-item", revision=0)
    parent_id = ItemId(artifact_type="req", name="deserialize.fidelity", revision=0)
    dep_id = ItemId(artifact_type="dsn", name="model.item-id", revision=0)

    spec_item = SpecItem(
        heading="SpecItem shape",
        id=item_id,
        description="The model SHALL represent each spec item ...",
        rationale="Typed accessors give every downstream consumer ...",
        comment=None,
        covers=[parent_id],
        depends=[dep_id],
        needs=["utest"],
        tags=["model"],
        interface=["model.SpecItem(...) -> None"],
        agent_review=[],
    )

    assert spec_item.heading == "SpecItem shape"
    assert spec_item.id == item_id
    assert spec_item.description == "The model SHALL represent each spec item ..."
    assert spec_item.rationale == "Typed accessors give every downstream consumer ..."
    assert spec_item.comment is None
    assert spec_item.covers == [parent_id]
    assert spec_item.depends == [dep_id]
    assert spec_item.needs == ["utest"]
    assert spec_item.tags == ["model"]
    assert spec_item.interface == ["model.SpecItem(...) -> None"]
    assert spec_item.agent_review == []


@pytest.mark.covers("dsn~model.graph~0")
def test_spec_graph_find_returns_item_or_none():
    item = make_item("model.spec-item")
    other = make_item("model.item-id")
    graph = SpecGraph(items=[item])

    assert graph.find(item.id) is item
    assert graph.find(other.id) is None


@pytest.mark.covers("dsn~model.graph~0")
def test_spec_graph_upstream_returns_items_named_in_covers():
    feat = make_item("model", artifact_type="feat")
    req = make_item("model.navigation", artifact_type="req", covers=[feat.id])
    graph = SpecGraph(items=[feat, req])

    assert graph.upstream(req.id) == [feat]
    assert graph.upstream(feat.id) == []


@pytest.mark.covers("dsn~model.graph~0")
def test_spec_graph_downstream_returns_items_that_cover_target():
    feat = make_item("model", artifact_type="feat")
    req_a = make_item("model.navigation", artifact_type="req", covers=[feat.id])
    req_b = make_item("model.round-trip", artifact_type="req", covers=[feat.id])
    graph = SpecGraph(items=[feat, req_a, req_b])

    assert graph.downstream(feat.id) == [req_a, req_b]
    assert graph.downstream(req_a.id) == []


@pytest.mark.covers("dsn~model.graph~0")
def test_spec_graph_as_digraph_nodes_keyed_by_id_with_coverage_edges():
    feat = make_item("model", artifact_type="feat")
    req = make_item("model.navigation", artifact_type="req", covers=[feat.id])
    graph = SpecGraph(items=[feat, req])

    digraph = graph.as_digraph()

    assert isinstance(digraph, networkx.DiGraph)
    assert set(digraph.nodes) == {feat.id, req.id}
    assert set(digraph.edges) == {(req.id, feat.id)}
