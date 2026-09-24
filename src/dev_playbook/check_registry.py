"""The check registry: one entry per rule id, filled by decorators.

A check is one function that decides one rule; ``@check("<family>.<slug>")``
on it writes one entry, id to function. A rule a tool decides, ruff or
shellcheck, is registered with the hook's name in place of a function by
:func:`tool_check`. The runner stamps the id on every finding a function
yields, ``playbook checks`` prints the dict, and the meta-test reads it. No
hand-kept tuple of ids exists anywhere.

The registry has two layers, laid out the same way. dev-playbook's check
modules are ``src/dev_playbook/checks/``, its tests
``tests/dev_playbook/checks/``; a consumer repo whose import package is
``story_forge`` keeps its own in ``src/story_forge/checks/`` and
``tests/story_forge/checks/``. In both, one module per ``standards/``
directory is named for it, so a rule's family and its module coincide.
:func:`load` imports dev-playbook's layer, and with a repo the repo's layer
too, and returns the one dict; :func:`layer_problems` holds the layer a repo
hosts and its Standards together.

The two layers run in two hooks. dev-playbook's runs in the pinned
``playbook-check`` hook, in the environment pre-commit builds for it, which
holds dev-playbook and nothing of the consumer's. A consumer's runs in its
``playbook-check-local`` hook, ``playbook check --local`` in the consumer's
own environment, so its checks can import its package and its dependencies.
"""

import ast
import importlib
import pkgutil
import re
import sys
import tomllib
import types
from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass

from dev_playbook import checks
from dev_playbook.model import Repo, Trailer

# The one environment tag: a check that reads sibling repos on this machine.
WORKSPACE = "workspace"

ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]*\.[a-z0-9][a-z0-9-]*$")


class RegistryError(Exception):
    """A registration that cannot stand: a bad id, a duplicate, a misplaced module."""


@dataclass(frozen=True)
class Finding:
    """One thing a check found: the file, the line where one applies, the message.

    The rule id is not here; the runner stamps it from the registry.
    """

    path: str
    line: int | None
    message: str


CheckFunction = Callable[[Repo], Iterator[Finding]]


@dataclass(frozen=True)
class Check:
    """One registered check: a function or a hook name, never both."""

    id: str
    function: CheckFunction | None
    hook: str | None
    needs: frozenset[str]
    module: str

    @property
    def family(self) -> str:
        """The part of the id before the dot; :func:`module_name` names its module."""
        return self.id.partition(".")[0]

    @property
    def slug(self) -> str:
        """The part of the id after the dot, and the heading it names."""
        return self.id.partition(".")[2]


CHECKS: dict[str, Check] = {}

# The layer a decorator with no ``registry`` writes to: dev-playbook's, except
# while :func:`load` runs a consumer repo's modules.
_layer: dict[str, Check] = CHECKS


def module_name(family: str) -> str:
    """The module a family's checks live in: the family with hyphens as underscores.

    ``doc-type`` is ``dev_playbook.checks.doc_type``, and its tests are
    ``tests/dev_playbook/checks/test_doc_type.py``.
    """
    return family.replace("-", "_")


def check(
    id: str, *, needs: Iterable[str] = (), registry: dict[str, Check] | None = None
) -> Callable[[CheckFunction], CheckFunction]:
    """Register the decorated function as the check that decides ``id``.

    ``needs`` tags the environments the check requires; ``WORKSPACE`` is the
    one tag. An untagged check runs at every gate.
    """

    def register(function: CheckFunction) -> CheckFunction:
        add(Check(id, function, None, frozenset(needs), function.__module__), registry)
        return function

    return register


def tool_check(
    id: str, *, hook: str, module: str, registry: dict[str, Check] | None = None
) -> None:
    """Register ``id`` as decided by the pre-commit hook ``hook``.

    ``module`` is the registering module's ``__name__``, so the entry sits in
    its family's module like any other.
    """
    add(Check(id, None, hook, frozenset(), module), registry)


def add(entry: Check, registry: dict[str, Check] | None = None) -> None:
    """Put one entry in the registry, or raise :class:`RegistryError`.

    With no ``registry``, the entry goes in the layer being loaded.
    """
    if registry is None:
        registry = _layer
    if not ID_PATTERN.match(entry.id):
        raise RegistryError(f"{entry.id}: not <family>.<slug>")
    if entry.id in registry:
        raise RegistryError(f"{entry.id}: registered twice")
    registered_from = entry.module.rpartition(".")[2]
    if registered_from != module_name(entry.family):
        raise RegistryError(
            f"{entry.id}: registered from module {registered_from}, "
            f"not {module_name(entry.family)}"
        )
    registry[entry.id] = entry


def import_package(repo: Repo) -> str | None:
    """The repo's import package: ``project.name`` with each hyphen an underscore.

    None where the repo has no root ``pyproject.toml`` or it names no project.
    """
    if "pyproject.toml" not in repo.contents:
        return None
    name = tomllib.loads(repo.text("pyproject.toml")).get("project", {}).get("name")
    return name.replace("-", "_") if isinstance(name, str) else None


def load(repo: Repo | None = None) -> dict[str, Check]:
    """Import every module under ``dev_playbook.checks``; return the registry.

    With ``repo``, also run the check modules that repo hosts and return both
    layers in one new dict; an id both layers register raises
    :class:`RegistryError`. dev-playbook hosts the first layer, so over
    dev-playbook the second is empty.
    """
    for info in pkgutil.iter_modules(checks.__path__):
        importlib.import_module(f"{checks.__name__}.{info.name}")
    if repo is None:
        return CHECKS
    package = import_package(repo)
    if package is None or package == "dev_playbook":
        return dict(CHECKS)
    layer = load_repo_layer(repo, package)
    if both := sorted(layer.keys() & CHECKS.keys()):
        raise RegistryError(f"{both[0]}: registered by dev-playbook and by {repo.name}")
    return CHECKS | layer


def load_repo_layer(repo: Repo, package: str) -> dict[str, Check]:
    """Run each ``src/<package>/checks/<module>.py``; return what they register.

    Each module runs from the model's bytes as ``<package>.checks.<module>``,
    so a file git does not track is never run, and a second load runs it
    again into a new dict. A module may import ``<package>`` and its
    dependencies, absolutely or relatively, wherever they are installed.
    """
    global _layer
    layer: dict[str, Check] = {}
    _layer = layer
    try:
        for path in repo.files:
            directory, _, filename = path.rpartition("/")
            if directory != f"src/{package}/checks" or not filename.endswith(".py"):
                continue
            name = f"{package}.checks.{filename.removesuffix('.py')}"
            module = types.ModuleType(name)
            module.__file__ = str(repo.root / path)
            module.__package__ = f"{package}.checks"
            sys.modules[name] = module
            exec(compile(repo.contents[path], module.__file__, "exec"), vars(module))
    finally:
        _layer = CHECKS
    return layer


def layer_problems(registry: Mapping[str, Check], repo: Repo) -> list[str]:
    """Where the checks ``repo`` hosts and its Standards fail to match.

    ``registry`` is every check that runs over ``repo``; the layer ``repo``
    hosts is those registered from ``<package>.checks``. Each check in the
    layer is a deterministic rule under ``standards/<family>/`` whose heading
    has the check's slug, and each function has a test ``test_<slug>`` in
    ``tests/<package>/checks/test_<module>.py``; each deterministic rule under
    ``standards/`` is in the registry.
    """
    package = import_package(repo)
    layer = [
        c
        for c in registry.values()
        if package is not None and c.module.startswith(f"{package}.checks.")
    ]
    tests = f"tests/{package}/checks"
    trailers: dict[str, tuple[str, Trailer]] = {
        t.id: (path, t)
        for path, doc in repo.markdown.items()
        if path.startswith("standards/")
        for t in doc.trailers
    }
    problems = []
    for entry in sorted(layer, key=lambda c: c.id):
        if entry.id not in trailers:
            problems.append(f"{entry.id}: no rule under standards/ has this id")
            continue
        path, trailer = trailers[entry.id]
        if trailer.kind != "deterministic":
            problems.append(f"{entry.id}: the rule in {path} is {trailer.kind}")
        if trailer.heading is None or trailer.heading.slug != entry.slug:
            problems.append(
                f"{entry.id}: the rule's heading in {path} is not {entry.slug}"
            )
        if path.split("/")[1] != entry.family:
            problems.append(
                f"{entry.id}: the rule is in {path}, not standards/{entry.family}/"
            )
        if entry.function is not None:
            test_file = f"{tests}/test_{module_name(entry.family)}.py"
            name = "test_" + entry.slug.replace("-", "_")
            if name not in defined_test_names(repo, test_file):
                problems.append(f"{entry.id}: no {name} in {test_file}")
    for id, (path, trailer) in sorted(trailers.items()):
        if trailer.kind == "deterministic" and id not in registry:
            problems.append(f"{id}: the rule in {path} has no check")
    return problems


def defined_test_names(repo: Repo, path: str) -> set[str]:
    """Every ``test_`` function name in one tracked Python file, at any depth."""
    source = repo.python.get(path)
    if source is None or source.tree is None:
        return set()
    return {
        node.name
        for node in ast.walk(source.tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    }
