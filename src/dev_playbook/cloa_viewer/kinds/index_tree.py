"""The ``index-tree`` kind: the checkout's markdown, arranged by its indexes.

One view file per checkout. The walk starts at the root ``index.md`` and
follows every listing entry, so the tree on screen is the hierarchy the
[Indexes](/standards/knowledge-organization/indexes.md) standard describes and
nothing else. Every tracked markdown file the walk never reaches lands in
``unindexed``, because total accounting is a principle: a file no index names
is exactly the file the user needs to see
([CLOA Viewer](/worktree-cloa-viewer-tool-working-docs/ROOT.md#principles)).

A directory row carries the sum of the words below it, so the tree answers
where a repo's documentation weight sits without opening a file.
"""

from pathlib import Path, PurePosixPath
from typing import Any

from dev_playbook.cloa_viewer import state
from dev_playbook.cloa_viewer.entry import Kind, View
from dev_playbook.cloa_viewer.identity import is_external, resolve_target
from dev_playbook.gitrepo import canonical_repo_name, git_files
from dev_playbook.md import lines_outside_fences, markdown_links, parse_frontmatter

KIND_NAME = "index-tree"
KIND_VERSION = 1
TITLE = "Index tree"
INDEX_FILE = "index.md"
MARKDOWN_SUFFIX = ".md"
HEADING_PREFIX = "# "
LISTING_PREFIX = "- "
SENTENCE_END = ". "


def _file_node(checkout: Path, identity: str, tracked: set[str]) -> dict[str, Any]:
    """One file row: its frontmatter facts and word count, or nulls when absent.

    An index that lists a file git does not carry is a defect the tree has to
    show rather than hide, so the row survives with ``exists`` false.
    """
    if identity not in tracked:
        return {
            "identity": identity,
            "type": None,
            "title": None,
            "description": None,
            "words": 0,
            "exists": False,
        }
    front, body = parse_frontmatter((checkout / identity).read_text(encoding="utf-8"))
    facts = front or {}
    return {
        "identity": identity,
        "type": facts.get("type"),
        "title": facts.get("title"),
        "description": facts.get("description"),
        "words": len(body.split()),
        "exists": True,
    }


def _heading(body: str) -> str | None:
    """The text of the first H1 outside a fence, without its ``# ``."""
    for _, line in lines_outside_fences(body):
        if line.startswith(HEADING_PREFIX):
            return line[len(HEADING_PREFIX) :].strip()
    return None


def _opening_sentence(body: str) -> str | None:
    """The first sentence of the prose between the H1 and the first listing line.

    That prose is what the indexes standard calls the introduction, and its
    first sentence names what the directory holds. The cut is at the first
    ``. ``, so a sentence that ends the prose keeps its full stop and one
    followed by more text does not.
    """
    prose: list[str] = []
    seen_heading = False
    for _, line in lines_outside_fences(body):
        if not seen_heading:
            seen_heading = line.startswith(HEADING_PREFIX)
            continue
        if line.startswith(LISTING_PREFIX):
            break
        if line.strip():
            prose.append(line.strip())
    if not prose:
        return None
    return " ".join(prose).split(SENTENCE_END, 1)[0]


def _listing_targets(body: str) -> list[str]:
    """The target of the first link on every listing line, in listing order.

    Only the first link on the line: an entry is a link followed by the
    document's description, and a description may carry a link of its own that
    is a citation, not an entry.
    """
    targets = []
    for _, line in lines_outside_fences(body):
        if not line.startswith(LISTING_PREFIX):
            continue
        links = markdown_links(line)
        if links:
            targets.append(links[0][1])
    return targets


def _directory_node(
    checkout: Path, identity: str, tracked: set[str], reached: set[str], repo: str
) -> dict[str, Any]:
    """One directory row and everything its ``index.md`` lists, in listing order.

    ``identity`` ends in ``/``, and is ``""`` for the checkout root.
    ``reached`` collects every identity the walk touches; what is left over is
    the unindexed list. ``repo`` is the checkout's canonical repo name, which
    tells a Citation of this repo from a Citation of another one.
    """
    index = identity + INDEX_FILE
    name = PurePosixPath(identity).name if identity else checkout.name
    if index not in tracked:
        return {
            "identity": identity,
            "title": name,
            "description": None,
            "words": 0,
            "children": [],
        }
    if index in reached:
        raise ValueError(f"{index} is reached twice: the index hierarchy is not a tree")
    reached.add(index)
    _, body = parse_frontmatter((checkout / index).read_text(encoding="utf-8"))
    children = [_file_node(checkout, index, tracked)]
    for target in _listing_targets(body):
        if is_external(target):
            continue
        child = resolve_target(index, target, repo)
        if child.endswith(f"/{INDEX_FILE}"):
            children.append(
                _directory_node(
                    checkout, child[: -len(INDEX_FILE)], tracked, reached, repo
                )
            )
        else:
            reached.add(child)
            children.append(_file_node(checkout, child, tracked))
    return {
        "identity": identity,
        "title": _heading(body) or name,
        "description": _opening_sentence(body),
        "words": sum(child["words"] for child in children),
        "children": children,
    }


def generate(checkout: Path) -> list[View]:
    """The one ``index-tree`` view file describing ``checkout``."""
    tracked = {
        relpath for relpath in git_files(checkout) if relpath.endswith(MARKDOWN_SUFFIX)
    }
    reached: set[str] = set()
    root = _directory_node(
        checkout, "", tracked, reached, canonical_repo_name(checkout)
    )
    payload: dict[str, Any] = {
        "root": root,
        "unindexed": [
            _file_node(checkout, relpath, tracked)
            for relpath in sorted(tracked - reached)
        ],
    }
    return [
        View(
            relpath=f"{KIND_NAME}.json",
            envelope=state.envelope(
                KIND_NAME,
                KIND_VERSION,
                TITLE,
                None,
                payload,
                commit=state.head_commit(checkout),
                generator=__name__,
            ),
        )
    ]


KIND = Kind(name=KIND_NAME, version=KIND_VERSION, per_subject=False, generate=generate)
