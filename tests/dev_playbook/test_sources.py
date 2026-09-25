"""Pins every constant in src/dev_playbook/sources.py to its document."""

import re

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
    doc = dev_playbook_repo.markdown[sources.OKF_TYPE_REGISTRY.path]
    rows = [
        t
        for _, t in doc.section(sources.OKF_TYPE_REGISTRY.heading)
        if t.startswith("| `")
    ]
    assert any(row.startswith("| `Standard`") for row in rows)


def registry_rows(repo: Repo) -> list[list[str]]:
    doc = repo.markdown[sources.OKF_TYPE_REGISTRY.path]
    lines = [
        t
        for _, t in doc.section(sources.OKF_TYPE_REGISTRY.heading)
        if t.startswith("|")
    ]
    return [[cell.strip() for cell in line.strip("|").split("|")] for line in lines[2:]]


def test_registered_types_are_the_type_registry_rows(dev_playbook_repo: Repo) -> None:
    names = {row[0].strip("`") for row in registry_rows(dev_playbook_repo)}
    assert names == sources.REGISTERED_OKF_TYPES


def test_workstream_headings_are_the_menu_rows(dev_playbook_repo: Repo) -> None:
    doc = dev_playbook_repo.markdown[sources.WORKSTREAM_HEADING_REGISTRY.path]
    lines = [
        t
        for _, t in doc.section(sources.WORKSTREAM_HEADING_REGISTRY.heading)
        if t.startswith("|")
    ]
    names = {line.strip("|").split("|")[0].strip().strip("`") for line in lines[2:]}
    assert names == sources.WORKSTREAM_HEADINGS


def test_type_registry_rows_name_a_type_in_the_first_cell(
    dev_playbook_repo: Repo,
) -> None:
    type_name = re.compile(r"`[A-Z][A-Za-z0-9]*(?:-[A-Z][A-Za-z0-9]*)*`")
    for row in registry_rows(dev_playbook_repo):
        assert type_name.fullmatch(row[0]), row[0]


def test_type_registry_rows_describe_the_type_in_the_second_cell(
    dev_playbook_repo: Repo,
) -> None:
    for row in registry_rows(dev_playbook_repo):
        assert len(row) == 2
        assert row[1], row[0]


def test_type_registry_rows_are_in_alphabetical_order(dev_playbook_repo: Repo) -> None:
    names = [row[0].strip("`").lower() for row in registry_rows(dev_playbook_repo)]
    assert names == sorted(names)


def test_canonical_dir_holds_tracked_files(dev_playbook_repo: Repo) -> None:
    prefix = sources.CANONICAL_DIR + "/"
    assert any(path.startswith(prefix) for path in dev_playbook_repo.files)


def test_canonical_files_are_the_files_directly_under_the_dir(
    dev_playbook_repo: Repo,
) -> None:
    prefix = sources.CANONICAL_DIR + "/"
    present = {
        path.removeprefix(prefix)
        for path in dev_playbook_repo.files
        if path.startswith(prefix) and "/" not in path.removeprefix(prefix)
    }
    assert present == sources.CANONICAL_FILES


def test_shipped_canonical_copy_is_byte_identical_to_the_tree(
    dev_playbook_repo: Repo,
) -> None:
    def tracked(directory: str) -> dict[str, bytes]:
        prefix = directory + "/"
        return {
            path.removeprefix(prefix): data
            for path, data in dev_playbook_repo.contents.items()
            if path.startswith(prefix)
        }

    tree = tracked(sources.CANONICAL_DIR)
    assert tracked(sources.SHIPPED_CANONICAL_DIR) == tree
    assert dict(dev_playbook_repo.canonical) == tree


def test_standard_directories_are_the_directories_under_standards(
    dev_playbook_repo: Repo,
) -> None:
    present = {
        parts[1]
        for path in dev_playbook_repo.files
        if len(parts := path.split("/")) >= 3 and parts[0] == "standards"
    }
    assert present == sources.STANDARD_DIRECTORIES
