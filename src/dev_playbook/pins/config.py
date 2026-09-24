"""A consumer's pinned block in ``.pre-commit-config.yaml``: read it, rewrite it.

The block is the ``- repo: <hook repo url>`` item with its ``rev:`` line and
its ``hooks:`` list. One function locates the rev line (``rev_line``); the
audit reads through it and the writers rewrite through it, so the reader and
the writer cannot disagree about which line carries the pin.
"""

import re

import yaml

from dev_playbook.errors import ToolError


def rev_line(lines: list[str], url: str) -> int | None:
    """Index of the ``rev:`` line pinning ``url``, or None when there is none."""
    for i, line in enumerate(lines):
        if re.match(rf"^\s*-\s*repo:\s*{re.escape(url)}\s*$", line):
            for follower in range(i + 1, min(i + 3, len(lines))):
                if re.match(r"^\s*rev:\s*\S+", lines[follower]):
                    return follower
    return None


def pinned_rev(config_text: str, url: str) -> str | None:
    """The ``rev`` pinned for ``url`` in a ``.pre-commit-config.yaml`` body, or None."""
    lines = config_text.splitlines()
    index = rev_line(lines, url)
    return lines[index].split(":", 1)[1].strip() if index is not None else None


def pinned_hook_ids(config_text: str, url: str) -> tuple[str, ...] | None:
    """The hook ids listed under ``url``'s block of a config body, or None without one."""
    config = yaml.safe_load(config_text)
    if not isinstance(config, dict):
        return None
    for block in config.get("repos") or ():
        if isinstance(block, dict) and block.get("repo") == url:
            return tuple(str(hook["id"]) for hook in block.get("hooks") or ())
    return None


def pinned_block(lines: list[str], url: str) -> range:
    """The lines of the block pinning ``url``: its ``- repo:`` line through its last child.

    The block ends at the first non-blank line indented no deeper than the
    ``- repo:`` line — the next repo item, or a top-level key. A config with no
    such block raises rather than growing one: adding a dev-playbook block to a
    repo is adoption, a different act from a bump.
    """
    index = rev_line(lines, url)
    if index is None:
        raise ToolError(f"no {url} pin to move")
    start = index - 1
    depth = len(lines[start]) - len(lines[start].lstrip())
    end = index + 1
    while end < len(lines):
        line = lines[end]
        if line.strip() and len(line) - len(line.lstrip()) <= depth:
            break
        end += 1
    return range(start, end)


def rewritten(text: str, url: str, sha: str, ids: tuple[str, ...]) -> tuple[str, str]:
    """``text`` with ``url``'s pin at ``sha`` and its hooks set to ``ids``, and the old rev.

    Two edits, both inside the one pinned block: the ``rev:`` line takes ``sha``,
    and the entries under ``hooks:`` become one ``- id:`` line per published id,
    so a hook renamed upstream — ``playbook-lint`` becoming ``playbook-check`` —
    moves with the pin instead of failing loud at the next gate. Indentation is
    taken from the block as found; every byte outside the block, including the
    trailing newline, is carried through untouched. A block whose hook entries
    already match ``ids`` changes only its rev line.
    """
    lines = text.splitlines()
    block = pinned_block(lines, url)
    rev_index = block.start + 1
    line = lines[rev_index]
    old = line.split(":", 1)[1].strip()
    indent = line[: len(line) - len(line.lstrip())]
    lines[rev_index] = f"{indent}rev: {sha}"

    hooks_index = next((i for i in block if lines[i].strip() == "hooks:"), None)
    if hooks_index is None:
        raise ToolError(f"the {url} block has no hooks: key")
    entries = [lines[i] for i in range(hooks_index + 1, block.stop)]
    id_lines = [entry for entry in entries if entry.lstrip().startswith("- id:")]
    if id_lines:
        id_indent = id_lines[0][: len(id_lines[0]) - len(id_lines[0].lstrip())]
    else:
        id_indent = indent + "  "
    lines[hooks_index + 1 : block.stop] = [
        f"{id_indent}- id: {hook_id}" for hook_id in ids
    ]

    tail = "\n" if text.endswith("\n") else ""
    return "\n".join(lines) + tail, old
