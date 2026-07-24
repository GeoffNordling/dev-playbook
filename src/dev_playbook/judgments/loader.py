"""Discover, parse, and validate judgment declarations from a repo's YAML files.

A repo opts in with a ``[tool.judgments]`` table in its ``pyproject.toml`` that
points (via ``paths`` globs) at one or more declaration files. This module turns
those files into validated :class:`Declaration` records: it owns root resolution,
file discovery, and the structural field rules. It does no file I/O on the
declared evidence/reference paths -- existence and path-format are the lint's and
``prepare``'s job -- and raises a clear error on the first violation it finds.
"""

import argparse
import re
import sys
import tomllib
from collections.abc import Iterator
from pathlib import Path, PurePosixPath
from typing import NamedTuple, TypeGuard

import yaml

from dev_playbook.findings import print_rules, render
from dev_playbook.judgments.bench import VALID_EFFORTS, VALID_MODELS

_ID_CHARSET = re.compile(r"[A-Za-z0-9._-]+")

# The rule ids judgments-lint can emit, one per existing error family: a
# malformed declaration (structural/field validation, at the declaring YAML
# file) and a bad evidence/reference path (absolute, `..`, or missing). Each id
# is a module-level constant so every emission site references the constant, not
# a raw literal, and --list-rules cannot drift from what the code emits.
DECLARATION = "semantic-validation.declaration"
EVIDENCE_PATH = "semantic-validation.evidence-path"
JUDGMENTS_RULES = (DECLARATION, EVIDENCE_PATH)


class DeclarationError(ValueError):
    """A malformed judgment declaration, located at its ``source`` file.

    Carries the offending ``source`` path and a path-free ``detail`` so callers
    format the location themselves -- repo-relative for a finding -- rather than
    reverse-engineering it back out of the message with string surgery. Subclasses
    ValueError so callers that catch ValueError (and ``load``'s fail-loud contract)
    keep working; ``str()`` is ``"{source}: {detail}"``.
    """

    def __init__(self, source: Path, detail: str) -> None:
        """Keeps the source path and detail apart, and formats them as the message."""
        self.source = source
        self.detail = detail
        super().__init__(f"{source}: {detail}")


class LintFinding(NamedTuple):
    """One judgments-lint finding, located at the declaring YAML file."""

    location: str  # repo-relative path to the declaring file
    rule: str  # in JUDGMENTS_RULES
    message: str


class Declaration(NamedTuple):
    """One parsed, validated judgment from a declaration YAML file."""

    id: str
    claim: str
    evidence: list[str]  # >=1 repo-root-relative paths
    reference: list[str]  # repo-root-relative paths; [] when omitted in the YAML
    model: str  # in VALID_MODELS
    effort: str  # in VALID_EFFORTS


def resolve_root(start: Path | None = None) -> Path | None:
    """Nearest ancestor of ``start`` whose ``pyproject.toml`` has ``[tool.judgments]``.

    Walks up from ``start`` (default: the current working directory). Returns the
    first directory that opts in, or ``None`` if no ancestor does -- in which case
    there are no judgments.
    """
    here = (start or Path.cwd()).resolve()
    for directory in (here, *here.parents):
        pyproject = directory / "pyproject.toml"
        if pyproject.is_file() and _has_judgments_table(pyproject):
            return directory
    return None


def _has_judgments_table(pyproject: Path) -> bool:
    """Whether ``pyproject``'s parsed contents carry a ``[tool.judgments]`` table."""
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    # a pyproject without a [tool] table is valid -- it just means no judgments
    return "judgments" in data.get("tool", {})


def load(root: Path | None) -> list[Declaration]:
    """Discover, parse, and validate every judgment declared under ``root``.

    Returns ``[]`` when ``root`` is ``None`` (no opted-in config). Otherwise it
    expands the ``[tool.judgments].paths`` globs against ``root``, parses each
    matched YAML file, and validates the structural field rules. It does no file
    I/O on the declared evidence/reference paths.
    """
    if root is None:
        return []
    pairs: list[tuple[Declaration, Path]] = []
    for path, result in _parsed_files(root):
        if isinstance(result, DeclarationError):
            raise result
        pairs.extend((declaration, path) for declaration in result)
    declarations: list[Declaration] = []
    for declaration, source, original in _dedup(pairs):
        if original is not None:
            raise ValueError(
                f"duplicate judgment id {declaration.id!r}: in {source} and {original}"
            )
        declarations.append(declaration)
    return declarations


def _discover(root: Path) -> list[Path]:
    """Expand the config's ``paths`` globs against ``root`` into sorted YAML files."""
    matched: set[Path] = set()
    for glob in _declaration_globs(root):
        matched.update(root.glob(glob))
    return sorted(matched)


def _parsed_files(
    root: Path,
) -> Iterator[tuple[Path, list[Declaration] | DeclarationError]]:
    """The single discover-and-parse traversal, consumed by load and the lint.

    Yields ``(file, declarations)`` for each discovered declaration file, or
    ``(file, error)`` when that one file is malformed -- so ``load`` can raise on
    the error and the lint can turn it into a finding, both over one walk. A
    configuration error (a bad ``[tool.judgments].paths``) raises out of the
    initial ``_discover`` before any file is yielded.
    """
    for path in _discover(root):
        try:
            yield path, _parse_file(path)
        except DeclarationError as error:
            yield path, error


def _dedup(
    pairs: list[tuple[Declaration, Path]],
) -> Iterator[tuple[Declaration, Path, Path | None]]:
    """Tag each ``(declaration, source)`` with the earlier source of a dup id.

    Yields ``(declaration, source, original)`` where ``original`` is the file
    that first declared this id, or ``None`` when the id is new. The one place
    duplicate-id detection lives: ``load`` raises on a duplicate and the lint
    reports it, but neither re-implements the bookkeeping.
    """
    first_source: dict[str, Path] = {}
    for declaration, source in pairs:
        original = first_source.get(declaration.id)
        if original is None:
            first_source[declaration.id] = source
        yield declaration, source, original


def _declaration_globs(root: Path) -> list[str]:
    """The ``[tool.judgments].paths`` globs from ``root``'s ``pyproject.toml``.

    A ``[tool.judgments]`` table that is present but declares no ``paths`` (or an
    empty ``paths``) is a hard configuration error: the repo opted in but pointed
    nowhere.
    """
    pyproject = root / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    paths = data["tool"]["judgments"].get("paths")
    if not _is_str_list(paths) or not paths:
        raise DeclarationError(
            pyproject, "[tool.judgments] must declare a non-empty 'paths' list"
        )
    return paths


def _parse_file(path: Path) -> list[Declaration]:
    """Parse one declaration YAML file into validated :class:`Declaration` records.

    Rejects a structurally-malformed file -- a non-mapping document, or a
    ``judgments`` value that is not a list -- with the module's clear, file-named
    ``ValueError`` before iterating, so a plausible typo surfaces as that uniform
    error rather than a raw ``TypeError``/``AttributeError`` traceback.
    """
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as error:
        raise DeclarationError(
            path, " ".join(f"invalid YAML: {error}".split())
        ) from error
    if not isinstance(document, dict):
        raise DeclarationError(
            path, "top-level YAML must be a mapping with a 'judgments' key"
        )
    judgments = document.get("judgments", [])
    if not isinstance(judgments, list):
        raise DeclarationError(path, "'judgments' must be a list")
    return [_to_declaration(item, path) for item in judgments]


def _to_declaration(item: object, source: Path) -> Declaration:
    """Validate one parsed YAML judgment object into a :class:`Declaration`.

    Enforces the structural field rules fail-loud, raising on the first
    violation with a message naming the offending ``id`` (or ``source`` file,
    when the ``id`` itself is the problem).
    """
    if not isinstance(item, dict):
        raise DeclarationError(source, f"each judgment must be a mapping, got {item!r}")
    id = _require(item, "id", source, "<unknown>")
    if not isinstance(id, str) or not id:
        raise DeclarationError(source, "judgment 'id' must be a non-empty string")
    if _ID_CHARSET.fullmatch(id) is None:
        raise DeclarationError(
            source,
            f"judgment {id!r}: 'id' has illegal characters (allowed: A-Za-z0-9._-)",
        )
    claim = _require(item, "claim", source, id)
    if not isinstance(claim, str) or not claim.strip():
        raise DeclarationError(
            source, f"judgment {id!r}: 'claim' must be a non-empty string"
        )
    evidence = _require(item, "evidence", source, id)
    if not _is_str_list(evidence):
        raise DeclarationError(
            source, f"judgment {id!r}: 'evidence' must be a list of paths"
        )
    if not evidence:
        raise DeclarationError(
            source, f"judgment {id!r}: 'evidence' must list at least one path"
        )
    reference = item.get("reference") or []
    if not _is_str_list(reference):
        raise DeclarationError(
            source, f"judgment {id!r}: 'reference' must be a list of paths"
        )
    model = _require(item, "model", source, id)
    if not isinstance(model, str) or model not in VALID_MODELS:
        raise DeclarationError(
            source,
            f"judgment {id!r}: 'model' {model!r} is not one of {sorted(VALID_MODELS)}",
        )
    effort = _require(item, "effort", source, id)
    if not isinstance(effort, str) or effort not in VALID_EFFORTS:
        raise DeclarationError(
            source,
            f"judgment {id!r}: 'effort' {effort!r} is not one of {sorted(VALID_EFFORTS)}",
        )
    return Declaration(id, claim, evidence, reference, model, effort)


def _require(item: dict[str, object], field: str, source: Path, id: str) -> object:
    """Return ``item[field]`` or raise a fail-loud missing-required-field error."""
    if field not in item:
        raise DeclarationError(
            source, f"judgment {id!r}: missing required field {field!r}"
        )
    return item[field]


def _is_str_list(value: object) -> TypeGuard[list[str]]:
    """Whether ``value`` is a list whose every element is a string."""
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def by_id(declarations: list[Declaration], id: str) -> Declaration:
    """Return the declaration with the given ``id``; raise if there is none."""
    for declaration in declarations:
        if declaration.id == id:
            return declaration
    raise ValueError(f"unknown judgment id: {id!r}")


def lint_findings(root: Path | None) -> list[LintFinding]:
    """Statically validate a repo's declarations; return findings (empty if clean).

    Runs the loader's field validation, then the static subset of ``prepare``'s
    path rules -- each evidence/reference path must be relative (not absolute, no
    ``..``) and exist. Each finding is located at the declaring YAML file (a
    configuration error at ``pyproject.toml``): a malformed declaration is
    ``semantic-validation.declaration``, a bad evidence/reference path is
    ``semantic-validation.evidence-path``. A repo with no ``[tool.judgments]`` config
    validates nothing. One run surfaces every offending file and path.
    """
    if root is None:
        return []
    findings: list[LintFinding] = []
    parsed: list[tuple[Declaration, Path]] = []
    try:
        for path, result in _parsed_files(root):
            if isinstance(result, DeclarationError):
                findings.append(
                    LintFinding(_rel(result.source, root), DECLARATION, result.detail)
                )
            else:
                parsed.extend((declaration, path) for declaration in result)
    except DeclarationError as error:
        # A configuration error (a bad [tool.judgments].paths) surfaces from the
        # initial discovery, before any file parses: one finding at pyproject.
        return [LintFinding(_rel(error.source, root), DECLARATION, error.detail)]

    for declaration, source, original in _dedup(parsed):
        rel = _rel(source, root)
        if original is not None:
            findings.append(
                LintFinding(
                    rel,
                    DECLARATION,
                    f"duplicate judgment id {declaration.id!r} "
                    f"(also in {_rel(original, root)})",
                )
            )
            continue
        for candidate in (*declaration.evidence, *declaration.reference):
            problem = _path_problem(candidate, root)
            if problem is not None:
                findings.append(
                    LintFinding(
                        rel, EVIDENCE_PATH, f"judgment {declaration.id!r}: {problem}"
                    )
                )
    return findings


def _rel(path: Path, root: Path) -> str:
    """A discovered file's repo-relative location, for a finding's location slot."""
    return str(path.relative_to(root))


def lint_cli(argv: list[str] | None = None) -> int:
    """Console-script entry point: lint the repo's judgments, findings to stdout.

    Resolves the repo root, runs :func:`lint_findings`, prints every finding as a
    GNU finding line to stdout and a summary count to stderr, and returns 1 if
    there were any findings else 0. ``--list-rules`` prints the rule ids and
    exits 0 without needing a repository. Registered as the ``judgments-lint``
    console script and called by the ``scripts/judgments-lint`` pre-commit shim,
    so both channels behave alike.
    """
    parser = argparse.ArgumentParser(
        prog="judgments-lint",
        description="Lint a repo's judgment declarations against the schema and paths.",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="repository root to lint (default: current directory)",
    )
    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="print the rule ids this detector can emit, one per line, and exit",
    )
    args = parser.parse_args(argv)
    if args.list_rules:
        return print_rules(JUDGMENTS_RULES)

    findings = lint_findings(resolve_root(Path(args.directory)))
    for finding in findings:
        print(render(finding.location, finding.rule, finding.message))
    if findings:
        print(f"judgments-lint: {len(findings)} finding(s)", file=sys.stderr)
        return 1
    return 0


def _path_problem(path: str, root: Path) -> str | None:
    """The static path defect (absolute / ``..`` / missing), or ``None`` if clean."""
    pure = PurePosixPath(path)
    if pure.is_absolute():
        return f"evidence/reference path must be relative, got absolute: {path!r}"
    if ".." in pure.parts:
        return f"evidence/reference path must not contain '..': {path!r}"
    if not (root / path).exists():
        return f"evidence/reference path does not exist: {path!r}"
    return None
