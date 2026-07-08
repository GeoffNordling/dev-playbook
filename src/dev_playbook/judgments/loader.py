"""Discover, parse, and validate judgment declarations from a repo's YAML files.

A repo opts in with a ``[tool.judgments]`` table in its ``pyproject.toml`` that
points (via ``paths`` globs) at one or more declaration files. This module turns
those files into validated :class:`Declaration` records: it owns root resolution,
file discovery, and the structural field rules. It does no file I/O on the
declared evidence/reference paths -- existence and path-format are the lint's and
``prepare``'s job -- and raises a clear error on the first violation it finds.
"""

import re
import sys
import tomllib
from pathlib import Path, PurePosixPath
from typing import NamedTuple, TypeGuard

import yaml

from dev_playbook.judgments.bench import VALID_EFFORTS, VALID_MODELS

_ID_CHARSET = re.compile(r"[A-Za-z0-9._-]+")


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


def lint(root: Path | None) -> list[str]:
    """Statically validate a repo's declarations; return all errors (empty if clean).

    Runs the loader's field validation, then the static subset of ``prepare``'s
    path rules -- each evidence/reference path must be relative (not absolute, no
    ``..``) and exist. A repo with no ``[tool.judgments]`` config validates
    nothing. A structural error short-circuits to that one error; otherwise every
    offending path is reported, so one run surfaces them all.
    """
    if root is None:
        return []
    try:
        declarations = load(root)
    except (ValueError, yaml.YAMLError) as error:
        return [str(error)]
    errors: list[str] = []
    for declaration in declarations:
        for path in (*declaration.evidence, *declaration.reference):
            problem = _path_problem(path, root)
            if problem is not None:
                errors.append(f"judgment {declaration.id!r}: {problem}")
    return errors


def lint_cli() -> int:
    """Console-script entry point: lint the repo's judgments, report on stderr.

    Resolves the repo root, runs :func:`lint`, prints every error and a summary
    count to stderr, and returns 1 if there were any errors else 0. Registered as
    the ``judgments-lint`` console script and called by the
    ``scripts/judgments-lint`` pre-commit shim, so both channels behave alike.
    """
    errors = lint(resolve_root())
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        print(f"judgments-lint: {len(errors)} error(s)", file=sys.stderr)
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
