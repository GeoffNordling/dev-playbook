"""Tests for sdd_tools.filtering."""

from pathlib import Path

from sdd_tools.filtering import filter_chains
from sdd_tools.models import SpecItem


def _item(spec_id, doctype, source_file="specs/x.md"):
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
        covers=[],
        needs=[],
        source_file=Path(source_file),
        source_line=1,
    )


def _chains():
    feat = _item("feat~auth~1", "feat", "specs/feat.md")
    req = _item("req~login~1", "req", "specs/req.md")
    dsn = _item("dsn~login~1", "dsn", "specs/design.md")
    return [[feat, req, dsn]]


class TestFilterChains:
    def test_no_filters_returns_input(self):
        chains = _chains()
        assert filter_chains(chains) == chains

    def test_id_pattern_match(self):
        assert len(filter_chains(_chains(), id_pattern="*login*")) == 1

    def test_id_pattern_no_match(self):
        assert filter_chains(_chains(), id_pattern="*missing*") == []

    def test_doctype_match(self):
        assert len(filter_chains(_chains(), doctype="dsn")) == 1

    def test_doctype_no_match(self):
        assert filter_chains(_chains(), doctype="impl") == []

    def test_source_file_substring(self):
        assert len(filter_chains(_chains(), source_file="design")) == 1

    def test_feature_glob_matches_root(self):
        assert len(filter_chains(_chains(), feature="*auth*")) == 1

    def test_feature_only_matches_feat_roots(self):
        chains = [[_item("req~x~1", "req")]]
        assert filter_chains(chains, feature="*x*") == []
