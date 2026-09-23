"""The standard family: the rules of ``standards/standard/``.

Five rules are decided by functions over the model. Four hold a repo's
``standards/`` tree to its shape: every directory a Standard directory, each
directory index opening with its governing sentence, the catalog
``standards/index.md`` listing the directories in order, and, outside
dev-playbook, no directory with the name of one dev-playbook publishes. One
holds the canonical pre-commit config's dev-playbook block to the ids the
manifest publishes. A repo is dev-playbook where it tracks the canonical
pre-commit config, which only dev-playbook hosts.
"""

import re
from collections.abc import Iterator

import yaml

from dev_playbook import sources
from dev_playbook.check_registry import Finding, check
from dev_playbook.model import MarkdownFile, Repo

STANDARDS = "standards"
CATALOG = "standards/index.md"
README = "standards/README.md"
INDEX = "index.md"
FLAT_FILES = frozenset({"README.md", INDEX})
STANDARD_TYPE = "Standard"
META_DIR = "standard"
MANIFEST = ".pre-commit-hooks.yaml"
CANONICAL_CONFIG = f"{sources.CANONICAL_DIR}/.pre-commit-config.yaml"

# A sentence ends at a period before a space or the end of the text, so the
# period in `index.md` does not end one.
SENTENCE_END = re.compile(r"\.(?=\s|$)")
GOVERNING_SENTENCE = re.compile(r"^\S.* governs \S.* — \S.*$")
# A catalog entry: `- [title](/root-absolute) — description`; the target's
# `#` anchor is dropped and the description, when present, captured.
ENTRY = re.compile(r"^\s*[-*]\s+\[[^\]]*\]\(/([^)\s#]+)[^)]*\)(?:\s+—\s+(.*?))?\s*$")


@check("standard.every-subdirectory-a-standard-directory")
def every_subdirectory_a_standard_directory(repo: Repo) -> Iterator[Finding]:
    """Every ``.md`` under a ``standards/`` directory but an index is a Standard.

    Each directory directly in ``standards/`` holds at least one, and the only
    ``.md`` files directly in ``standards/`` are ``README.md`` and
    ``index.md``.
    """
    with_standard: set[str] = set()
    for path in repo.markdown:
        parts = path.split("/")
        if parts[0] != STANDARDS:
            continue
        if len(parts) == 2:
            if parts[1] not in FLAT_FILES:
                yield Finding(
                    path,
                    None,
                    "the only `.md` files directly in `standards/` are "
                    "`README.md` and `index.md`",
                )
            continue
        if parts[-1] == INDEX:
            continue
        front = repo.markdown[path].frontmatter
        doctype = front.get("type") if front else None
        if doctype != STANDARD_TYPE:
            yield Finding(
                path,
                None,
                f"typed {doctype!r} under `standards/`; it must be `Standard`",
            )
            continue
        with_standard.add(parts[1])
    for name in sorted(_directories(repo) - with_standard):
        yield Finding(
            f"{STANDARDS}/{name}", None, "the directory holds no file typed `Standard`"
        )


@check("standard.directory-index-opens-with-the-governing-sentence")
def opens_with_the_governing_sentence(repo: Repo) -> Iterator[Finding]:
    """The first sentence after the H1 of each directory index has the governing form.

    The form is ``<Name> governs <what> — <the things>``.
    """
    for name in sorted(_directories(repo)):
        path = f"{STANDARDS}/{name}/{INDEX}"
        if path not in repo.markdown:
            continue
        opening = _opening_sentence(repo.markdown[path])
        if opening is None:
            yield Finding(path, None, "no sentence follows the H1")
            continue
        line, sentence = opening
        if not GOVERNING_SENTENCE.match(sentence):
            yield Finding(
                path,
                line,
                "the first sentence has the form `<Name> governs <what> — <the things>`",
            )


@check("standard.the-catalog-lists-every-directory")
def the_catalog_lists_every_directory(repo: Repo) -> Iterator[Finding]:
    """``standards/index.md`` lists ``README.md``, then every directory index in order.

    The directories are alphabetical by name, ``standard/`` first in
    dev-playbook, and each entry carries its index's first sentence less the
    final period. An index with no first sentence is the governing-sentence
    rule's finding, not this one's.
    """
    directories = _directories(repo)
    if CATALOG not in repo.markdown:
        if directories:
            yield Finding(CATALOG, None, "a `standards/` tree has a catalog here")
        return
    lead = [META_DIR] if _in_dev_playbook(repo) and META_DIR in directories else []
    names = lead + sorted(directories - set(lead))
    expected = [README] + [f"{STANDARDS}/{name}/{INDEX}" for name in names]
    entries = _entries(repo.markdown[CATALOG])
    listed = [target for _, target, _ in entries]
    for line, target, _ in entries:
        if target not in expected:
            yield Finding(
                CATALOG,
                line,
                f"lists {target}; the catalog lists `README.md` and directory "
                "indexes only",
            )
    for target in expected:
        if target not in listed:
            yield Finding(CATALOG, None, f"does not list {target}")
    if set(listed) == set(expected) and listed != expected:
        line = next(
            n
            for (n, got, _), want in zip(entries, expected, strict=False)
            if got != want
        )
        yield Finding(
            CATALOG,
            line,
            "out of order: `README.md`, then the directories alphabetical by "
            "name" + (", `standard/` first" if lead else ""),
        )
    for line, target, description in entries:
        if target == README or target not in expected or target not in repo.markdown:
            continue
        opening = _opening_sentence(repo.markdown[target])
        if opening is not None and description != opening[1]:
            yield Finding(
                CATALOG,
                line,
                f"the entry for {target} carries its first sentence: {opening[1]!r}",
            )


@check("standard.no-shadowing")
def no_shadowing(repo: Repo) -> Iterator[Finding]:
    """Outside dev-playbook, no ``standards/`` directory has a name dev-playbook's has."""
    if _in_dev_playbook(repo):
        return
    for name in sorted(_directories(repo) & sources.STANDARD_DIRECTORIES):
        yield Finding(
            f"{STANDARDS}/{name}",
            None,
            f"shadows dev-playbook's `standards/{name}/`",
        )


@check("standard.offered-by-the-canonical-template")
def offered_by_the_canonical_template(repo: Repo) -> Iterator[Finding]:
    """The canonical config's dev-playbook block offers exactly the manifest's hook ids."""
    if not _in_dev_playbook(repo):
        return
    canonical, fault = _load(repo, CANONICAL_CONFIG)
    if fault is not None:
        yield Finding(CANONICAL_CONFIG, None, fault)
        return
    published: set[str] = set()
    if MANIFEST in repo.contents:
        manifest, fault = _load(repo, MANIFEST)
        if fault is not None:
            yield Finding(MANIFEST, None, fault)
            return
        published = _ids(manifest)
    offered = _dev_playbook_ids(canonical)
    for hook in sorted(published - offered):
        yield Finding(
            CANONICAL_CONFIG,
            None,
            f"published hook {hook} is not in the dev-playbook block",
        )
    for hook in sorted(offered - published):
        yield Finding(
            CANONICAL_CONFIG,
            None,
            f"dev-playbook block hook {hook} is not published in {MANIFEST}",
        )


def _in_dev_playbook(repo: Repo) -> bool:
    """Whether the repo tracks the canonical pre-commit config only dev-playbook hosts."""
    return CANONICAL_CONFIG in repo.contents


def _directories(repo: Repo) -> set[str]:
    """The names of the directories directly in ``standards/`` that hold a tracked file."""
    return {
        parts[1]
        for path in repo.files
        if len(parts := path.split("/")) >= 3 and parts[0] == STANDARDS
    }


def _opening_sentence(doc: MarkdownFile) -> tuple[int, str] | None:
    """The line and text of the first sentence after the H1, less its period.

    The sentence is cut from the first paragraph after the H1, its line
    breaks as spaces. None when the file has no H1 or no paragraph after it.
    """
    h1 = next((h for h in doc.headings if h.level == 1), None)
    if h1 is None:
        return None
    heading_lines = {h.line for h in doc.headings}
    paragraph: list[str] = []
    first: int | None = None
    for number, text in doc.content:
        if number <= h1.line:
            continue
        if number in heading_lines:
            break
        if not text.strip():
            if paragraph:
                break
            continue
        if first is None:
            first = number
        paragraph.append(text.strip())
    if first is None:
        return None
    joined = " ".join(paragraph)
    end = SENTENCE_END.search(joined)
    return first, joined[: end.start()] if end else joined


def _entries(doc: MarkdownFile) -> list[tuple[int, str, str | None]]:
    """The catalog's ``(line, target, description)`` entries in order."""
    return [
        (number, m.group(1), m.group(2))
        for number, text in doc.content
        if (m := ENTRY.match(text))
    ]


def _load(repo: Repo, path: str) -> tuple[object, str | None]:
    """The parsed YAML of ``path``, or the error that stopped it."""
    try:
        return yaml.safe_load(repo.text(path)), None
    except yaml.YAMLError as err:
        return None, f"malformed YAML, so the hook ids cannot be read: {err}"


def _ids(hooks: object) -> set[str]:
    """The string ``id`` of each mapping in a list of hooks."""
    if not isinstance(hooks, list):
        return set()
    return {
        h["id"] for h in hooks if isinstance(h, dict) and isinstance(h.get("id"), str)
    }


def _dev_playbook_ids(config: object) -> set[str]:
    """The hook ids of every ``repo:`` block of a pre-commit config naming dev-playbook."""
    if not isinstance(config, dict) or not isinstance(config.get("repos"), list):
        return set()
    return {
        hook
        for block in config["repos"]
        if isinstance(block, dict) and "dev-playbook" in str(block.get("repo", ""))
        for hook in _ids(block.get("hooks"))
    }
