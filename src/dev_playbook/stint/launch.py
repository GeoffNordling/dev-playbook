"""One stint from launch to the end: both copies opened, the loop, both closed.

The stint's folder is ``<home>/<repo>/<name>/``, made fresh. At launch it
gets two copies: the work copy, ``<repo>/``, holding the new branch
``<name>`` at the base; and the config copy, ``config/``. At the end the work
copy is closed, which brings the branch into the repository and deletes the
copy, and the config copy is deleted. A work copy that cannot close, such as
one holding uncommitted work, is kept, and the record says so. The records
stay in the folder; ``records.py`` lists them.
"""

import shutil
import time
from dataclasses import dataclass
from pathlib import Path

from dev_playbook.errors import ToolError
from dev_playbook.stint import workcopy
from dev_playbook.stint.call import Runner, Sealed, container_repo
from dev_playbook.stint.config import make_config
from dev_playbook.stint.loop import Assignment, Loop, Stop
from dev_playbook.stint.records import StintRecord


@dataclass(frozen=True)
class Order:
    """What the launching agent asks for: the command's arguments, all required."""

    repo: Path
    """The repository the stint changes."""
    base: str
    """The ref the stint's branch starts at; it holds the workstream."""
    workstream: str
    """The workstream folder in the repository, with its plan and progress log."""
    check: str
    """The command that must pass after every change."""
    budget: int
    """The most iterations the stint may spend."""
    name: str
    """The stint's name, and its branch's."""
    home: Path
    """Where stint folders live."""
    playbook: Path
    """The dev-playbook checkout whose ``main`` the config copy is cloned from."""
    model: str
    """The Claude model every call runs."""


@dataclass(frozen=True)
class Host:
    """What the machine provides; a test passes a fake runner and store."""

    image: str
    credentials: Path
    events: Path
    patches: list[Path]
    runner: Runner


def launch(order: Order, host: Host) -> StintRecord:
    """Run one stint and return its record, also written to ``stint.json``.

    A reason other than ``done`` is a stop. Anything else that goes wrong is
    raised after both copies are closed and the record is written.
    """
    repo = order.repo.resolve()
    if not workcopy.is_checkout(repo):
        raise ToolError(f"{repo} is not a git checkout")
    folder = (order.home / repo.name / order.name).resolve()
    if folder.exists():
        raise ToolError(f"{folder} already exists; a stint's folder is made fresh")
    copy, config = folder / repo.name, folder / "config"
    (folder / "calls").mkdir(parents=True)
    record = StintRecord(reason="", budget=order.budget)
    started = time.monotonic()
    print(f"stint {order.name}: {folder}", flush=True)
    try:
        try:
            make_config(order.playbook, config, host.patches)
            workcopy.open_copy(repo, copy, order.name, order.base)
            work = Assignment(
                copy=copy,
                repo=container_repo(copy),
                workstream=order.workstream,
                check=order.check,
                budget=order.budget,
            )
            sealed = Sealed(
                config=config,
                copy=copy,
                folder=folder,
                model=order.model,
                image=host.image,
                credentials=host.credentials,
                events=host.events,
                runner=host.runner,
            )
            Loop(work, sealed, record, folder).run()
            record.reason = "done"
        except Stop as stop:
            record.reason = str(stop)
        except BaseException as err:
            record.reason = f"the tool failed: {err}"
            raise
        finally:
            record.closed = close(copy, config)
    finally:
        record.minutes = round((time.monotonic() - started) / 60, 1)
        record.write(folder)
        print(summary(record, copy), flush=True)
    return record


def close(copy: Path, config: Path) -> bool:
    """Close the work copy and delete the config copy; whether the copy closed."""
    closed = True
    if copy.exists():
        try:
            workcopy.close_copy(copy)
        except workcopy.CopyFault as err:
            print(f"the work copy is kept: {err}", flush=True)
            closed = False
    if config.exists():
        shutil.rmtree(config)
    return closed


def summary(record: StintRecord, copy: Path) -> str:
    """The stint's last line on screen."""
    context = record.principal_context
    final = f"{context[-1].tokens:,}" if context else "none"
    line = (
        f"end: {record.reason} ({record.spent}/{record.budget} iterations,"
        f" {len(record.calls)} calls, {len(record.notes)} notes,"
        f" principal context {final} tokens, {record.minutes} min)"
    )
    return line if record.closed else f"{line}\nthe work copy is kept: {copy}"
