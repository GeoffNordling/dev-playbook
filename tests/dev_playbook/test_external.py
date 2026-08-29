"""Unit tests for the verbatim-content registry, src/dev_playbook/external.py."""

from dev_playbook import external


class TestIsVerbatimDoc:
    def test_reference_type_is_verbatim(self) -> None:
        assert external.is_verbatim_doc({"type": "Reference", "title": "X"})

    def test_concept_type_is_not_verbatim(self) -> None:
        assert not external.is_verbatim_doc({"type": "Standard"})

    def test_missing_type_is_not_verbatim(self) -> None:
        assert not external.is_verbatim_doc({"title": "X"})

    def test_absent_frontmatter_is_not_verbatim(self) -> None:
        assert not external.is_verbatim_doc(None)
