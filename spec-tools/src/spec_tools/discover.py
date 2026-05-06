"""Enumerate the spec files reachable from a project root."""

import pathlib

_ADMITTED_CHILDREN = frozenset(
    {
        "design.md",
        "design",
        "functional_requirements.md",
        "functional_requirements",
    }
)


def find(root: pathlib.Path) -> list[pathlib.Path]:
    """Return the spec files reachable from `<root>/specs/`, sorted lexicographically.

    Raises ValueError when the project root has no recognized spec layout.
    """
    specs = root / "specs"
    if not specs.is_dir():
        raise ValueError(f"no specs/ directory at {root}")
    children = {child.name for child in specs.iterdir()}
    for name in children:
        if name not in _ADMITTED_CHILDREN:
            raise ValueError(f"unexpected entry under specs/: {name}")
    for stem in ("design", "functional_requirements"):
        if f"{stem}.md" in children and stem in children:
            raise ValueError(f"specs/ has both {stem}.md and {stem}/; pick one layout")
        if stem in children and not (specs / stem / "index.md").is_file():
            raise ValueError(f"folder-form spec dir specs/{stem}/ is missing index.md")
    for entry in specs.rglob("*"):
        if entry.is_dir():
            continue
        if entry.suffix != ".md":
            raise ValueError(f"non-spec entry under specs/: {entry.relative_to(specs)}")
    spec_files = sorted(p for p in specs.rglob("*.md") if p.name != "index.md")
    if not spec_files:
        raise ValueError(f"specs/ at {root} contains no spec files")
    return spec_files
