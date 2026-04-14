"""Tests for chain enumeration."""

from sdd_chain_text.chains import build_chains
from sdd_chain_text.oft_xml import SpecItem


def _item(full_id, doctype, covers=None, needs=None):
    parts = full_id.split("~")
    return SpecItem(
        full_id=full_id,
        doctype=doctype,
        name=parts[1],
        version=int(parts[2]),
        title=f"Title for {parts[1]}",
        status="approved",
        source_file="test.md",
        source_line=1,
        description="desc",
        rationale="",
        needs=needs or [],
        covers=covers or [],
    )


def test_simple_chain():
    feat = _item("feat~auth~1", "feat", needs=["req"])
    req = _item("req~auth.login~1", "req", covers=["feat~auth~1"], needs=["dsn"])
    dsn = _item("dsn~auth.login~1", "dsn", covers=["req~auth.login~1"])

    chains = build_chains([feat, req, dsn])
    assert len(chains) == 1
    assert [i.full_id for i in chains[0]] == [
        "feat~auth~1",
        "req~auth.login~1",
        "dsn~auth.login~1",
    ]


def test_branching_produces_separate_chains():
    feat = _item("feat~auth~1", "feat", needs=["req"])
    req1 = _item("req~auth.login~1", "req", covers=["feat~auth~1"], needs=["dsn"])
    req2 = _item("req~auth.logout~1", "req", covers=["feat~auth~1"], needs=["dsn"])

    chains = build_chains([feat, req1, req2])
    assert len(chains) == 2
    # Both chains start with feat
    assert chains[0][0].full_id == "feat~auth~1"
    assert chains[1][0].full_id == "feat~auth~1"
    # Each chain has a different req leaf
    leaves = {c[-1].full_id for c in chains}
    assert leaves == {"req~auth.login~1", "req~auth.logout~1"}


def test_test_items_excluded():
    req = _item("req~auth~1", "req", needs=["utest"])
    utest = _item("utest~auth~1", "utest", covers=["req~auth~1"])

    chains = build_chains([req, utest])
    assert len(chains) == 1
    assert len(chains[0]) == 1
    assert chains[0][0].full_id == "req~auth~1"


def test_no_items_no_chains():
    assert build_chains([]) == []
