"""Behavioral test for scripts/headless-probe.

The probe runs the billing guard, then asserts over state the harness declares
about a set of real `claude -p` invocations. Exit 0 means every probe passed;
1 means one failed; 2 means the guard tripped or `claude` is not on PATH. This
test is the standing check that headless operation still holds, so it makes
real inference calls against subscription usage.
"""

import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "headless-probe"


def test_headless_probe_passes() -> None:
    result = subprocess.run(
        ["uv", "run", "--script", str(SCRIPT)],
        capture_output=True,
        text=True,
        timeout=420,
    )
    assert result.returncode == 0, result.stdout + result.stderr
