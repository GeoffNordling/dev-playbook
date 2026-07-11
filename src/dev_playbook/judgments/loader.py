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
from pathlib import Path, PurePosixPath
from typing import NamedTuple, TypeGuard

import yaml

from dev_playbook.findings import print_rules, render
from dev_playbook.judgments.bench import VALID_EFFORTS, VALID_MODELS

_ID_CHARSET = re.compile(r"[A-Za-z0-9._-]+")

# The rule ids judgments-audit can emit, one per existing error family: a
# malformed declaration (structural/field validation, at the declaring YAML
# file) and a bad evidence/reference path (absolute, `..`, or missing).
JUDGMENTS_RULES = ("judgments.declaration", "judgments.evidence-path")


class LintFinding(NamedTuple):
    """One judgments-audit finding, located at the declaring YAML file."""

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
    declarations: list[Declaration] = []
    source_of: dict[str, Path] = {}
    for path in _discover(root):
        for declaration in _parse_file(path):
            if declaration.id in source_of:
                raise ValueError(
                    f"duplicate judgment id {declaration.id!r}: "
                    f"in {path} and {source_of[declaration.id]}"
                )
            source_of[declaration.id] = path
            declarations.append(declaration)
    return declarations


def _discover(root: Path) -> list[Path]:
    """Expand the config's ``paths`` globs against ``root`` into sorted YAML files."""
    matched: set[Path] = set()
    for glob in _declaration_globs(root):
        matched.update(root.glob(glob))
    return sorted(matched)


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
        raise ValueError(
            f"{pyproject}: [tool.judgments] must declare a non-empty 'paths' list"
        )
    return paths


def _parse_file(path: Path) -> list[Declaration]:
    """Parse one declaration YAML file into validated :class:`Declaration` records.

    Rejects a structurally-malformed file -- a non-mapping document, or a
    ``judgments`` value that is not a list -- with the module's clear, file-named
    ``ValueError`` before iterating, so a plausible typo surfaces as that uniform
    error rather than a raw ``TypeError``/``AttributeError`` traceback.
    """
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(document, dict):
        raise ValueError(
            f"{path}: top-level YAML must be a mapping with a 'judgments' key"
        )
    judgments = document.get("judgments", [])
    if not isinstance(judgments, list):
        raise ValueError(f"{path}: 'judgments' must be a list")
    return [_to_declaration(item, path) for item in judgments]


def _to_declaration(item: object, source: Path) -> Declaration:
    """Validate one parsed YAML judgment object into a :class:`Declaration`.

    Enforces the structural field rules fail-loud, raising on the first
    violation with a message naming the offending ``id`` (or ``source`` file,
    when the ``id`` itself is the problem).
    """
    if not isinstance(item, dict):
        raise ValueError(f"{source}: each judgment must be a mapping, got {item!r}")
    id = _require(item, "id", source, "<unknown>")
    if not isinstance(id, str) or not id:
        raise ValueError(f"{source}: judgment 'id' must be a non-empty string")
    if _ID_CHARSET.fullmatch(id) is None:
        raise ValueError(
            f"judgment {id!r}: 'id' has illegal characters (allowed: A-Za-z0-9._-)"
        )
    claim = _require(item, "claim", source, id)
    if not isinstance(claim, str) or not claim.strip():
        raise ValueError(f"judgment {id!r}: 'claim' must be a non-empty string")
    evidence = _require(item, "evidence", source, id)
    if not _is_str_list(evidence):
        raise ValueError(f"judgment {id!r}: 'evidence' must be a list of paths")
    if not evidence:
        raise ValueError(f"judgment {id!r}: 'evidence' must list at least one path")
    reference = item.get("reference") or []
    if not _is_str_list(reference):
        raise ValueError(f"judgment {id!r}: 'reference' must be a list of paths")
    model = _require(item, "model", source, id)
    if not isinstance(model, str) or model not in VALID_MODELS:
        raise ValueError(
            f"judgment {id!r}: 'model' {model!r} is not one of {sorted(VALID_MODELS)}"
        )
    effort = _require(item, "effort", source, id)
    if not isinstance(effort, str) or effort not in VALID_EFFORTS:
        raise ValueError(
            f"judgment {id!r}: 'effort' {effort!r} is not one of {sorted(VALID_EFFORTS)}"
        )
    return Declaration(id, claim, evidence, reference, model, effort)


def _require(item: dict[str, object], field: str, source: Path, id: str) -> object:
    """Return ``item[field]`` or raise a fail-loud missing-required-field error."""
    if field not in item:
        raise ValueError(
            f"judgment {id!r} in {source}: missing required field {field!r}"
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
    ``judgments.declaration``, a bad evidence/reference path is
    ``judgments.evidence-path``. A repo with no ``[tool.judgments]`` config
    validates nothing. One run surfaces every offending file and path.
    """
    if root is None:
        return []
    try:
        files = _discover(root)
    except (ValueError, yaml.YAMLError) as error:
        pyproject = root / "pyproject.toml"
        message = " ".join(str(error).split()).replace(f"{pyproject}: ", "")
        return [LintFinding("pyproject.toml", "judgments.declaration", message)]

    findings: list[LintFinding] = []
    source_of: dict[str, Path] = {}
    for path in files:
        rel = str(path.relative_to(root))
        try:
            declarations = _parse_file(path)
        except (ValueError, yaml.YAMLError) as error:
            message = " ".join(str(error).split())
            message = message.replace(f"{path}: ", "").replace(f" in {path}", "")
            findings.append(LintFinding(rel, "judgments.declaration", message))
            continue
        for declaration in declarations:
            if declaration.id in source_of:
                origin = source_of[declaration.id].relative_to(root)
                findings.append(
                    LintFinding(
                        rel,
                        "judgments.declaration",
                        f"duplicate judgment id {declaration.id!r} (also in {origin})",
                    )
                )
                continue
            source_of[declaration.id] = path
            for candidate in (*declaration.evidence, *declaration.reference):
                problem = _path_problem(candidate, root)
                if problem is not None:
                    findings.append(
                        LintFinding(
                            rel,
                            "judgments.evidence-path",
                            f"judgment {declaration.id!r}: {problem}",
                        )
                    )
    return findings


def lint_cli(argv: list[str] | None = None) -> int:
    """Console-script entry point: lint the repo's judgments, findings to stdout.

    Resolves the repo root, runs :func:`lint_findings`, prints every finding as a
    GNU finding line to stdout and a summary count to stderr, and returns 1 if
    there were any findings else 0. ``--list-rules`` prints the rule ids and
    exits 0 without needing a repository. Registered as the ``judgments-audit``
    console script and called by the ``scripts/judgments-audit`` pre-commit shim,
    so both channels behave alike.
    """
    parser = argparse.ArgumentParser(
        prog="judgments-audit",
        description="Lint a repo's judgment declarations against the schema and paths.",
    )
    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="print the rule ids this detector can emit, one per line, and exit",
    )
    args = parser.parse_args(argv)
    if args.list_rules:
        return print_rules(JUDGMENTS_RULES)

    findings = lint_findings(resolve_root())
    for finding in findings:
        print(render(finding.location, finding.rule, finding.message))
    if findings:
        print(f"judgments-audit: {len(findings)} finding(s)", file=sys.stderr)
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
