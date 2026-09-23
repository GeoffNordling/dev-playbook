"""Audit the ``standards/`` tree against the meta-standard's deterministic rules.

standards-lint is the detector behind the meta-standard, a published hook any
repo can run over its own ``standards/`` tree. It runs in two modes:
**dev-playbook mode**, where the audited tree is dev-playbook itself (or a
fixture simulating it), detected by the canonical consumer template
``standards/build/canonical/.pre-commit-config.yaml`` -- which only the hook
repo hosts; and **consumer mode**, every other repo, which is policed from this
hook's own pinned clone. A repo carrying no standards/ surface
-- neither a catalog nor a Standard directory -- is clean by construction. The
rules, each the id of its heading in standards/standard/tree.md:

  - **directory-layout** — every immediate subdirectory of ``standards/`` is a
    Standard directory: it holds at least one file typed ``Standard``, and every
    tracked ``.md`` under it, ``index.md`` aside, is typed ``Standard``. The only
    flat files under ``standards/`` are README.md and index.md.
  - **the-population** — a file typed ``Standard`` names its population in
    frontmatter, one string.
  - **the-catalog** — ``standards/index.md`` follows its declared ordering:
    README first, then only directories -- (in dev-playbook mode) the
    meta-standard's ``standard/`` when the tree carries it, the rest
    alphabetical by name -- each row carrying the directory index's opening
    sentence verbatim, less its period.
  - **the-hosting-pattern** and **offered-by-the-canonical-template** — the
    detector-hook id sets agree between the published manifest and the local
    block; in dev-playbook mode the canonical consumer template's pinned block
    offers exactly what the manifest publishes. Every detector carries a
    scripts/README.md validation-table row when that file is present — "every
    detector" meaning the playbook-lint roster in dev-playbook mode (consumers
    wire one aggregate hook, so the roster, not the config, enumerates what
    runs) and the local detector hooks in consumer mode.
  - **no-shadowing** — in consumer mode, no local Standard directory may reuse
    an upstream directory's name drawn from this hook's own pinned clone.

Output:
    stdout — one finding per line, ``file:line: standard.rule message``.
    stderr — one readable summary line.
    exit   — 0 clean, 1 findings, 2 cannot run.

Usage:
    standards-lint [directory]
    standards-lint --list-rules
"""

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from dev_playbook import md
from dev_playbook.findings import print_rules, render
from dev_playbook.playbook_lint import DETECTORS

# The dev-playbook checkout this module's hook ships in — the pre-commit clone
# in consumer repos, dev-playbook's own tree when dogfooded. The shadow rule
# resolves its upstream directory set here, since a consumer never carries
# dev-playbook's own Standards. The module sits at src/dev_playbook/, so the
# repo root is three parents up.
HOOK_REPO_ROOT = Path(__file__).resolve().parents[2]

# Every rule id this detector can emit, namespaced by the meta-standard whose
# question it answers. Each id is a module-level constant so every emission site
# references the constant, never a raw literal, and RULES (what --list-rules
# prints) cannot drift from what the detector actually emits.
DIRECTORY_LAYOUT = "standard.every-subdirectory-a-standard-directory"
THE_POPULATION = "doc-type.the-frontmatter-names-the-population"
THE_CATALOG = "standard.the-catalog-lists-every-directory"
NO_SHADOWING = "standard.no-shadowing"
THE_HOSTING_PATTERN = "standard.every-detector-is-reachable-and-listed"
OFFERED_BY_THE_CANONICAL_TEMPLATE = "standard.offered-by-the-canonical-template"

RULES = (
    DIRECTORY_LAYOUT,
    THE_POPULATION,
    THE_CATALOG,
    NO_SHADOWING,
    THE_HOSTING_PATTERN,
    OFFERED_BY_THE_CANONICAL_TEMPLATE,
)

STANDARD_TYPE = "Standard"
# The types a Standard directory admits beside its index.
ADMITTED_TYPES = frozenset({STANDARD_TYPE})
STANDARDS = "standards"
CATALOG = "standards/index.md"
README = "standards/README.md"
INDEX = "index.md"
META_DIR = "standard"

# Any ATX heading, used to bound the opening paragraph of a document.
_HEADING = re.compile(r"^#{1,6}\s")
# A sentence terminator: a period at end of line or before a space. Requiring the
# boundary keeps ``CLAUDE.md`` and ``index.md`` from ending a sentence mid-word.
_SENTENCE_END = re.compile(r"\.(?=\s|$)")
# An index bullet: ``- [title](/root-absolute) — description``; the target's
# ``#`` anchor is dropped and the description, when present, captured.
_BULLET = re.compile(
    r"^\s*[-*]\s+\[([^\]]*)\]\((/[^)\s#]+)[^)]*\)(?:\s+—\s+(.*?))?\s*$"
)


class CannotRun(Exception):
    """A precondition the detector cannot judge past; surfaces as exit 2."""


@dataclass(frozen=True)
class Finding:
    """One nonconformance: a repo-relative location, a rule id, and a message."""

    file: str
    line: int | None
    rule: str
    message: str

    def render(self) -> str:
        """The finding as one GNU-format line."""
        return render(self.file, self.rule, self.message, self.line)


# --- shared helpers ---------------------------------------------------------


def _relpath(path: Path, root: Path) -> str:
    """A file's repo-relative POSIX path."""
    return str(PurePosixPath(path.relative_to(root)))


def _frontmatter(path: Path) -> dict | None:
    """A doc's parsed frontmatter mapping, or None when it carries none.

    Raises CannotRun when the file cannot be read (a dangling catalog target) or
    its frontmatter will not parse (malformed YAML), so either surfaces as exit 2
    rather than an uncaught traceback -- matching ``_load_yaml``'s boundary.
    """
    import yaml

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        return md.parse_frontmatter(text)[0]
    except (OSError, yaml.YAMLError) as err:
        raise CannotRun(f"cannot read frontmatter of {path.name}: {err}") from err


def _tracked(root: Path) -> list[str]:
    """Every tracked file of the checkout, repo-relative.

    Discovery runs ``git ls-files``, so a non-git ``root`` funnels into CannotRun
    here -- the single chokepoint that covers every caller (the audited root's
    optional-surface guard and the shadow rule's ``hook_repo_root`` scan alike),
    so a non-git checkout surfaces as the module's uniform exit-2 diagnostic
    rather than an uncaught ``CalledProcessError``.
    """
    try:
        found = md.find_files(root)
    except subprocess.CalledProcessError as err:
        raise CannotRun(
            f"cannot scan {STANDARDS}/: {root} is not a git checkout"
        ) from err
    return [_relpath(p, root) for p in found]


def _standard_dirs(root: Path) -> list[str]:
    """Every immediate subdirectory of ``standards/``, by name, sorted.

    A directory is one that holds any tracked file at any depth.
    """
    names = {
        parts[1]
        for rel in _tracked(root)
        if len(parts := PurePosixPath(rel).parts) >= 3 and parts[0] == STANDARDS
    }
    return sorted(names)


def _members(root: Path) -> list[str]:
    """Every tracked ``.md`` in a Standard directory that is not an index."""
    return sorted(
        rel
        for rel in _tracked(root)
        if len(parts := PurePosixPath(rel).parts) >= 3
        and parts[0] == STANDARDS
        and parts[-1].endswith(".md")
        and parts[-1] != INDEX
    )


def _flat_strays(root: Path) -> list[str]:
    """Flat ``standards/*.md`` files that are neither README.md nor index.md."""
    return sorted(
        rel
        for rel in _tracked(root)
        if len(parts := PurePosixPath(rel).parts) == 2
        and parts[0] == STANDARDS
        and parts[1].endswith(".md")
        and parts[1] not in {"README.md", INDEX}
    )


def _dev_playbook_mode(root: Path) -> bool:
    """Whether the audited tree is dev-playbook (or a fixture simulating it).

    The probe is the canonical consumer template's presence --
    ``standards/build/canonical/.pre-commit-config.yaml``. Only the hook repo
    hosts that template; consumers copy *from* it and never carry it. Keying on
    the meta-standard's directory ``standards/standard/`` instead would collide
    with the shadow rule -- a consumer may innocently name a directory
    ``standard``, which must stay in consumer mode so the shadow rule catches
    it, not flip the whole audit into dev-playbook mode. The template cannot be
    created innocently, so it carries no such ambiguity, and the probe is
    self-consistent with hook-surfaces' canonical leg, which reads exactly this
    file -- that leg can never CannotRun on an absent template. Path equality
    against the hook clone is deliberately avoided: it would put every fixture
    in consumer mode and break every dev-playbook-mode test.
    """
    return (root / CANONICAL_CONFIG).is_file()


# --- standard.every-subdirectory-a-standard-directory and doc-type.the-frontmatter-names-the-population ------------------


def check_directory_layout(root: Path) -> list[Finding]:
    """Flag a stray flat file, an unadmitted member, a Standard-less directory, or a populationless Standard."""
    findings: list[Finding] = []
    for rel in _flat_strays(root):
        findings.append(
            Finding(
                rel,
                None,
                DIRECTORY_LAYOUT,
                f"flat file under {STANDARDS}/; a Standard is "
                f"{STANDARDS}/<name>/<topic>.md",
            )
        )
    with_standard: set[str] = set()
    for rel in _members(root):
        front = _frontmatter(root / rel)
        doctype = front.get("type") if front else None
        if doctype not in ADMITTED_TYPES:
            findings.append(
                Finding(
                    rel,
                    None,
                    DIRECTORY_LAYOUT,
                    f"typed {doctype!r} in a Standard directory; a Standard "
                    f"directory admits {', '.join(sorted(ADMITTED_TYPES))}",
                )
            )
            continue
        if doctype != STANDARD_TYPE:
            continue
        with_standard.add(PurePosixPath(rel).parts[1])
        population = front.get("population") if front else None
        if not isinstance(population, str) or not population.strip():
            findings.append(
                Finding(
                    rel,
                    None,
                    THE_POPULATION,
                    "a Standard names its population: a `population` string in "
                    "frontmatter",
                )
            )
    for name in _standard_dirs(root):
        if name not in with_standard:
            findings.append(
                Finding(
                    f"{STANDARDS}/{name}",
                    None,
                    DIRECTORY_LAYOUT,
                    f"directory holds no file typed '{STANDARD_TYPE}'",
                )
            )
    return findings


# --- standard.the-catalog-lists-every-directory ---------------------------------------------------


def _opening_sentence(path: Path) -> tuple[int, str] | None:
    """The ``(line, text)`` of the first sentence after a document's H1.

    The sentence is the run up to the first period at a word boundary, taken from
    the paragraph following the H1 with its line breaks flattened to spaces.
    Returns None when the document has no H1 or nothing follows it.
    """
    lines = list(md.content_lines(path))
    start = next((i for i, (_, ln) in enumerate(lines) if ln.startswith("# ")), None)
    if start is None:
        return None
    paragraph: list[str] = []
    number: int | None = None
    for num, line in lines[start + 1 :]:
        if not line.strip():
            if paragraph:
                break
            continue
        if _HEADING.match(line):
            break
        if number is None:
            number = num
        paragraph.append(line.strip())
    if number is None:
        return None
    text = " ".join(paragraph)
    end = _SENTENCE_END.search(text)
    return number, text[: end.start()] if end else text


def _index_bullets(path: Path) -> list[tuple[str, str, str | None]]:
    """An index's ``(title, target, description)`` bullets in listing order.

    Targets are repo-relative (the leading ``/`` and any ``#`` anchor stripped);
    the description is None when the bullet carries none.
    """
    bullets: list[tuple[str, str, str | None]] = []
    for _, line in md.content_lines(path):
        m = _BULLET.match(line)
        if m:
            bullets.append((m.group(1), m.group(2).lstrip("/"), m.group(3)))
    return bullets


def _is_directory_bullet(target: str) -> bool:
    """Whether a catalog bullet points at a child directory's ``index.md``."""
    return PurePosixPath(target).name == INDEX


def check_catalog_order(root: Path, dev_playbook_mode: bool) -> list[Finding]:
    """Flag a catalog whose entries depart from the declared order or wording.

    okf-lint already enforces catalog *membership* (the ``Ordering:`` marker
    exempts only its generic alphabetical rule), so this checks order and each
    row's description: README, then directories only -- the meta-standard's
    ``standard/`` *when the tree is dev-playbook's own and carries it*, the rest
    alphabetical by name -- each row repeating its directory index's opening
    sentence verbatim, less the period. The meta lead slot is mode-gated -- only
    a dev-playbook-mode tree that carries ``standards/standard/`` gets it. In
    consumer mode a directory named ``standard`` is an ordinary directory sorted
    among the others, so a consumer that names one draws only the intended
    ``no-shadowing`` finding, never a spurious catalog-order complaint about a
    meta-standard it has no concept of.
    """
    if not (root / CATALOG).is_file():
        raise CannotRun(f"no catalog at {CATALOG}")
    bullets = _index_bullets(root / CATALOG)
    targets = [t for _, t, _ in bullets]
    for target in targets:
        if not (root / target).is_file():
            raise CannotRun(f"catalog row targets a missing file: {target}")
    strays = [t for t in targets if t != README and not _is_directory_bullet(t)]
    if strays:
        return [
            Finding(
                CATALOG,
                None,
                THE_CATALOG,
                f"the catalog lists README.md and directories only; found {strays[0]}",
            )
        ]

    meta_index = f"{STANDARDS}/{META_DIR}/{INDEX}"
    has_meta_lead = dev_playbook_mode and (root / meta_index).is_file()
    dirs = [t for t in targets if _is_directory_bullet(t)]
    rest = [t for t in dirs if not (has_meta_lead and t == meta_index)]
    expected = (
        [README]
        + ([meta_index] if has_meta_lead else [])
        + sorted(rest, key=lambda t: PurePosixPath(t).parent.name)
    )
    if targets != expected:
        offender = next(
            (a for a, b in zip(targets, expected, strict=False) if a != b), ""
        )
        return [
            Finding(
                CATALOG,
                None,
                THE_CATALOG,
                "entries are out of the declared order (README, meta-standard, "
                f"directories by name); first out of place: {offender}",
            )
        ]

    findings: list[Finding] = []
    for _, target, description in bullets:
        if not _is_directory_bullet(target):
            continue
        opening = _opening_sentence(root / target)
        if opening is None:
            findings.append(
                Finding(target, None, THE_CATALOG, "index states no opening sentence")
            )
            continue
        if description != opening[1]:
            findings.append(
                Finding(
                    CATALOG,
                    None,
                    THE_CATALOG,
                    f"row for {target} must carry the index's opening sentence "
                    f"verbatim: {opening[1]!r}",
                )
            )
    return findings


# --- standard.every-detector-is-reachable-and-listed -------------------------------------------

MANIFEST = ".pre-commit-hooks.yaml"
LOCAL_CONFIG = ".pre-commit-config.yaml"
CANONICAL_CONFIG = "standards/build/canonical/.pre-commit-config.yaml"
SCRIPTS_README = "scripts/README.md"

# A markdown table row's first backticked cell: ``| `name` | ... |``.
_TABLE_NAME = re.compile(r"^\s*\|\s*`([^`]+)`\s*\|")


def _scripts_entry_ids(hooks: list[dict]) -> set[str]:
    """The ids of hooks whose ``entry`` is a ``scripts/`` path (the detectors).

    Non-detector hooks (make-check, validate-manifest -- ``language: system``)
    fall outside by this entry-path scoping.
    """
    return {
        hook["id"]
        for hook in hooks
        if isinstance(hook.get("entry"), str) and hook["entry"].startswith("scripts/")
    }


def _load_yaml(path: Path) -> object:
    """Parse a YAML file, or raise CannotRun naming it when it will not read."""
    import yaml

    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as err:
        raise CannotRun(f"cannot read {path.name}: {err}") from err


def _local_hooks(root: Path) -> list[dict]:
    """The hooks of the ``repo: local`` block in the local pre-commit config.

    An absent ``.pre-commit-config.yaml`` wires nothing -- the common consumer
    that only pulls dev-playbook's pinned block carries no local config -- so it
    reads as no hooks, never CannotRun (the ``scripts/README.md`` guard shape).
    """
    if not (root / LOCAL_CONFIG).is_file():
        return []
    config = _load_yaml(root / LOCAL_CONFIG)
    if not isinstance(config, dict):
        return []
    for repo in config.get("repos", []):
        if isinstance(repo, dict) and repo.get("repo") == "local":
            return [h for h in repo.get("hooks", []) if isinstance(h, dict)]
    return []


def _canonical_dev_hook_ids(root: Path) -> set[str]:
    """The hook ids in the canonical template's pinned dev-playbook block.

    Consumers wire dev-playbook's detectors through this one ``repo:`` block, so
    it must list exactly the published manifest's detector hooks. Ids in the
    template's other blocks -- third-party repos, its own ``repo: local`` block --
    are out of scope: a detector misplaced there is one a consumer never gets, so
    scoping to the pinned block is what lets that misplacement fail as missing.
    """
    config = _load_yaml(root / CANONICAL_CONFIG)
    ids: set[str] = set()
    if isinstance(config, dict):
        for repo in config.get("repos", []):
            if not isinstance(repo, dict) or "dev-playbook" not in str(
                repo.get("repo", "")
            ):
                continue
            for hook in repo.get("hooks") or []:
                if isinstance(hook, dict) and "id" in hook:
                    ids.add(hook["id"])
    return ids


def _readme_table_names(root: Path) -> set[str]:
    """Every backticked first-cell name in a scripts/README.md table.

    Called only when scripts/README.md is present -- the sole caller guards on
    that file's existence -- so the read needs no existence check of its own.
    """
    path = root / SCRIPTS_README
    return {
        m.group(1)
        for _, line in md.content_lines(path)
        if (m := _TABLE_NAME.match(line))
    }


def _manifest_ids(root: Path) -> tuple[set[str], set[str]]:
    """The manifest's ``(all published ids, detector ids)``.

    Detector ids are the subset whose ``entry`` is a ``scripts/`` path; the full
    set additionally carries the published non-detectors (validate-manifest,
    ``language: system``). The mirror compare uses the detector subset; the
    canonical leg uses the full set.

    An absent ``.pre-commit-hooks.yaml`` publishes nothing -- a consumer that
    adopts the standards without publishing hooks of its own carries none -- so
    it reads as empty, never CannotRun (the ``scripts/README.md`` guard shape).
    """
    if not (root / MANIFEST).is_file():
        return set(), set()
    raw = _load_yaml(root / MANIFEST)
    hooks = [h for h in raw if isinstance(h, dict)] if isinstance(raw, list) else []
    all_ids = {h["id"] for h in hooks if "id" in h}
    return all_ids, _scripts_entry_ids(hooks)


def check_hook_surfaces(
    root: Path,
    dev_playbook_mode: bool,
    roster: tuple[str, ...] = DETECTORS,
) -> list[Finding]:
    """The published-hook surfaces agree.

    The detector-hook id sets (hooks whose entry is a ``scripts/`` path) must be
    equal between the published manifest and the local block -- in both modes.
    In dev-playbook mode the canonical consumer template's pinned block must
    offer exactly what the manifest publishes -- consumers carry no canonical
    template, so that leg is dev-playbook-only.

    The per-detector leg -- rowed in the scripts/README.md validation table when
    that file is present -- runs over the set that actually enumerates what the
    commit gate runs. In consumer mode that is the local detector hooks; in
    dev-playbook mode it is ``roster`` (the playbook-lint dispatch list -- the
    local block carries only the aggregate hook, which owns no rules).
    """
    manifest_all, manifest = _manifest_ids(root)
    local = _scripts_entry_ids(_local_hooks(root))

    findings: list[Finding] = []

    def host(location: str, message: str) -> None:
        findings.append(Finding(location, None, THE_HOSTING_PATTERN, message))

    def offered(location: str, message: str) -> None:
        findings.append(
            Finding(location, None, OFFERED_BY_THE_CANONICAL_TEMPLATE, message)
        )

    # Mirror: the manifest's detectors and the local block's detectors agree.
    for name in sorted(manifest - local):
        host(LOCAL_CONFIG, f"manifest hook {name} is missing from the local block")
    for name in sorted(local - manifest):
        host(LOCAL_CONFIG, f"local hook {name} is not in the published manifest")

    # Canonical menu: the pinned dev-playbook block offers exactly the published
    # manifest. Dev-playbook-only -- consumers have none.
    if dev_playbook_mode:
        canonical = _canonical_dev_hook_ids(root)
        for name in sorted(manifest_all - canonical):
            offered(
                CANONICAL_CONFIG,
                f"manifest hook {name} is missing from the canonical consumer "
                "template's pinned dev-playbook block",
            )
        for name in sorted(canonical - manifest_all):
            offered(
                CANONICAL_CONFIG,
                f"canonical consumer template hook {name} is not in the published "
                "manifest",
            )

    detectors = set(roster) if dev_playbook_mode else local
    if (root / SCRIPTS_README).is_file():
        table = _readme_table_names(root)
        for name in sorted(detectors - table):
            host(SCRIPTS_README, f"detector {name} is missing from the README table")
    return findings


# --- standard.no-shadowing --------------------------------------------------


def check_shadows_upstream(root: Path, hook_repo_root: Path) -> list[Finding]:
    """Flag any local Standard directory whose name shadows an upstream one (consumer mode).

    The upstream set is the ``standards/<name>/`` directory names of
    ``hook_repo_root`` -- the pinned clone this hook ships in. A local directory
    that reuses an upstream name silently overrides dev-playbook's Standard of
    that name, so the collision is caught at the consumer's commit gate.
    Self-policing: no network, no workspace scan -- a collision introduced
    upstream surfaces at the consumer's next pin bump as a red gate, resolved
    locally.

    A non-git ``hook_repo_root`` funnels into CannotRun through ``_tracked``,
    the single chokepoint for every git scan -- so if the clone the hook ships in
    is not a git checkout, that surfaces as the module's uniform exit-2 diagnostic
    rather than an uncaught ``CalledProcessError``.
    """
    upstream = set(_standard_dirs(hook_repo_root))
    return [
        Finding(
            f"{STANDARDS}/{name}",
            None,
            NO_SHADOWING,
            f"local directory shadows the upstream {STANDARDS}/{name}/",
        )
        for name in _standard_dirs(root)
        if name in upstream
    ]


# --- the walk ---------------------------------------------------------------


def audit(
    root: Path,
    *,
    hook_repo_root: Path = HOOK_REPO_ROOT,
    roster: tuple[str, ...] = DETECTORS,
) -> list[Finding]:
    """Run every applicable rule over ``root`` and return the combined findings.

    A repo carrying no standards/ surface -- neither a catalog nor a Standard
    directory -- is clean by construction: there is nothing to police, so the
    walk returns no findings rather than can't-run on the absent catalog (the
    harness-files-lint optional-surface precedent). A repo with directories but
    no catalog is a malformed surface, so it still fails loud through
    ``check_catalog_order``. The canonical-template leg of hook-surfaces and the
    shadow rule are gated on the mode the marker probe resolves: the shadow rule
    fires in consumer mode only, since dev-playbook's own directories cannot
    shadow themselves.
    """
    if not (root / CATALOG).is_file() and not _standard_dirs(root):
        return []
    dev_playbook_mode = _dev_playbook_mode(root)
    findings: list[Finding] = []
    findings.extend(check_directory_layout(root))
    findings.extend(check_catalog_order(root, dev_playbook_mode))
    findings.extend(check_hook_surfaces(root, dev_playbook_mode, roster))
    if not dev_playbook_mode:
        findings.extend(check_shadows_upstream(root, hook_repo_root))
    return findings


def main(argv: list[str] | None = None) -> int:
    """Scan the standards tree and print one finding per line; return the exit code."""
    parser = argparse.ArgumentParser(
        prog="standards-lint",
        description="Audit the standards/ tree against the meta-standard's rules.",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="repository root to scan (default: current directory)",
    )
    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="print the rule ids this detector can emit, one per line, and exit",
    )
    args = parser.parse_args(argv)
    if args.list_rules:
        return print_rules(RULES)
    root = Path(args.directory).resolve()

    try:
        findings = audit(root)
    except CannotRun as err:
        print(f"standards-lint: cannot run: {err}", file=sys.stderr)
        return 2

    for f in sorted(findings, key=lambda f: (f.file, f.line or 0, f.rule, f.message)):
        print(f.render())

    if findings:
        print(f"standards-lint: {len(findings)} finding(s)", file=sys.stderr)
        return 1
    print("standards-lint: clean", file=sys.stderr)
    return 0
