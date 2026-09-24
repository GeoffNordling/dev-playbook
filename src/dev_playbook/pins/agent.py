"""The headless agent a red repo is handed to, and the PR read back afterwards.

The agent is ``claude -p`` in the red worktree, invoking the
``finish-pin-bump`` skill the way a user would: the prompt is the slash
command plus the state only this process knows — the repo, the worktree, the
sha move, the unmerged branches, the path of the gate's output. Every
instruction about *how* to work the findings and land the PR lives in the
skill, once.

The gate's output travels as a file, never inline. The prompt is one argument
of the ``claude`` command line, and the kernel caps an argument at about 128 KB
(``MAX_ARG_STRLEN``): date-tree's 1364 findings, 185 KB, were refused as
``Argument list too long`` and took the whole run down with them
(2026-09-24). ``update-pins`` writes the file before launching, so the agent
reads it where the arguments say.

Nothing the agent prints is trusted. The one fact the ledger records about a
red repo is its PR, and that is read from GitHub with ``gh pr list``.

**Billing.** A headless run must draw from the subscription
([Headless Operation](/docs/headless.md)), and any credential variable in the
environment outranks the login silently. The agent is not launched while one
is set: an unexplained variable on the publishing machine is a fact to
surface, not to work around.
"""

import os
import subprocess
from pathlib import Path

from dev_playbook.errors import ToolError
from dev_playbook.pins.consumer import Branch

# The agent and the GitHub CLI, as tuples so a test can point each at a
# script; ``gate.GATE`` is the same shape for the same reason.
CLAUDE = ("claude",)
GH = ("gh",)
MODEL = "opus"
EFFORT = "high"
# Working a red repo to green is reading standards, editing, and running the
# gate repeatedly; an hour is generous, and expiry is a hang, not slow work.
TIMEOUT = 3600

SKILL = "/finish-pin-bump"

# The variables that move a headless run off the subscription, from
# docs/headless.md § Billing. ``CLAUDE_CODE_OAUTH_TOKEN`` is not among them: it
# is a subscription credential.
METERED_VARS = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_BASE_URL",
    "CLAUDE_CODE_USE_BEDROCK",
    "CLAUDE_CODE_USE_VERTEX",
    "CLAUDE_CODE_USE_FOUNDRY",
    "ANTHROPIC_PROFILE",
    "ANTHROPIC_FEDERATION_RULE_ID",
    "ANTHROPIC_ORGANIZATION_ID",
)


def prompt(
    repo: str,
    worktree: Path,
    branch: str,
    old: str,
    sha: str,
    ids: tuple[str, ...],
    branches: list[Branch],
    findings: Path,
) -> str:
    """The skill invocation plus the state the skill's arguments carry.

    ``findings`` is the file holding the gate's output at ``sha``; the prompt
    names it and carries none of its text.
    """
    report = "\n".join(f"- {branch.render()}" for branch in branches) or "- none"
    return f"""{SKILL}

Repo: {repo}
Worktree: {worktree} (the working directory), branch {branch}, cut from origin/main
Pin: {old} -> {sha}; hook ids: {", ".join(ids)}
Launched by: update-pins, headless. No user is present; the pull request is the only output read.

Remote branches not merged to main, for the PR body:
{report}

Gate output at {sha[:12]}: {findings}
Read that file for the worklist. It is not inlined here because it can run to
thousands of lines.
"""


def require_subscription_billing() -> None:
    """Refuse to launch the agent while a metered credential would outrank the login."""
    present = [name for name in METERED_VARS if os.environ.get(name)]
    if present:
        raise ToolError(
            f"{', '.join(present)} set in the environment; a headless run would "
            "bill the metered API instead of the subscription (docs/headless.md)"
        )


def run(worktree: Path, task: str, log: Path) -> None:
    """Run the headless agent in ``worktree`` on ``task``, its whole output to ``log``.

    The exit code is not the verdict — the PR's existence is — so a non-zero
    exit is recorded in the log and nothing more. A timeout is a refusal: an
    agent still running after an hour is not working the findings. So is a
    launch the operating system declines — ``claude`` missing from PATH, or
    unrunnable — since the run must go on to the next repo and the ledger.
    """
    require_subscription_billing()
    log.parent.mkdir(parents=True, exist_ok=True)
    argv = [
        *CLAUDE,
        "-p",
        task,
        "--model",
        MODEL,
        "--effort",
        EFFORT,
        "--permission-mode",
        "bypassPermissions",
        "--output-format",
        "json",
    ]
    with log.open("w", encoding="utf-8") as sink:
        try:
            result = subprocess.run(
                argv,
                cwd=worktree,
                stdout=sink,
                stderr=subprocess.STDOUT,
                timeout=TIMEOUT,
            )
        except FileNotFoundError as err:
            raise ToolError(f"{CLAUDE[0]} not found on PATH") from err
        except OSError as err:
            raise ToolError(f"could not launch {CLAUDE[0]}: {err}") from err
        except subprocess.TimeoutExpired as err:
            raise ToolError(
                f"the agent did not finish in {TIMEOUT}s; its log is {log}"
            ) from err
        sink.write(f"\n[update-pins] claude exited {result.returncode}\n")


def open_pr(repo: Path, branch: str) -> str | None:
    """The URL of the open PR whose head is ``branch``, or None.

    Read from GitHub, never from what an agent printed: the PR is the one fact
    about a red repo the ledger records, so it comes from the system of record.
    """
    return _pr_field(repo, branch, state="open", field="url")


def pr_state(repo: Path, branch: str) -> str | None:
    """``OPEN``, ``MERGED`` or ``CLOSED`` for the newest PR whose head is ``branch``; None for no PR."""
    return _pr_field(repo, branch, state="all", field="state")


def _pr_field(repo: Path, branch: str, *, state: str, field: str) -> str | None:
    try:
        result = subprocess.run(
            [
                *GH,
                "pr",
                "list",
                "--head",
                branch,
                "--state",
                state,
                "--json",
                field,
                "--jq",
                f".[0].{field} // empty",
            ],
            cwd=repo,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as err:
        raise ToolError(f"{GH[0]} not found on PATH") from err
    if result.returncode != 0:
        raise ToolError(f"gh pr list --head {branch} failed: {result.stderr.strip()}")
    value = result.stdout.strip()
    return value or None
