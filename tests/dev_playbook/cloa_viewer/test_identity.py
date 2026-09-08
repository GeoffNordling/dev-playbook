import pytest

from dev_playbook.cloa_viewer.identity import resolve_target


def test_a_citation_of_this_repo_resolves_into_the_checkout() -> None:
    assert (
        resolve_target("a.md", "~/workspace/fixture/docs/b.md#x", "fixture")
        == "docs/b.md"
    )


def test_a_root_absolute_link_resolves_against_the_checkout_root() -> None:
    assert resolve_target("a.md", "/docs/b.md", "fixture") == "docs/b.md"


def test_a_citation_of_another_repo_has_no_identity() -> None:
    with pytest.raises(ValueError, match="a citation of another repo"):
        resolve_target("a.md", "~/workspace/other/b.md", "fixture")
