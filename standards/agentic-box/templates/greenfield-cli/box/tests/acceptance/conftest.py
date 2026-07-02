import subprocess
import sys

import pytest


@pytest.fixture
def run_cli(tmp_path):
    def _run(*args):
        return subprocess.run(
            [sys.executable, "-m", "sessionxml", *args],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

    return _run
