"""Pins every constant in src/dev_playbook/sources.py to its document."""

from dev_playbook import sources
from dev_playbook.model import Repo


def test_every_section_names_a_tracked_file_and_a_present_heading(
    dev_playbook_repo: Repo,
) -> None:
    for name, section in sources.sections().items():
        assert section.path in dev_playbook_repo.markdown, name
        slugs = {h.slug for h in dev_playbook_repo.markdown[section.path].headings}
        assert section.heading in slugs, f"{name}: {section.path}#{section.heading}"


def test_type_registry_section_holds_the_table(dev_playbook_repo: Repo) -> None:
    doc = dev_playbook_repo.markdown[sources.TYPE_REGISTRY.path]
    rows = [
        t for _, t in doc.section(sources.TYPE_REGISTRY.heading) if t.startswith("| `")
    ]
    assert any(row.startswith("| `Standard`") for row in rows)


def test_canonical_dir_holds_tracked_files(dev_playbook_repo: Repo) -> None:
    prefix = sources.CANONICAL_DIR + "/"
    assert any(path.startswith(prefix) for path in dev_playbook_repo.files)
