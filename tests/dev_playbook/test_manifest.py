"""The published manifest, .pre-commit-hooks.yaml, holds one hook.

The decision record docs/decisions/0012-one-published-hook.md asks for
this: a consumer enrolls in every check by pinning one id, and a check
added upstream reaches it at the next pin bump without a config edit.
"""

import yaml
from conftest import REPO_ROOT

MANIFEST = REPO_ROOT / ".pre-commit-hooks.yaml"


def test_one_published_hook_runs_the_console_script() -> None:
    hooks = yaml.safe_load(MANIFEST.read_text())
    assert [h["id"] for h in hooks] == ["playbook-check"]
    assert hooks[0]["entry"] == "playbook check"
    assert hooks[0]["language"] == "python"
