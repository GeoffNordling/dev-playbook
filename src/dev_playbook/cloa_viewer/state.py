"""The state directory: where view files live, and the envelope they carry.

The state directory is the whole interface between the server, which writes,
and the viewer, which reads. It sits at
``$XDG_STATE_HOME/cloa-viewer/`` and holds one subdirectory per checkout, named
from that checkout's absolute path so a worktree and its main checkout never
collide. Inside a checkout directory, ``checkout.json`` says which working copy
it describes and every other file is a view file.

Every view file is one envelope: seven top-level fields, governed by
``schemas/envelope.schema.json``, with the kind's own schema governing
``payload`` alone. Nothing here writes a file it has not validated, and
``validate`` raises rather than repairs, because a view file that fails its
schema must reach the screen as an error panel and not as a quietly patched
panel.
"""

import hashlib
import json
import os
import subprocess
from datetime import UTC, datetime
from importlib import resources
from pathlib import Path
from typing import Any

import jsonschema

from dev_playbook.gitrepo import canonical_repo_name, no_git_env

ENVELOPE_VERSION = 1
STATE_DIR_NAME = "cloa-viewer"
DEFAULT_STATE_HOME = ".local/state"
DIGEST_LENGTH = 8
RFC_3339_UTC = "%Y-%m-%dT%H:%M:%SZ"
SCHEMA_PACKAGE = "dev_playbook.cloa_viewer"
SCHEMA_DIR = "schemas"


class ContractError(ValueError):
    """An instance does not match the schema it was checked against."""


def state_root() -> Path:
    """The state directory holding one subdirectory per checkout."""
    # XDG_STATE_HOME is genuinely optional: the spec names ~/.local/state as
    # the value to use when the variable is unset or empty.
    home = os.environ.get("XDG_STATE_HOME") or str(Path.home() / DEFAULT_STATE_HOME)
    return Path(home) / STATE_DIR_NAME


def checkout_dir(checkout: Path) -> Path:
    """The state subdirectory for ``checkout``, named from its absolute path.

    The basename alone would collide across a worktree and its main checkout,
    which usually share it, so a digest of the whole path follows the name.
    """
    resolved = checkout.resolve()
    digest = hashlib.sha256(str(resolved).encode()).hexdigest()[:DIGEST_LENGTH]
    return state_root() / f"{resolved.name}-{digest}"


# --- git facts about a checkout ---


def _rev_parse(checkout: Path, *args: str) -> str:
    """The stripped output of ``git rev-parse`` with ``args`` in ``checkout``."""
    result = subprocess.run(
        ["git", "-C", str(checkout), "rev-parse", *args],
        capture_output=True,
        text=True,
        check=True,
        env=no_git_env(),
    )
    return result.stdout.strip()


def head_commit(checkout: Path) -> str:
    """The full commit hash at ``checkout``'s HEAD."""
    return _rev_parse(checkout, "HEAD")


def branch_name(checkout: Path) -> str:
    """The branch ``checkout`` has checked out, or ``HEAD`` when detached."""
    return _rev_parse(checkout, "--abbrev-ref", "HEAD")


def write_checkout_json(checkout: Path) -> Path:
    """Write ``checkout.json``, the readable facts about ``checkout``.

    The viewer reads only the state directory, so the path, repo name, branch,
    and HEAD it shows in the top bar have to be written down here.
    """
    resolved = checkout.resolve()
    path = checkout_dir(resolved) / "checkout.json"
    write_json(
        path,
        {
            "path": str(resolved),
            "repo": canonical_repo_name(resolved),
            "branch": branch_name(resolved),
            "head": head_commit(resolved),
        },
    )
    return path


def envelope(
    kind: str,
    kind_version: int,
    title: str,
    subject: str | None,
    payload: dict[str, Any],
    *,
    commit: str,
    generator: str,
) -> dict[str, Any]:
    """Wrap ``payload`` in the envelope a view file carries.

    ``subject`` is the identity the file is about, and ``None`` for a
    per-checkout kind such as ``index-tree``.
    """
    return {
        "envelope": ENVELOPE_VERSION,
        "kind": kind,
        "kind_version": kind_version,
        "title": title,
        "subject": subject,
        "stamp": {
            "commit": commit,
            "generated_at": datetime.now(UTC).strftime(RFC_3339_UTC),
            "generator": generator,
        },
        "payload": payload,
    }


def load_schema(name: str) -> dict[str, Any]:
    """Read ``schemas/<name>.schema.json`` out of the package."""
    source = resources.files(SCHEMA_PACKAGE).joinpath(SCHEMA_DIR, f"{name}.schema.json")
    schema: dict[str, Any] = json.loads(source.read_text())
    return schema


def validate(instance: dict[str, Any], schema: dict[str, Any]) -> None:
    """Raise ``ContractError`` naming the first failing field, or return.

    The errors are sorted before one is picked so that the same bad instance
    always names the same field, whatever order the validator found them in.
    """
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(
        validator.iter_errors(instance),
        key=lambda error: (error.json_path, error.message),
    )
    if errors:
        raise ContractError(f"{errors[0].json_path}: {errors[0].message}")


def write_json(path: Path, data: dict[str, Any]) -> None:
    """Write ``data`` to ``path`` atomically, creating parent directories.

    The viewer watches the state directory, so a reader must never see a
    half-written file: the bytes land beside the target and ``os.replace``
    moves them into place in one step.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    staged = path.with_suffix(".tmp")
    staged.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    os.replace(staged, path)
