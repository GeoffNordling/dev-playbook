"""The ``markdown-file`` kind: what one markdown file is, and what touches it.

One view file per tracked markdown file: its frontmatter facts, its word count,
its headings, the links it makes with whether each one resolves, the files that
link back to it, and its source as written
([Registry](/worktree-cloa-viewer-tool-working-docs/registry.md)). It is the
detail behind a CLOA panel, and the whole panel for a file no CLOA kind covers.

``links_in`` is why the generator reads every file before it writes any: the
files pointing at a document are found only by resolving every other document's
links first, so the walk is two passes over one read of the checkout.
"""

import re
from pathlib import Path
from typing import Any, TypedDict

from dev_playbook.cloa_viewer import state
from dev_playbook.cloa_viewer.entry import Kind, View
from dev_playbook.cloa_viewer.identity import citation_repo, is_external, resolve_target
from dev_playbook.gitrepo import canonical_repo_name, git_files
from dev_playbook.md import (
    github_slug,
    lines_outside_fences,
    markdown_links,
    parse_frontmatter,
)

KIND_NAME = "markdown-file"
KIND_VERSION = 1
MARKDOWN_SUFFIX = ".md"
ANCHOR_PREFIX = "#"
# An ATX heading: the hashes say the level, the rest is the text the slug and
# the panel show.
HEADING_PATTERN = re.compile(r"^(#{1,6}) (.+)$")


class Link(TypedDict):
    """One link out: as the document writes it, whether it resolves, and what it names.

    ``identity`` is the file the target names in this checkout, and is null for
    a link that names none — an ``external`` one, or a ``citation`` of another
    repo — so the page opens a target without resolving a path itself.
    """

    target: str
    status: str
    identity: str | None


def _headings(body: str) -> list[dict[str, Any]]:
    """Every heading outside a fence, with the anchor slug GitHub gives it.

    The slug comes from ``md.github_slug``, the rule the workspace's own link
    checking already uses, so a heading identity here and a ``#slug`` in a link
    elsewhere name the same heading.
    """
    headings: list[dict[str, Any]] = []
    for _, line in lines_outside_fences(body):
        match = HEADING_PATTERN.match(line.rstrip())
        if match is None:
            continue
        text = match.group(2)
        headings.append(
            {"level": len(match.group(1)), "text": text, "slug": github_slug(text)}
        )
    return headings


def _target_identity(source: str, target: str, repo: str) -> str:
    """The identity ``target`` names, read from the file at identity ``source``.

    A target that is a bare ``#anchor`` names the file it sits in: it carries no
    path, so ``resolve_target`` would answer with the source's own directory and
    the link would read as broken.
    """
    if target.startswith(ANCHOR_PREFIX):
        return source
    return resolve_target(source, target, repo)


def _link(source: str, target: str, tracked: set[str], repo: str) -> Link:
    """One link out: whether it leaves the checkout, lands in it, or breaks.

    A Citation of another repo is the status ``citation`` and is never checked:
    a generator reads one checkout, and ``ref-lint`` already verifies those
    targets on disk. A Citation of ``repo`` is a link into this checkout like
    any other, so it scores ``ok`` or ``broken`` by the file it names.
    """
    if is_external(target):
        return {"target": target, "status": "external", "identity": None}
    citation = citation_repo(target)
    if citation is not None and citation != repo:
        return {"target": target, "status": "citation", "identity": None}
    identity = _target_identity(source, target, repo)
    status = "ok" if identity in tracked else "broken"
    return {"target": target, "status": status, "identity": identity}


def _links_out(source: str, body: str, tracked: set[str], repo: str) -> list[Link]:
    """Every link the file makes, in reading order, each with its status.

    The target is kept as the document writes it, not as it resolves, because
    the panel shows the reader what the file says.
    """
    links = []
    for _, line in lines_outside_fences(body):
        for _text, target in markdown_links(line):
            links.append(_link(source, target, tracked, repo))
    return links


def _links_in(outbound: dict[str, list[Link]]) -> dict[str, list[str]]:
    """For each subject, the sorted identities of the files that link to it.

    Only a resolving link counts, and only such a link carries an identity;
    and only from another file, because a document's own ``#anchor`` links
    point at itself and are not links in.
    """
    inbound: dict[str, set[str]] = {identity: set() for identity in outbound}
    for source, links in outbound.items():
        for link in links:
            target = link["identity"]
            if link["status"] != "ok" or target is None:
                continue
            if target != source and target in inbound:
                inbound[target].add(source)
    return {identity: sorted(sources) for identity, sources in inbound.items()}


def generate(checkout: Path) -> list[View]:
    """One ``markdown-file`` view for every tracked markdown file in ``checkout``."""
    tracked = set(git_files(checkout))
    repo = canonical_repo_name(checkout)
    subjects = sorted(
        relpath for relpath in tracked if relpath.endswith(MARKDOWN_SUFFIX)
    )
    sources = {
        identity: (checkout / identity).read_text(encoding="utf-8")
        for identity in subjects
    }
    documents = {
        identity: parse_frontmatter(sources[identity]) for identity in subjects
    }
    outbound = {
        identity: _links_out(identity, documents[identity][1], tracked, repo)
        for identity in subjects
    }
    inbound = _links_in(outbound)
    commit = state.head_commit(checkout)
    views = []
    for identity in subjects:
        front, body = documents[identity]
        facts = front or {}
        payload: dict[str, Any] = {
            "type": facts.get("type"),
            "title": facts.get("title"),
            "description": facts.get("description"),
            "words": len(body.split()),
            "headings": _headings(body),
            "links_out": outbound[identity],
            "links_in": inbound[identity],
            "source": sources[identity],
        }
        views.append(
            View(
                relpath=f"{KIND_NAME}/{identity}.json",
                envelope=state.envelope(
                    KIND_NAME,
                    KIND_VERSION,
                    facts.get("title") or identity,
                    identity,
                    payload,
                    commit=commit,
                    generator=__name__,
                ),
            )
        )
    return views


KIND = Kind(name=KIND_NAME, version=KIND_VERSION, per_subject=True, generate=generate)
