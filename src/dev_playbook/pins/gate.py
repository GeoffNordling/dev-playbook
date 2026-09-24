"""The consumer's commit gate, run to a verdict or a refusal.

The gate is ``uvx pre-commit run --all-files``, verbatim as the canonical
Makefile's ``check`` target spells it. It is the surface the pin controls:
every dev-playbook check reaches a consumer through pre-commit and nothing
else. The repo's own mypy/pytest targets are unaffected by the pin and are
left to ``make check``.
"""

import subprocess
from pathlib import Path

from dev_playbook.errors import ToolError

GATE = ("uvx", "pre-commit", "run", "--all-files")

# A cold `uvx` download plus a fresh clone of the new rev plus every hook over
# every file. Generous, because expiry here is a hang, not a slow repo.
GATE_TIMEOUT = 900

# pre-commit's own exit codes: 0 clean, 1 a hook reported findings, 3 an
# internal error, 130 interrupted. Only 0 and 1 are verdicts about the repo.
# Anything else — and either banner pre-commit's error handler prints, which
# covers the internal error it reports as 1 — means the gate never ran, which
# must never be reported as findings.
GATE_VERDICT_CODES = frozenset({0, 1})
GATE_ERROR_BANNERS = ("An error has occurred:", "An unexpected error has occurred:")


def run_gate(repo: Path) -> tuple[bool, str]:
    """The commit gate's (passed, combined output) for one repo.

    Only a run that reached a verdict returns. A missing runner, a timeout, and
    a pre-commit that died before judging the repo all raise instead, because
    "the gate could not run" and "the gate found something" are different facts
    and reporting the first as the second names a repo for a problem it does not
    have. The run at a *new* pin is the one most likely to hit this: it is where
    pre-commit clones the rev, so it is the only step that needs the network.
    """
    try:
        result = subprocess.run(
            GATE,
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=GATE_TIMEOUT,
        )
    except FileNotFoundError as err:
        raise ToolError(f"{GATE[0]} not found on PATH") from err
    except subprocess.TimeoutExpired as err:
        raise ToolError(
            f"the gate did not finish in {GATE_TIMEOUT}s in {repo}"
        ) from err
    output = result.stdout + result.stderr
    died = result.returncode not in GATE_VERDICT_CODES or any(
        banner in output for banner in GATE_ERROR_BANNERS
    )
    if died:
        raise ToolError(
            f"the gate could not run in {repo} — pre-commit exited "
            f"{result.returncode} without judging it:\n{output}"
        )
    return result.returncode == 0, output
