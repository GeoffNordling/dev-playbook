"""The check registry: one entry per rule id, filled by decorators.

A check is one function that decides one rule; ``@check("<family>.<slug>")``
on it writes one entry, id to function. A rule a tool decides, ruff or
shellcheck, is registered with the hook's name in place of a function by
:func:`tool_check`. The runner stamps the id on every finding a function
yields, ``playbook checks`` prints the dict, and the meta-test reads it. No
hand-kept tuple of ids exists anywhere.

Check modules live under ``dev_playbook.checks``, one per ``standards/``
directory and named for it, so a rule's family and its module coincide;
:func:`load` imports them all and returns the dict.
"""

import importlib
import pkgutil
import re
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass

from dev_playbook import checks
from dev_playbook.model import Repo

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


def module_name(family: str) -> str:
    """The module a family's checks live in: the family with hyphens as underscores.

    ``doc-type`` is ``dev_playbook.checks.doc_type``, and its tests are
    ``tests/dev_playbook/checks/test_doc_type.py``.
    """
    return family.replace("-", "_")


def check(
    id: str, *, needs: Iterable[str] = (), registry: dict[str, Check] = CHECKS
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
    id: str, *, hook: str, module: str, registry: dict[str, Check] = CHECKS
) -> None:
    """Register ``id`` as decided by the pre-commit hook ``hook``.

    ``module`` is the registering module's ``__name__``, so the entry sits in
    its family's module like any other.
    """
    add(Check(id, None, hook, frozenset(), module), registry)


def add(entry: Check, registry: dict[str, Check] = CHECKS) -> None:
    """Put one entry in the registry, or raise :class:`RegistryError`."""
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


def load() -> dict[str, Check]:
    """Import every module under ``dev_playbook.checks``; return the registry."""
    for info in pkgutil.iter_modules(checks.__path__):
        importlib.import_module(f"{checks.__name__}.{info.name}")
    return CHECKS
