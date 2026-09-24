"""Read GitHub through the ``gh`` command-line client.

Every workspace-scope fact the tools need — a repo's settings, its labels, a
file on its default branch, a commit's parents — is read over ``gh api``, and
this module is the one place that call is made. The contract is degradation,
not failure: a call that gets no usable answer yields ``None`` for that one
read, so a single bad response becomes one unreachable finding rather than a
traceback that blinds the caller to every other repo. The exception is
authentication, which is a precondition of any run and is checked once up
front (``check_auth``).
"""

import json
import re
import subprocess
from pathlib import Path

from dev_playbook import gitrepo
from dev_playbook.errors import ToolError

REMOTE_SLUG_PATTERN = re.compile(
    r"^(?:git@github\.com:|https://github\.com/)([^/\s]+/[^/\s]+?)(?:\.git)?$"
)


def gh_api(path: str, *, paginate: bool = False) -> object | None:
    """Parsed JSON from ``gh api <path>``, or None when the call fails.

    A non-zero exit or a body that is not JSON (an empty 204, a degraded/HTML
    error page) yields None for that one path. With ``paginate=True``,
    ``gh api --paginate`` follows the Link headers and merges every page's JSON
    array into one array, so a list endpoint with more than a page of results
    is read in full.
    """
    argv = ["gh", "api"]
    if paginate:
        argv.append("--paginate")
    argv.append(path)
    return gh_json(argv)


def gh_graphql(query: str, **variables: str) -> object | None:
    """Parsed JSON from ``gh api graphql``, or None when the call fails.

    The same degradation contract as ``gh_api``: a non-zero exit (which is how
    ``gh`` reports GraphQL errors) or an unparseable body yields None for that
    one call.
    """
    argv = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        argv += ["-f", f"{key}={value}"]
    return gh_json(argv)


def gh_json(argv: list[str]) -> object | None:
    """Parsed JSON from one ``gh`` invocation, or None when the call is unusable."""
    try:
        result = subprocess.run(argv, capture_output=True, text=True)
    except FileNotFoundError as err:
        raise ToolError("gh not found on PATH") from err
    if result.returncode != 0:
        return None
    try:
        parsed: object = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    return parsed


def check_auth() -> None:
    """Stop the run when ``gh`` holds no usable credential.

    An unauthenticated ``gh`` does not fail — it degrades to anonymous requests,
    and anonymity is answered three different ways. A public repo serves its
    REST resources, so labels and issues return real findings. A private repo
    answers 404, indistinguishable from one that was deleted. GraphQL has no
    anonymous mode at all. A run would then print a mix of genuine findings and
    per-repo unreachable lines with nothing telling a reader which was which.
    Refusing to start is the only honest answer.
    """
    try:
        result = subprocess.run(
            ["gh", "auth", "status"], capture_output=True, text=True
        )
    except FileNotFoundError as err:
        raise ToolError("gh not found on PATH") from err
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise ToolError(
            "gh holds no usable credential, so every GitHub read would "
            "silently degrade to an anonymous request. Run `gh auth login`, or "
            f"re-run where the credential store is readable.\n{detail}"
        )


def origin_slug(repo: Path) -> str | None:
    """``owner/name`` from the repo's GitHub origin, or None if there is none."""
    result = subprocess.run(
        ["git", "-C", str(repo), "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        env=gitrepo.no_git_env(),
    )
    if result.returncode != 0:
        return None
    match = REMOTE_SLUG_PATTERN.match(result.stdout.strip())
    return match.group(1) if match else None
