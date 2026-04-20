"""Tests for sdd_tools.chains."""

from pathlib import Path

from sdd_tools.chains import build_chains
from sdd_tools.models import SpecItem


def _item(spec_id, doctype, covers=()):
    name = spec_id.split("~")[1]
    return SpecItem(
        id=spec_id,
        doctype=doctype,
        name=name,
        revision=1,
        title=name,
        status="approved",
        description="",
        rationale="",
        covers=list(covers),
        needs=[],
        source_file=Path(f"specs/{name}.md"),
        source_line=1,
    )


class TestBuildChains:
    def test_single_root_no_children(self):
        feat = _item("feat~user.auth~1", "feat")
        chains = build_chains([feat])
        assert chains == [[feat]]

    def test_two_layer_chain(self):
        feat = _item("feat~auth~1", "feat")
        req = _item("req~auth.login~1", "req", covers=["feat~auth~1"])
        chains = build_chains([feat, req])
        assert chains == [[feat, req]]

    def test_branching(self):
        feat = _item("feat~auth~1", "feat")
        r1 = _item("req~a~1", "req", covers=["feat~auth~1"])
        r2 = _item("req~b~1", "req", covers=["feat~auth~1"])
        chains = build_chains([feat, r1, r2])
        assert sorted(chains, key=lambda c: c[-1].id) == [
            [feat, r1],
            [feat, r2],
        ]

    def test_test_layers_excluded(self):
        feat = _item("feat~auth~1", "feat")
        req = _item("req~login~1", "req", covers=["feat~auth~1"])
        ut = _item("utest~login~1", "utest", covers=["req~login~1"])
        chains = build_chains([feat, req, ut])
        # utest excluded; req has no non-test children → req is leaf
        assert chains == [[feat, req]]

    def test_orphan_covers_ignored(self):
        item = _item("req~x~1", "req", covers=["feat~missing~1"])
        chains = build_chains([item])
        assert chains == [[item]]
