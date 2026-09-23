"""The distribution family: the rules of ``standards/distribution/``.

One rule is decided by a function over the model: a repo that publishes a
``.pre-commit-hooks.yaml`` runs every id it publishes from a ``repo: local``
block of its ``.pre-commit-config.yaml``. The manifest's validity is decided
by ``pre-commit validate-manifest``, which ``playbook-lint`` runs as its
``validate-manifest`` step only where the manifest exists, and is registered
by that name.
"""

from collections.abc import Iterator

import yaml

from dev_playbook.check_registry import Finding, check, tool_check
from dev_playbook.model import Repo

MANIFEST = ".pre-commit-hooks.yaml"
CONFIG = ".pre-commit-config.yaml"

tool_check(
    "distribution.the-manifest-validates", hook="validate-manifest", module=__name__
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
