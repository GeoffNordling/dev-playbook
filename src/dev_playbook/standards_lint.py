"""Audit the ``standards/`` tree against the meta-standard's deterministic rules.

standards-lint is the detector behind the meta-standard card. It is
dev-playbook-local: the ``standards/`` tree it audits exists only in this repo,
so the detector is wired in dev-playbook's local pre-commit block alone (the
local-only precedent is validate-manifest). Four rules, each namespaced under
the meta card (``standard.*``):

  - **card-layout** — every flat ``standards/<name>.md`` except README.md and
    index.md is a card: ``type: Standard-Card`` frontmatter and the four cells
    (Define, Audit, Enforce, Adopt) as ``##`` sections, in that order. Contracts
    live in sub-directories, so the flat-file layer is exactly the cards.
  - **catalog-order** — ``standards/index.md`` follows its declared ordering:
    README first, the meta-standard card second, the remaining cards
    alphabetical by title, then the contract docs alphabetical by title,
    directories last.
  - **rule-matrix** — the bidirectional card<->rule check between each card's
    Audit-cell detector citations and the rule prefixes those detectors emit
    (``--list-rules`` is the trusted ground truth).
  - **hook-surfaces** — the detector-hook id sets agree across the published
    manifest, the canonical consumer template, and the local block (modulo the
    declared local-only set ``{standards-lint}``), and every detector hook has
    a scripts/README.md validation-table row and is cited by a card.

Output:
    stdout — one finding per line, ``file:line: standard.rule message``.
    stderr — one human-readable summary line.
    exit   — 0 clean, 1 findings, 2 cannot run.

Usage:
    standards-lint [directory]
    standards-lint --list-rules
"""

import argparse
import re
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from dev_playbook import md
from dev_playbook.findings import print_rules, render

# Every rule id this detector can emit, namespaced by the meta card whose
# question it answers. Each id is a module-level constant so every emission site
# references the constant, never a raw literal, and RULES (what --list-rules
# prints) cannot drift from what the detector actually emits.
CARD_LAYOUT = "standard.card-layout"
CATALOG_ORDER = "standard.catalog-order"
RULE_MATRIX = "standard.rule-matrix"
HOOK_SURFACES = "standard.hook-surfaces"

RULES = (CARD_LAYOUT, CATALOG_ORDER, RULE_MATRIX, HOOK_SURFACES)

CARD_TYPE = "Standard-Card"
CATALOG = "standards/index.md"
README = "standards/README.md"
META_CARD = "standards/standard.md"
# The four cells every card carries as ``##`` sections, in this order.
CELLS = ("Define", "Audit", "Enforce", "Adopt")

# A ``## Heading`` (exactly level two): three ``#`` would fail the ``\s`` after.
_H2 = re.compile(r"^##\s+(.+?)\s*#*\s*$")
# An index bullet: ``- [title](/root-absolute)``; the target's ``#`` anchor and
# any trailing description are dropped.
_BULLET = re.compile(r"^\s*[-*]\s+\[([^\]]*)\]\((/[^)\s#]+)")


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


def _title(path: Path) -> str:
    """A doc's frontmatter title, falling back to its stem for sorting."""
    front = _frontmatter(path)
    title = front.get("title") if front else None
    return title if isinstance(title, str) else path.stem


def _h2_sections(path: Path) -> list[str]:
    """The level-two heading texts of a document, in order."""
    return [m.group(1) for _, line in md.content_lines(path) if (m := _H2.match(line))]


def _is_card_path(rel: str) -> bool:
    """Whether ``rel`` is a flat ``standards/<name>.md`` card slot."""
    parts = PurePosixPath(rel).parts
    return (
        len(parts) == 2
        and parts[0] == "standards"
        and parts[1].endswith(".md")
        and parts[1] not in {"README.md", "index.md"}
    )


def _card_paths(root: Path) -> list[str]:
    """Every flat card slot under ``standards/`` in the checkout, sorted."""
    return sorted(
        rel for p in md.find_md_files(root) if _is_card_path(rel := _relpath(p, root))
    )


# --- standard.card-layout ---------------------------------------------------


def check_card_layout(root: Path) -> list[Finding]:
    """Flag any flat card slot that is not a well-formed standard card."""
    findings: list[Finding] = []
    for rel in _card_paths(root):
        path = root / rel
        front = _frontmatter(path)
        if not front or front.get("type") != CARD_TYPE:
            findings.append(
                Finding(
                    rel, None, CARD_LAYOUT, f"flat card must be typed '{CARD_TYPE}'"
                )
            )
            continue
        sections = [s for s in _h2_sections(path) if s in CELLS]
        missing = [c for c in CELLS if c not in sections]
        if missing:
            findings.append(
                Finding(
                    rel,
                    None,
                    CARD_LAYOUT,
                    f"card is missing the cell(s): {', '.join(missing)}",
                )
            )
        elif len(sections) != len(CELLS):
            # All four present but one repeats — a duplicate, not a reordering.
            duplicates = sorted({c for c in sections if sections.count(c) > 1})
            findings.append(
                Finding(
                    rel,
                    None,
                    CARD_LAYOUT,
                    f"card has duplicate cell(s): {', '.join(duplicates)}",
                )
            )
        elif sections != list(CELLS):
            findings.append(
                Finding(
                    rel,
                    None,
                    CARD_LAYOUT,
                    f"card cells are out of order (want {', '.join(CELLS)})",
                )
            )
    return findings


# --- standard.catalog-order -------------------------------------------------


def _catalog_bullets(root: Path) -> list[tuple[str, str]]:
    """The catalog's ``(title, target)`` bullets in listing order.

    Targets are repo-relative (the leading ``/`` and any ``#`` anchor stripped).
    """
    bullets: list[tuple[str, str]] = []
    for _, line in md.content_lines(root / CATALOG):
        m = _BULLET.match(line)
        if m:
            bullets.append((m.group(1), m.group(2).lstrip("/")))
    return bullets


def _is_directory_bullet(target: str) -> bool:
    """Whether a catalog bullet points at a child directory's ``index.md``."""
    return PurePosixPath(target).name == "index.md"


def check_catalog_order(root: Path) -> list[Finding]:
    """Flag a catalog whose entries depart from the declared order.

    okf-lint already enforces catalog *membership* (the ``Ordering:`` marker
    exempts only its generic alphabetical rule), so this checks order alone:
    README, the meta-standard card, the remaining cards by title, the contract
    docs by title, then directories.
    """
    if not (root / CATALOG).is_file():
        raise CannotRun(f"no catalog at {CATALOG}")
    bullets = _catalog_bullets(root)
    doc_targets = [t for _, t in bullets if not _is_directory_bullet(t)]
    dir_seen = False
    for _, target in bullets:
        if _is_directory_bullet(target):
            dir_seen = True
        elif dir_seen:
            return [
                Finding(
                    CATALOG,
                    None,
                    CATALOG_ORDER,
                    "directory entries must be listed after all document entries",
                )
            ]

    cards = [t for t in doc_targets if _is_card_path(t) and t != META_CARD]
    contracts = [t for t in doc_targets if not _is_card_path(t) and t != README]
    expected = (
        [README, META_CARD]
        + sorted(cards, key=lambda t: _title(root / t).lower())
        + sorted(contracts, key=lambda t: _title(root / t).lower())
    )
    if doc_targets != expected:
        offender = next(
            (a for a, b in zip(doc_targets, expected, strict=False) if a != b),
            "",
        )
        return [
            Finding(
                CATALOG,
                None,
                CATALOG_ORDER,
                "document entries are out of the declared order "
                f"(README, meta-standard, cards by title, contract docs by title); "
                f"first out of place: {offender}",
            )
        ]
    return []


# --- standard.rule-matrix ---------------------------------------------------


def _section_lines(path: Path, heading: str) -> list[str]:
    """The lines under a card's ``## heading`` cell, up to the next ``##``."""
    lines: list[str] = []
    in_section = False
    for _, line in md.content_lines(path):
        m = _H2.match(line)
        if m:
            in_section = m.group(1).strip() == heading
            continue
        if in_section:
            lines.append(line)
    return lines


def _audit_citations(path: Path) -> list[str]:
    """The first-party detector names an Audit cell cites via ``/scripts/`` links.

    Third-party detectors (ruff, shellcheck, shfmt) are cited by name and pin,
    never a ``/scripts/`` link, and non-script pointers (judgment files) target
    other trees -- both fall outside the matrix by this scoping.
    """
    names: list[str] = []
    for line in _section_lines(path, "Audit"):
        for _, target in md.markdown_links(line):
            clean = target.partition("#")[0]
            if clean.startswith("/scripts/"):
                names.append(PurePosixPath(clean).name)
    return names


def _prefix(rule: str) -> str:
    """The card prefix of a ``card.rule`` id -- everything before the first dot."""
    return rule.partition(".")[0]


def check_rule_matrix(
    root: Path, list_rules: Callable[[str, Path], list[str]]
) -> list[Finding]:
    """The bidirectional card<->rule check between cards and their detectors.

    Membership: every Audit-cell ``/scripts/`` pointer is a detector citation,
    and each cited detector must answer ``--list-rules``. Direction 1: every
    ``card.*`` prefix a detector emits belongs to a card whose Audit cell cites
    that detector. Direction 2: every detector citation is backed by at least
    one rule carrying the citing card's prefix.
    """
    card_prefixes = {PurePosixPath(rel).stem for rel in _card_paths(root)}
    cited_by: dict[str, list[str]] = {}  # detector -> card prefixes citing it
    for rel in _card_paths(root):
        for name in _audit_citations(root / rel):
            cited_by.setdefault(name, []).append(PurePosixPath(rel).stem)

    findings: list[Finding] = []
    prefixes_of: dict[str, set[str]] = {}
    for name, citing_prefixes in sorted(cited_by.items()):
        try:
            rules = list_rules(name, root)
        except CannotRun:
            for prefix in citing_prefixes:
                findings.append(
                    Finding(
                        f"standards/{prefix}.md",
                        None,
                        RULE_MATRIX,
                        f"Audit cell cites scripts/{name}, which does not answer "
                        "--list-rules",
                    )
                )
            continue
        prefixes_of[name] = {_prefix(r) for r in rules}
        # Direction 2: each citing card's prefix must be one this detector emits.
        for prefix in citing_prefixes:
            if prefix not in prefixes_of[name]:
                findings.append(
                    Finding(
                        f"standards/{prefix}.md",
                        None,
                        RULE_MATRIX,
                        f"Audit cell cites scripts/{name}, but it emits no "
                        f"{prefix}.* rule",
                    )
                )

    # Direction 1: every emitted prefix belongs to a card that cites the detector.
    for name, prefixes in sorted(prefixes_of.items()):
        for prefix in sorted(prefixes):
            if prefix not in card_prefixes:
                findings.append(
                    Finding(
                        f"scripts/{name}",
                        None,
                        RULE_MATRIX,
                        f"emits {prefix}.* rules, but there is no card "
                        f"standards/{prefix}.md",
                    )
                )
            elif prefix not in cited_by[name]:
                findings.append(
                    Finding(
                        f"standards/{prefix}.md",
                        None,
                        RULE_MATRIX,
                        f"scripts/{name} emits {prefix}.* rules, but this card's "
                        "Audit cell does not cite it",
                    )
                )
    return findings


# --- standard.hook-surfaces -------------------------------------------------

MANIFEST = ".pre-commit-hooks.yaml"
LOCAL_CONFIG = ".pre-commit-config.yaml"
CANONICAL_CONFIG = "standards/build/canonical/.pre-commit-config.yaml"
SCRIPTS_README = "scripts/README.md"
# Detectors wired only in dev-playbook's local block, never published or offered
# to consumers: their audited surface exists only here. standards-lint audits
# the standards/ tree, which no consumer carries (the validate-manifest
# precedent). Kept a constant so the local-only set is declared in one place.
LOCAL_ONLY = frozenset({"standards-lint"})

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
    """The hooks of the ``repo: local`` block in the local pre-commit config."""
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
    """Every backticked first-cell name in a scripts/README.md table."""
    path = root / SCRIPTS_README
    if not path.is_file():
        return set()
    return {
        m.group(1)
        for _, line in md.content_lines(path)
        if (m := _TABLE_NAME.match(line))
    }


def _all_cited_detectors(root: Path) -> set[str]:
    """Every detector any card's Audit cell cites via a ``/scripts/`` link."""
    cited: set[str] = set()
    for rel in _card_paths(root):
        cited.update(_audit_citations(root / rel))
    return cited


def check_hook_surfaces(root: Path) -> list[Finding]:
    """The three detector-hook surfaces agree, modulo the local-only set.

    The detector-hook id sets (hooks whose entry is a ``scripts/`` path) must be
    equal across the published manifest, the canonical consumer template, and
    the local block, modulo ``LOCAL_ONLY``. Every local detector hook must also
    have a scripts/README.md validation-table row and be cited by a card.
    """
    manifest_raw = _load_yaml(root / MANIFEST)
    manifest = _scripts_entry_ids(
        [h for h in manifest_raw if isinstance(h, dict)]
        if isinstance(manifest_raw, list)
        else []
    )
    local = _scripts_entry_ids(_local_hooks(root))
    canonical = _canonical_dev_hook_ids(root)

    findings: list[Finding] = []

    def flag(location: str, message: str) -> None:
        findings.append(Finding(location, None, HOOK_SURFACES, message))

    for name in sorted(manifest - local):
        flag(LOCAL_CONFIG, f"manifest hook {name} is missing from the local block")
    for name in sorted(local - manifest - LOCAL_ONLY):
        flag(
            LOCAL_CONFIG,
            f"local hook {name} is not in the manifest and is not declared local-only",
        )
    for name in sorted(LOCAL_ONLY - local):
        flag(LOCAL_CONFIG, f"local-only hook {name} is missing from the local block")
    for name in sorted(manifest - canonical):
        flag(
            CANONICAL_CONFIG,
            f"manifest hook {name} is missing from the canonical consumer "
            "template's pinned dev-playbook block",
        )
    for name in sorted(canonical - manifest):
        flag(
            CANONICAL_CONFIG,
            f"canonical consumer template hook {name} is not in the published manifest",
        )

    table = _readme_table_names(root)
    cited = _all_cited_detectors(root)
    for name in sorted(local - table):
        flag(SCRIPTS_README, f"detector hook {name} is missing from the README table")
    for name in sorted(local - cited):
        flag(
            f"scripts/{name}",
            f"detector hook {name} is cited by no card's Audit cell",
        )
    return findings


# --- the walk ---------------------------------------------------------------


def audit(root: Path, list_rules: Callable[[str, Path], list[str]]) -> list[Finding]:
    """Run every rule over ``root`` and return the combined findings."""
    findings: list[Finding] = []
    findings.extend(check_card_layout(root))
    findings.extend(check_catalog_order(root))
    findings.extend(check_rule_matrix(root, list_rules))
    findings.extend(check_hook_surfaces(root))
    return findings


def _list_rules_via_subprocess(name: str, root: Path) -> list[str]:
    """Run ``scripts/<name> --list-rules`` and return its printed rule ids.

    The detector's own ``uv run --script`` shebang resolves its dependencies, so
    this is the trusted ground truth format.md §Detectors fixes. Raises
    ``CannotRun`` when the script is absent or does not answer the flag.
    """
    script = root / "scripts" / name
    if not script.is_file():
        raise CannotRun(f"cited detector has no scripts/{name}")
    try:
        result = subprocess.run(
            [str(script), "--list-rules"],
            capture_output=True,
            text=True,
            cwd=root,
            timeout=10,
        )
    except OSError as err:
        raise CannotRun(f"scripts/{name} --list-rules failed: {err}") from err
    except subprocess.TimeoutExpired as err:
        raise CannotRun(f"scripts/{name} --list-rules timed out") from err
    if result.returncode != 0:
        raise CannotRun(f"scripts/{name} does not answer --list-rules")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


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
        findings = audit(root, _list_rules_via_subprocess)
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
