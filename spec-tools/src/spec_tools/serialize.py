"""Render SpecItems to standard-conformant Markdown."""

import pathlib

from spec_tools.model import ItemId, SpecItem


def render(items: list[SpecItem]) -> str:
    """Render `items` to a Markdown string conforming to the workspace spec standard."""
    return "\n".join(_render_item(item) for item in items)


def write(items: list[SpecItem], path: pathlib.Path) -> None:
    """Render `items` and write the result to `path`."""
    path.write_text(render(items))


def _render_item(item: SpecItem) -> str:
    """Render one SpecItem as a Markdown block, omitting absent or empty fields."""
    sections = [
        f"### {item.heading}\n`{_format_id(item.id)}`",
        f"Description:\n{item.description}",
        _block("Rationale", item.rationale),
        _block("Comment", item.comment),
        _id_bullets("Covers", item.covers),
        _id_bullets("Depends", item.depends),
        _bullets("Needs", item.needs),
        _inline("Tags", item.tags),
        _repeated("Interface", item.interface),
        _repeated("AgentReview", item.agent_review),
    ]
    return "\n\n".join(s for s in sections if s) + "\n"


def _format_id(item_id: ItemId) -> str:
    """Format an ItemId as `type~name~rev`."""
    return f"{item_id.artifact_type}~{item_id.name}~{item_id.revision}"


def _block(keyword: str, body: str | None) -> str | None:
    """Format a `Keyword:\\n<body>` block, or None when body is None."""
    return None if body is None else f"{keyword}:\n{body}"


def _bullets(keyword: str, items: list[str]) -> str | None:
    """Format `Keyword:` followed by a bullet list, or None when items is empty."""
    if not items:
        return None
    body = "\n".join(f"- {item}" for item in items)
    return f"{keyword}:\n{body}"


def _id_bullets(keyword: str, ids: list[ItemId]) -> str | None:
    """Format `Keyword:` followed by a bullet list of formatted IDs, or None when empty."""
    return _bullets(keyword, [_format_id(i) for i in ids])


def _inline(keyword: str, items: list[str]) -> str | None:
    """Format `Keyword: a, b, c` on a single line, or None when items is empty."""
    return f"{keyword}: {', '.join(items)}" if items else None


def _repeated(keyword: str, entries: list[str]) -> str | None:
    """Format one `Keyword: <entry>` line per entry, or None when entries is empty."""
    if not entries:
        return None
    return "\n".join(f"{keyword}: {entry}" for entry in entries)
