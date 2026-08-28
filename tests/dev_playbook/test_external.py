"""Unit tests for the externally-managed / verbatim registry, src/dev_playbook/external.py."""

from pathlib import PurePosixPath

import pytest

from dev_playbook import external


class TestIsExternallyManaged:
    def test_registry_is_empty(self) -> None:
        # No vendored roots exist today: the last one, dotfiles/.agents,
        # retired when the workspace took ownership of the copies.
        assert external.EXTERNALLY_MANAGED_ROOTS == ()

    def test_retired_root_is_no_longer_external(self) -> None:
        assert not external.is_externally_managed("dotfiles/.agents/skills/x/SKILL.md")

    def test_authored_path_is_not_external(self) -> None:
        assert not external.is_externally_managed("standards/prose/conventions.md")


class TestIsExternallyManagedMechanism:
    """The registry mechanism itself, exercised with a root patched in."""

    @pytest.fixture(autouse=True)
    def a_registered_root(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            external,
            "EXTERNALLY_MANAGED_ROOTS",
            (PurePosixPath("vendor/tree"),),
        )

    def test_path_inside_a_registered_root_is_external(self) -> None:
        assert external.is_externally_managed("vendor/tree/x/SKILL.md")

    def test_the_root_itself_is_external(self) -> None:
        assert external.is_externally_managed("vendor/tree")

    def test_stray_same_named_dir_elsewhere_is_not_external(self) -> None:
        # Only the registered root is externally managed; a directory that
        # merely shares the leaf name is authored content.
        assert not external.is_externally_managed("src/tree/note.md")


class TestIsVerbatimDoc:
    def test_reference_type_is_verbatim(self) -> None:
        assert external.is_verbatim_doc({"type": "Reference", "title": "X"})

    def test_concept_type_is_not_verbatim(self) -> None:
        assert not external.is_verbatim_doc({"type": "Standard"})

    def test_missing_type_is_not_verbatim(self) -> None:
        assert not external.is_verbatim_doc({"title": "X"})

    def test_absent_frontmatter_is_not_verbatim(self) -> None:
        assert not external.is_verbatim_doc(None)
