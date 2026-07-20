"""Unit tests for the externally-managed / verbatim registry, src/dev_playbook/external.py."""

from dev_playbook import external


class TestIsExternallyManaged:
    def test_path_inside_vendored_root_is_external(self) -> None:
        assert external.is_externally_managed("dotfiles/.agents/skills/x/SKILL.md")

    def test_the_root_itself_is_external(self) -> None:
        assert external.is_externally_managed("dotfiles/.agents")

    def test_authored_path_is_not_external(self) -> None:
        assert not external.is_externally_managed("standards/prose/conventions.md")

    def test_stray_same_named_dir_elsewhere_is_not_external(self) -> None:
        # Only the vendored root dotfiles/.agents is externally managed; a
        # directory that merely shares the leaf name is authored content.
        assert not external.is_externally_managed("src/.agents/note.md")

    def test_dead_dhub_root_is_not_external(self) -> None:
        # .dhub was dropped: it no longer names an externally-managed root.
        assert not external.is_externally_managed("dotfiles/.dhub/whatever.md")


class TestIsVerbatimDoc:
    def test_reference_type_is_verbatim(self) -> None:
        assert external.is_verbatim_doc({"type": "Reference", "title": "X"})

    def test_concept_type_is_not_verbatim(self) -> None:
        assert not external.is_verbatim_doc({"type": "Standard"})

    def test_missing_type_is_not_verbatim(self) -> None:
        assert not external.is_verbatim_doc({"title": "X"})

    def test_absent_frontmatter_is_not_verbatim(self) -> None:
        assert not external.is_verbatim_doc(None)
