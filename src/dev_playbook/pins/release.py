"""The hook repo as GitHub publishes it: URL, release head, manifest, files.

Everything a pin can point at is read from the remote, never from a checkout
on this machine. pre-commit installs a pin by fetching that object from the
hook repo's URL, so a sha the remote has never seen is not stale, it is
uninstallable; and a consumer's release should not depend on what happens to
be checked out elsewhere on the publishing machine.

The one exception is identity: ``is_hook_repo`` answers whether a path *is*
dev-playbook, which is a fact about the disk.
"""

import base64
import re
from pathlib import Path

import yaml

from dev_playbook import gitrepo
from dev_playbook.errors import ToolError
from dev_playbook.github import gh_api, origin_slug

HOOK_REPO_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_CONFIG = (
    HOOK_REPO_ROOT / "standards" / "build" / "canonical" / ".pre-commit-config.yaml"
)

# The ledger ``update-pins`` appends to, the one file on the hook repo's
# ``main`` whose commits are not releases. If that commit moved the head
# consumers pin, every run would trigger the next; ``release_head`` walks back
# over commits touching this file alone.
LEDGER = "docs/pin-updates.md"
# How many ledger-only commits the walk will step over before refusing.
# ``update-pins`` commits once per run and a run happens once per release, so
# two in a row is already unusual; fifty means the head is not what this
# reader thinks.
RELEASE_WALK_LIMIT = 50


def hook_repo_url() -> str:
    """The published hook-repo URL, read from the canonical config's pinned block."""
    text = CANONICAL_CONFIG.read_text(encoding="utf-8")
    match = re.search(r"-\s*repo:\s*(\S+)\n\s*rev:\s*<pinned-sha>", text)
    if not match:
        raise ToolError(f"no pinned block in {CANONICAL_CONFIG}")
    return match.group(1)


def is_hook_repo(repo: Path) -> bool:
    """Whether ``repo`` is a checkout of the hook repo — its main checkout or any worktree.

    Identity is the shared ``.git`` directory, not the path: this code may be
    running from a worktree of dev-playbook while the workspace lists the main
    checkout, and both are the one repo that dogfoods and pins nothing.
    """
    try:
        return gitrepo.common_dir(repo) == gitrepo.common_dir(HOOK_REPO_ROOT)
    except gitrepo.NotAGitRepository:
        return False


def hook_repo_slug() -> str:
    """``owner/name`` of the hook repo's GitHub origin."""
    slug = origin_slug(HOOK_REPO_ROOT)
    if slug is None:
        raise ToolError(f"no GitHub origin in {HOOK_REPO_ROOT}")
    return slug


def published_head() -> str:
    """The hook repo's ``main`` head sha, as GitHub has it."""
    slug = hook_repo_slug()
    match gh_api(f"repos/{slug}/branches/main"):
        case {"commit": {"sha": str(sha)}}:
            return sha
    raise ToolError(f"cannot read main's head sha from {slug}")


def release_head() -> str:
    """The newest commit on the hook repo's ``main`` that touches anything but the ledger.

    This is the sha a consumer pins. ``published_head`` is the raw head, and the
    two differ only right after ``update-pins`` has recorded a run: that commit
    changes ``LEDGER`` and nothing else, and it is bookkeeping about a release,
    not one. Pinning it would be harmless to the consumer and would trigger
    another run, whose ledger commit would trigger the next, so the walk steps
    back over every such commit to the release underneath. A ledger-only commit
    with no single parent — a root, a merge — is not something this reader can
    walk past, and it refuses rather than guess.
    """
    slug = hook_repo_slug()
    sha = published_head()
    for _ in range(RELEASE_WALK_LIMIT):
        match gh_api(f"repos/{slug}/commits/{sha}"):
            case {"files": list(files), "parents": list(parents)}:
                pass
            case _:
                raise ToolError(f"cannot read commit {sha[:12]} from {slug}")
        touched = {str(entry["filename"]) for entry in files if isinstance(entry, dict)}
        if touched != {LEDGER}:
            return sha
        match parents:
            case [{"sha": str(parent)}]:
                sha = parent
            case _:
                raise ToolError(
                    f"{sha[:12]} touches only {LEDGER} and has "
                    f"{len(parents)} parents; the release head cannot be walked to"
                )
    raise ToolError(
        f"{RELEASE_WALK_LIMIT} consecutive commits on {slug} main touch only "
        f"{LEDGER}; the release head cannot be walked to"
    )


def published_file(slug: str, path: str, ref: str | None = None) -> str | None:
    """The text of ``path`` in ``slug`` at ``ref`` (default branch when None), or None."""
    query = f"?ref={ref}" if ref else ""
    match gh_api(f"repos/{slug}/contents/{path}{query}"):
        case {"encoding": "base64", "content": str(content)}:
            return base64.b64decode(content).decode("utf-8")
    return None


def published_hook_ids(sha: str) -> tuple[str, ...]:
    """The hook ids ``.pre-commit-hooks.yaml`` publishes at ``sha``, as GitHub has it.

    Read at the target sha rather than from the publisher's disk: the consumer
    runs the manifest pre-commit clones at that sha, and a local checkout may
    sit anywhere.
    """
    slug = hook_repo_slug()
    text = published_file(slug, ".pre-commit-hooks.yaml", sha)
    if text is None:
        raise ToolError(f"cannot read .pre-commit-hooks.yaml at {sha[:12]} from {slug}")
    return manifest_ids(text)


def manifest_ids(text: str) -> tuple[str, ...]:
    """The hook ids a ``.pre-commit-hooks.yaml`` body publishes, in file order."""
    manifest = yaml.safe_load(text)
    if not isinstance(manifest, list) or not manifest:
        raise ToolError("the published manifest is not a list of hooks")
    return tuple(str(hook["id"]) for hook in manifest)
