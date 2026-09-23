"""The build family: the rules of ``standards/build/``.

Every rule is decided by a function over the model. The skeleton rules read
the tracked paths; a directory exists when a tracked file sits under it. The
canonical rules compare a repo's copy against ``repo.canonical``, the copy of
``sources.CANONICAL_DIR`` the package ships, so they compare in every repo.
The Python project rules read the root ``pyproject.toml``; the import package
is its ``project.name`` with each hyphen an underscore, and only the
name-mapping rule holds that name to ``repo.name``.
"""

import ast
import re
import tomllib
from collections.abc import Iterator
from pathlib import PurePosixPath
from typing import Any

import yaml

from dev_playbook import sources
from dev_playbook.check_registry import Finding, check
from dev_playbook.model import Repo

BASE_REQUIRED = (
    "README.md",
    "CLAUDE.md",
    "index.md",
    ".gitignore",
    ".pre-commit-config.yaml",
    "Makefile",
    ".github/workflows/ci.yml",
)
ROOT_ONLY = ("pyproject.toml", "CONTEXT.md", "CANDIDATES.md")
FUTURE_WORK_NAMES = frozenset({"ROADMAP.md", "TODO.md", "BACKLOG.md", "IDEAS.md"})
RUNNABLE_DIRS = ("bin", "tools")
CODE_ROOTS = ("src", "tests", "scripts")
REV_PLACEHOLDER = "<pinned-sha>"
UV_SHEBANG = "#!/usr/bin/env -S uv run --script"
PEP723_OPEN = "# /// script"
REQUIRES_PYTHON = re.compile(r'#\s*requires-python\s*=\s*"([^"]*)"')
ENTRY_POINT = re.compile(r"^([A-Za-z_][\w.]*):main$")

PYPROJECT = "pyproject.toml"
PYTHON_VERSION = ".python-version"
PRE_COMMIT_CONFIG = ".pre-commit-config.yaml"
CI_YML = ".github/workflows/ci.yml"


# --- the layers and the shared readers ---


def _in_canonical(path: str) -> bool:
    """True for a path under the canonical directory or its shipped copy, quoted material."""
    return path.startswith(
        (sources.CANONICAL_DIR + "/", sources.SHIPPED_CANONICAL_DIR + "/")
    )


def _has_dir(repo: Repo, name: str) -> bool:
    """True when a tracked file sits under the directory ``name``."""
    return any(path.startswith(name + "/") for path in repo.files)


def _is_python(repo: Repo) -> bool:
    """The Python layer: a root ``pyproject.toml`` exists."""
    return PYPROJECT in repo.contents


def _is_package(repo: Repo) -> bool:
    """The Python package layer: a Python repo in which ``src/`` exists."""
    return _is_python(repo) and _has_dir(repo, "src")


def _scripts_hold_python(repo: Repo) -> bool:
    """True when ``scripts/`` holds a Python file."""
    return any(path.startswith("scripts/") for path in repo.python)


def _carries_canonical(repo: Repo) -> bool:
    """True for the repo that tracks the canonical directory, dev-playbook."""
    return any(path.startswith(sources.CANONICAL_DIR + "/") for path in repo.files)


def _canonical(repo: Repo, name: str) -> str:
    """The text of one canonical source file, from the copy the model carries."""
    return repo.canonical[name].decode("utf-8")


def _pyproject(repo: Repo) -> dict[str, Any] | None:
    """The parsed root ``pyproject.toml``; None when absent or not TOML."""
    if PYPROJECT not in repo.contents:
        return None
    try:
        return tomllib.loads(repo.text(PYPROJECT))
    except tomllib.TOMLDecodeError:
        return None


def _get(data: object, dotted: str) -> object | None:
    """The value at a dotted key path, or None where a key is missing."""
    current = data
    for key in dotted.split("."):
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def _package(repo: Repo) -> str | None:
    """The import package: ``project.name`` with each hyphen an underscore."""
    name = _get(_pyproject(repo), "project.name")
    return name.replace("-", "_") if isinstance(name, str) else None


# --- skeleton.md ---


@check("build.files-every-repo-carries")
def files_every_repo_carries(repo: Repo) -> Iterator[Finding]:
    """The base files exist at the root, and ``.github/workflows/ci.yml`` exists."""
    for path in BASE_REQUIRED:
        if path not in repo.contents:
            yield Finding(path, None, "required in every repo")


@check("build.one-at-the-root-or-none")
def one_at_the_root_or_none(repo: Repo) -> Iterator[Finding]:
    """``pyproject.toml``, ``CONTEXT.md``, and ``CANDIDATES.md`` sit at the root only."""
    for path in repo.files:
        name = PurePosixPath(path).name
        if name in ROOT_ONLY and path != name and not _in_canonical(path):
            yield Finding(path, None, f"{name} lives at the repo root only")


@check("build.no-other-future-work-file")
def no_other_future_work_file(repo: Repo) -> Iterator[Finding]:
    """No ``ROADMAP.md``, ``TODO.md``, ``BACKLOG.md``, or ``IDEAS.md`` at any depth."""
    for path in repo.files:
        if PurePosixPath(path).name in FUTURE_WORK_NAMES and not _in_canonical(path):
            yield Finding(
                path,
                None,
                "uncommitted work lives in CANDIDATES.md, committed work in issues",
            )


@check("build.runnables-live-in-scripts")
def runnables_live_in_scripts(repo: Repo) -> Iterator[Finding]:
    """No ``bin/`` and no ``tools/`` directory exists at the root."""
    for name in RUNNABLE_DIRS:
        if _has_dir(repo, name):
            yield Finding(
                f"{name}/",
                None,
                "checked-in runnables live in scripts/, not a root bin/ or tools/",
            )


@check("build.dependencies-live-in-pyprojecttoml")
def dependencies_live_in_pyprojecttoml(repo: Repo) -> Iterator[Finding]:
    """No file named ``requirements.txt`` exists anywhere in the tree."""
    for path in repo.files:
        if PurePosixPath(path).name == "requirements.txt" and not _in_canonical(path):
            yield Finding(path, None, "dependencies live in pyproject.toml + uv.lock")


@check("build.lock-file-tracked-python-version-pinned")
def lock_file_tracked_python_version_pinned(repo: Repo) -> Iterator[Finding]:
    """In a Python repo, ``uv.lock`` is tracked and ``.python-version`` exists."""
    if not _is_python(repo):
        return
    if "uv.lock" not in repo.contents:
        yield Finding("uv.lock", None, "must be committed in a python repo")
    if PYTHON_VERSION not in repo.contents:
        yield Finding(PYTHON_VERSION, None, "required in a python repo")


@check("build.one-package-under-src")
def one_package_under_src(repo: Repo) -> Iterator[Finding]:
    """In a Python package repo, ``src/`` holds only the import package's directory."""
    package = _package(repo)
    if not _is_package(repo) or package is None:
        return
    entries = {
        PurePosixPath(path).parts[1] for path in repo.files if path.startswith("src/")
    }
    message = f"src/ holds exactly one package, named '{package}'"
    for extra in sorted(entries - {package}):
        yield Finding(f"src/{extra}", None, message)
    if not any(path.startswith(f"src/{package}/") for path in repo.files):
        yield Finding(f"src/{package}/", None, message)


@check("build.tests-present")
def has_tests(repo: Repo) -> Iterator[Finding]:
    """Where ``src/`` sits beside ``pyproject.toml`` or scripts hold Python, tests exist."""
    if (_is_package(repo) or _scripts_hold_python(repo)) and not _has_dir(
        repo, "tests"
    ):
        yield Finding(
            "tests/", None, "required once src/ exists or scripts/ holds Python"
        )


# --- canonical.md ---


def _byte_compare(repo: Repo, path: str, name: str) -> Iterator[Finding]:
    """A finding when ``path`` exists and differs from the canonical ``name``."""
    if path in repo.contents and repo.text(path) != _canonical(repo, name):
        yield Finding(path, None, f"must be byte-identical to the canonical {name}")


@check("build.ciyml-byte-identical-to-canonical")
def ciyml_byte_identical(repo: Repo) -> Iterator[Finding]:
    """``.github/workflows/ci.yml`` is byte-identical to the canonical ``ci.yml``."""
    yield from _byte_compare(repo, CI_YML, "ci.yml")


@check("build.python-version-byte-identical-to-canonical")
def python_version_byte_identical(repo: Repo) -> Iterator[Finding]:
    """``.python-version`` is byte-identical to the canonical one."""
    yield from _byte_compare(repo, PYTHON_VERSION, PYTHON_VERSION)


def _line_matches(canon: str, actual: str) -> bool:
    """One canonical line against one copy line; the rev placeholder takes any value."""
    canon, actual = canon.rstrip(), actual.rstrip()
    if REV_PLACEHOLDER in canon:
        prefix = canon[: canon.index(REV_PLACEHOLDER)]
        return actual.startswith(prefix) and bool(actual[len(prefix) :].strip())
    return canon == actual


def _find_run(lines: list[str], block: list[str], start: int) -> int | None:
    """The index of the first run of ``lines`` at or after ``start`` matching ``block``."""
    n = len(block)
    for i in range(start, len(lines) - n + 1):
        if all(_line_matches(block[j], lines[i + j]) for j in range(n)):
            return i
    return None


def _config_blocks(text: str) -> list[list[str]]:
    """The canonical pre-commit config split at each ``- repo:`` entry."""
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in text.splitlines():
        if line.startswith("  - repo:") and current:
            blocks.append(current)
            current = []
        current.append(line)
    if current:
        blocks.append(current)
    return blocks


@check("build.pre-commit-configyaml-holds-every-canonical-block")
def holds_every_canonical_block(repo: Repo) -> Iterator[Finding]:
    """``.pre-commit-config.yaml`` holds every canonical block verbatim and in order.

    The repo that carries the canonical directory is exempt from the block
    holding the dev-playbook ``rev``.
    """
    if PRE_COMMIT_CONFIG not in repo.contents:
        return
    exempt = _carries_canonical(repo)
    lines = repo.text(PRE_COMMIT_CONFIG).splitlines()
    position = 0
    for block in _config_blocks(_canonical(repo, PRE_COMMIT_CONFIG)):
        if exempt and any(REV_PLACEHOLDER in line for line in block):
            continue
        found = _find_run(lines, block, position)
        if found is None:
            yield Finding(
                PRE_COMMIT_CONFIG,
                None,
                f"canonical block missing or out of order: '{block[0].strip()}'",
            )
        else:
            position = found + len(block)


@check("build.makefile-holds-its-layers-targets")
def makefile_holds_its_layers_targets(repo: Repo) -> Iterator[Finding]:
    """``Makefile`` holds its layer's canonical fragment verbatim and unbroken."""
    name = "Makefile.python" if _is_python(repo) else "Makefile.base"
    if "Makefile" not in repo.contents:
        return
    source = _canonical(repo, name)
    roots = " ".join(
        root
        for root in CODE_ROOTS
        if any(p.startswith(root + "/") and p.endswith(".py") for p in repo.files)
    )
    block = source.replace("<code-roots>", roots).splitlines()
    if _find_run(repo.text("Makefile").splitlines(), block, 0) is None:
        yield Finding(
            "Makefile",
            None,
            f"canonical {name} targets missing (verbatim; extras may follow)",
        )


@check("build.pyprojecttoml-matches-every-pinned-value")
def pyprojecttoml_matches_every_pinned_value(repo: Repo) -> Iterator[Finding]:
    """The root ``pyproject.toml`` parses and matches every value the canonical one pins."""
    if not _is_python(repo):
        return
    try:
        copy = tomllib.loads(repo.text(PYPROJECT))
    except tomllib.TOMLDecodeError as err:
        yield Finding(PYPROJECT, None, f"does not parse: {err}")
        return
    canon = tomllib.loads(_canonical(repo, PYPROJECT))
    expected: dict[str, object] = {
        key: _get(canon, key)
        for key in (
            "project.requires-python",
            "tool.pytest.ini_options.testpaths",
            "tool.ruff.target-version",
            "tool.ruff.line-length",
            "tool.ruff.lint.select",
            "tool.ruff.lint.ignore",
            "tool.ruff.lint.pydocstyle.convention",
        )
    }
    package = _package(repo)
    if package is not None:
        expected["tool.ruff.lint.isort.known-first-party"] = [package]
    mypy = _get(canon, "tool.mypy")
    assert isinstance(mypy, dict)
    expected.update({f"tool.mypy.{key}": value for key, value in mypy.items()})
    if _has_dir(repo, "src"):
        build = _get(canon, "build-system")
        assert isinstance(build, dict)
        expected.update({f"build-system.{k}": v for k, v in build.items()})
    else:
        if _get(copy, "build-system") is not None:
            yield Finding(
                PYPROJECT, None, "a scripts-only repo (no src/) omits [build-system]"
            )
        expected["tool.uv.package"] = False
    for key, value in expected.items():
        actual = _get(copy, key)
        if actual != value:
            yield Finding(PYPROJECT, None, f"{key} must be {value!r}, got {actual!r}")
    floors = _get(canon, "dependency-groups.dev")
    assert isinstance(floors, list)
    dev = _get(copy, "dependency-groups.dev")
    for floor in floors:
        if not isinstance(dev, list) or floor not in dev:
            yield Finding(
                PYPROJECT, None, f"dependency-groups.dev must contain {floor!r}"
            )


def _patterns(text: str) -> list[str]:
    """The patterns of a ``.gitignore``: stripped lines, no blanks, no comments."""
    lines = (line.strip() for line in text.splitlines())
    return [line for line in lines if line and not line.startswith("#")]


@check("build.gitignore-holds-every-canonical-pattern")
def gitignore_holds_every_canonical_pattern(repo: Repo) -> Iterator[Finding]:
    """``.gitignore`` holds every pattern of the canonical ``.gitignore``."""
    if ".gitignore" not in repo.contents:
        return
    have = set(_patterns(repo.text(".gitignore")))
    for pattern in _patterns(_canonical(repo, ".gitignore")):
        if pattern not in have:
            yield Finding(".gitignore", None, f"missing baseline pattern '{pattern}'")


def _ruff_rev(config: object) -> str | None:
    """The ``rev`` of the ruff-pre-commit block, without its leading ``v``."""
    repos = _get(config, "repos")
    for block in repos if isinstance(repos, list) else []:
        url = _get(block, "repo")
        rev = _get(block, "rev")
        if isinstance(url, str) and url.endswith("/ruff-pre-commit"):
            return str(rev).removeprefix("v")
    return None


@check("build.one-version-set")
def one_version_set(repo: Repo) -> Iterator[Finding]:
    """The canonical Python version and ruff version are each written once."""
    pyproject_path = f"{sources.CANONICAL_DIR}/{PYPROJECT}"
    config_path = f"{sources.CANONICAL_DIR}/{PRE_COMMIT_CONFIG}"
    version = _canonical(repo, PYTHON_VERSION).strip()
    canon = tomllib.loads(_canonical(repo, PYPROJECT))
    for key, value in (
        ("project.requires-python", f">={version}"),
        ("tool.ruff.target-version", "py" + version.replace(".", "")),
        ("tool.mypy.python_version", version),
    ):
        actual = _get(canon, key)
        if actual != value:
            yield Finding(
                pyproject_path,
                None,
                f"{key} must be {value!r} for .python-version {version}, "
                f"got {actual!r}",
            )
    rev = _ruff_rev(yaml.safe_load(_canonical(repo, PRE_COMMIT_CONFIG)))
    dev = _get(canon, "dependency-groups.dev")
    floors = [
        entry.removeprefix("ruff>=")
        for entry in (dev if isinstance(dev, list) else [])
        if isinstance(entry, str) and entry.startswith("ruff>=")
    ]
    if floors != [rev]:
        yield Finding(
            config_path,
            None,
            f"the ruff rev ({rev}) and the ruff>= floor in {pyproject_path} "
            f"({', '.join(floors) or 'none'}) must carry the same version",
        )


# --- python.md ---


@check("build.the-repo-directory-names-the-project-and-package")
def names_the_project_and_package(repo: Repo) -> Iterator[Finding]:
    """``project.name`` is the repository's directory name lowercased.

    The repository's name is ``repo.name``, the same from the main checkout
    and every worktree.
    """
    pyproject = _pyproject(repo)
    if pyproject is None:
        return
    expected = repo.name.lower()
    actual = _get(pyproject, "project.name")
    if actual != expected:
        yield Finding(
            PYPROJECT, None, f"project.name must be {expected!r}, got {actual!r}"
        )


def _defines_main(tree: ast.Module) -> bool:
    """True when a module binds ``main`` at its top level."""
    return "main" in {name for node in tree.body for name in _bound_names(node)}


def _bound_names(node: ast.stmt) -> list[str]:
    """The names one top-level statement binds: a def, an assignment, an import."""
    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
        return [node.name]
    if isinstance(node, ast.Assign):
        return [t.id for t in node.targets if isinstance(t, ast.Name)]
    if isinstance(node, ast.ImportFrom | ast.Import):
        return [a.asname or a.name for a in node.names]
    return []


@check("build.every-entry-point-resolves-to-a-modules-main")
def entry_points_resolve_to_main(repo: Repo) -> Iterator[Finding]:
    """Every ``[project.scripts]`` value is ``<module>:main`` in the package, defining it."""
    scripts = _get(_pyproject(repo), "project.scripts")
    package = _package(repo)
    if not isinstance(scripts, dict) or package is None:
        return
    for name, value in scripts.items():
        match = ENTRY_POINT.match(value) if isinstance(value, str) else None
        if match is None:
            yield Finding(PYPROJECT, None, f"entry point {name} must be <module>:main")
            continue
        module = match.group(1)
        if module != package and not module.startswith(package + "."):
            yield Finding(
                PYPROJECT,
                None,
                f"entry point {name}: {module} is not inside the package {package}",
            )
            continue
        stem = "src/" + module.replace(".", "/")
        source = repo.python.get(stem + ".py") or repo.python.get(stem + "/__init__.py")
        if source is None or source.tree is None or not _defines_main(source.tree):
            yield Finding(
                PYPROJECT, None, f"entry point {name}: {module} does not define main"
            )


@check("build.executable-scripts-carry-the-uv-shebang-and-inline-metadata")
def carry_the_uv_shebang(repo: Repo) -> Iterator[Finding]:
    """An executable Python file under ``scripts/`` opens with the uv shebang and PEP 723."""
    pin = repo.text(PYTHON_VERSION).strip() if PYTHON_VERSION in repo.contents else None
    for path, source in repo.python.items():
        if not path.startswith("scripts/") or path not in repo.executable:
            continue
        lines = source.text.splitlines()
        if not lines or lines[0].rstrip() != UV_SHEBANG:
            yield Finding(
                path, 1, f"executable Python in scripts/ opens with '{UV_SHEBANG}'"
            )
        if not any(line.strip() == PEP723_OPEN for line in lines):
            yield Finding(
                path, None, f"missing PEP 723 inline metadata block ('{PEP723_OPEN}')"
            )
        elif pin is not None:
            declared = next(
                (
                    m.group(1)
                    for line in lines
                    if (m := REQUIRES_PYTHON.match(line.strip()))
                ),
                None,
            )
            if declared != f">={pin}":
                yield Finding(
                    path,
                    None,
                    f'PEP 723 requires-python must be ">={pin}"'
                    " (the repo's .python-version floor)",
                )
