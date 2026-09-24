"""The distribution family: the rules of ``standards/distribution/``.

Three rules are decided by functions over the model: a repo that publishes a
``.pre-commit-hooks.yaml`` runs every id it publishes from a ``repo: local``
block of its ``.pre-commit-config.yaml``; a host, a consumer with its own
deterministic rules or checks, lists the ``playbook-check-local`` hook; and a
repo with that hook sources dev-playbook as a dev dependency at the rev its
config pins. The manifest's validity is decided
by ``pre-commit validate-manifest``, which ``playbook check`` runs as its
``validate-manifest`` step only where the manifest exists, and is registered
by that name. Whether a consumer pins the published head is decided by
``scripts/workspace-lint``, which reads the consumer's config and the hook
repo's head over ``gh api``, and is registered by that hook name.
"""

import re
import tomllib
from collections.abc import Iterator

import yaml

from dev_playbook.check_registry import Finding, check, import_package, tool_check
from dev_playbook.model import Repo
from dev_playbook.pins.config import hook_url, pinned_rev

MANIFEST = ".pre-commit-hooks.yaml"
CONFIG = ".pre-commit-config.yaml"
PYPROJECT = "pyproject.toml"

LOCAL_HOOK = "playbook-check-local"
LOCAL_ENTRY = "uv run --locked playbook check --local"

tool_check(
    "distribution.the-manifest-validates", hook="validate-manifest", module=__name__
)
tool_check(
    "distribution.a-consumer-pins-the-published-head",
    hook="workspace-lint",
    module=__name__,
)


@check("distribution.a-publisher-dogfoods-its-manifest")
def dogfoods_its_manifest(repo: Repo) -> Iterator[Finding]:
    """Every hook id ``.pre-commit-hooks.yaml`` publishes is in a ``repo: local`` block."""
    if MANIFEST not in repo.contents:
        return
    manifest, fault = _load(repo, MANIFEST)
    if fault is not None:
        yield Finding(MANIFEST, None, fault)
        return
    published = _ids(manifest)
    local: set[str] = set()
    if CONFIG in repo.contents:
        config, fault = _load(repo, CONFIG)
        if fault is not None:
            yield Finding(CONFIG, None, fault)
            return
        local = _local_ids(config)
    missing = sorted(published - local)
    if missing:
        yield Finding(
            CONFIG,
            None,
            "a `repo: local` block must list every published hook id "
            f"(missing: {', '.join(missing)})",
        )


@check("distribution.a-host-runs-its-own-checks")
def a_host_runs_its_own_checks(repo: Repo) -> Iterator[Finding]:
    """A consumer with its own deterministic rules or checks lists the local hook."""
    if repo.is_dev_playbook or not _is_host(repo):
        return
    hook = None
    if CONFIG in repo.contents:
        config, fault = _load(repo, CONFIG)
        if fault is not None:
            yield Finding(CONFIG, None, fault)
            return
        hook = _local_hook(config)
    if hook is None:
        yield Finding(
            CONFIG,
            None,
            f"a repo with its own rules or checks lists `{LOCAL_HOOK}` under a "
            "`repo: local` block, or they never run",
        )
    elif hook.get("entry") != LOCAL_ENTRY or hook.get("language") != "system":
        yield Finding(
            CONFIG,
            None,
            f"`{LOCAL_HOOK}` must have `entry: {LOCAL_ENTRY}` and `language: system`",
        )


@check("distribution.a-hosts-dev-playbook-rides-the-pin")
def a_hosts_dev_playbook_rides_the_pin(repo: Repo) -> Iterator[Finding]:
    """A repo with the local hook sources dev-playbook as git at its pinned rev."""
    if repo.is_dev_playbook or CONFIG not in repo.contents:
        return
    config, fault = _load(repo, CONFIG)
    if fault is not None or _local_hook(config) is None:
        return
    url = hook_url(repo.canonical[CONFIG].decode("utf-8"))
    rev = pinned_rev(repo.text(CONFIG), url)
    if rev is None:
        return  # a-consumer-pins-the-published-head reports the missing pin
    want = f'dev-playbook = {{ git = "{url}", rev = "{rev}" }}'
    if PYPROJECT not in repo.contents:
        yield Finding(
            CONFIG, None, f"`{LOCAL_HOOK}` needs a pyproject.toml with {want}"
        )
        return
    pyproject = tomllib.loads(repo.text(PYPROJECT))
    dev = pyproject.get("dependency-groups", {}).get("dev", [])
    if "dev-playbook" not in {_requirement_name(d) for d in dev if isinstance(d, str)}:
        yield Finding(
            PYPROJECT, None, "`[dependency-groups] dev` must list dev-playbook"
        )
    source = pyproject.get("tool", {}).get("uv", {}).get("sources", {})
    if source.get("dev-playbook") != {"git": url, "rev": rev}:
        yield Finding(
            PYPROJECT,
            None,
            f"`[tool.uv.sources]` must hold {want}, the rev {CONFIG} pins",
        )


def _is_host(repo: Repo) -> bool:
    """True for a repo with a deterministic rule under ``standards/`` or a check module."""
    if any(
        t.kind == "deterministic"
        for path, doc in repo.markdown.items()
        if path.startswith("standards/")
        for t in doc.trailers
    ):
        return True
    package = import_package(repo)
    return package is not None and any(
        path.startswith(f"src/{package}/checks/") and path.endswith(".py")
        for path in repo.files
    )


def _local_hook(config: object) -> dict[str, object] | None:
    """The ``playbook-check-local`` hook under a ``repo: local`` block, or None."""
    if not isinstance(config, dict) or not isinstance(config.get("repos"), list):
        return None
    for block in config["repos"]:
        if not isinstance(block, dict) or block.get("repo") != "local":
            continue
        for hook in block.get("hooks") or ():
            if isinstance(hook, dict) and hook.get("id") == LOCAL_HOOK:
                return hook
    return None


def _requirement_name(requirement: str) -> str:
    """The distribution name a PEP 508 requirement names, lowercased."""
    return re.split(r"[\s<>=!~;\[@(]", requirement.strip(), maxsplit=1)[0].lower()


def _load(repo: Repo, path: str) -> tuple[object, str | None]:
    """The parsed YAML of ``path``, or the error that stopped it."""
    try:
        return yaml.safe_load(repo.text(path)), None
    except yaml.YAMLError as err:
        return None, f"malformed YAML, so the published ids cannot be read: {err}"


def _ids(hooks: object) -> set[str]:
    """The string ``id`` of each mapping in a list of hooks."""
    if not isinstance(hooks, list):
        return set()
    return {
        h["id"] for h in hooks if isinstance(h, dict) and isinstance(h.get("id"), str)
    }


def _local_ids(config: object) -> set[str]:
    """The hook ids listed under every ``repo: local`` block of a pre-commit config."""
    if not isinstance(config, dict) or not isinstance(config.get("repos"), list):
        return set()
    return {
        hook
        for block in config["repos"]
        if isinstance(block, dict) and block.get("repo") == "local"
        for hook in _ids(block.get("hooks"))
    }
