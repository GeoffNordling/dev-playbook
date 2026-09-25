"""The command's surface: every argument required, and exit 2 when it cannot run."""

import pytest

from dev_playbook.errors import ToolError
from dev_playbook.stint import cli

RUN = [
    "run",
    "repo",
    "--base",
    "main",
    "--workstream",
    "ws",
    "--check",
    "true",
    "--budget",
    "4",
    "--name",
    "s1",
    "--home",
    "h",
    "--playbook",
    "p",
    "--model",
    "m",
]


@pytest.mark.parametrize("dropped", [a for a in RUN if a.startswith("--")])
def test_every_run_option_is_required(dropped: str) -> None:
    at = RUN.index(dropped)
    with pytest.raises(SystemExit) as exit_:
        cli.parser().parse_args(RUN[:at] + RUN[at + 2 :])
    assert exit_.value.code == 2


def test_a_run_before_setup_exits_2(monkeypatch: pytest.MonkeyPatch) -> None:
    def not_set_up() -> None:
        raise ToolError("the image is not built; run stint setup")

    monkeypatch.setattr(cli.install, "check_installed", not_set_up)
    assert cli.main(RUN) == 2
