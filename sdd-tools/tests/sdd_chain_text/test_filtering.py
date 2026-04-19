"""Tests for chain filtering."""

from sdd_chain_text.filtering import filter_chains
from sdd_chain_text.oft_xml import SpecItem


def _item(full_id, doctype, source_file="test.md"):
    parts = full_id.split("~")
    return SpecItem(
        full_id=full_id,
        doctype=doctype,
        name=parts[1],
        version=int(parts[2]),
        title="",
        status="approved",
        source_file=source_file,
        source_line=1,
        description="",
        rationale="",
    )


def _chains():
    return [
        [_item("feat~auth~1", "feat"), _item("req~auth.login~1", "req")],
        [
            _item("feat~data~1", "feat"),
            _item("req~data.export~1", "req", source_file="data.md"),
        ],
    ]


def test_filter_by_id():
    result = filter_chains(_chains(), id_pattern="*auth*")
    assert len(result) == 1
    assert result[0][0].full_id == "feat~auth~1"


def test_filter_by_feature():
    result = filter_chains(_chains(), feature="*data*")
    assert len(result) == 1
    assert result[0][1].full_id == "req~data.export~1"


def test_filter_by_source_file():
    result = filter_chains(_chains(), source_file="data.md")
    assert len(result) == 1


def test_filter_by_doctype():
    result = filter_chains(_chains(), doctype="req")
    assert len(result) == 2  # Both chains contain req items


def test_no_match():
    result = filter_chains(_chains(), id_pattern="*nonexistent*")
    assert result == []
