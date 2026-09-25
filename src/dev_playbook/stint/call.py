"""One sealed call: one agent session in a new container on the work copy.

    host, this module                    sandcastle/run.mjs, Node
    billing guard
    credential copy, receiver   ──▶  request  ──▶  run(): the setup, pre-commit install
                                                    run(): the agent
                                                    run(): the probe, git status
    stream parsed, record kept  ◀──  response ◀──
    receiver stopped, temp folder deleted

The stint's run of the target check is a job of its own, ``Sealed.check``:
the command in place of the setup and the agent, then the probe. It spends no
tokens, so it gets no credential and no receiver.

Node does only what needs Sandcastle. Everything around it is here: what
the container mounts, what it is billed to, and what the call left behind.
The container sees three read-only files beside the work copy: the config
copy of dev-playbook, a copy of the subscription credential, and the sink
file that names the hook receiver; and, read-only, each sibling copy
(``config.py``). It also mounts the stint's cache folder
read-write as its ``~/.cache``, so the gate's environments are built once
per stint, not once per call.

The setup installs the repository's pre-commit hooks in the work copy, inside
the container, so an agent's commit runs the gate. It runs there, not on the
host, because the hook it writes names the interpreter that installed it.

Each call leaves in ``<folder>/calls/``: ``<name>.request.json``, what Node
was asked; ``<name>.log``, ``<name>-setup.log``, and ``<name>-probe.log``,
Sandcastle's logs; and ``<name>.json``, the CallRecord.
"""

import json
import os
import shutil
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

from dev_playbook.checks.billing import (
    CREDENTIAL_SETTINGS_KEYS,
    SETTINGS_FILES,
    CannotRead,
    metered_env_vars,
    read_settings,
    settings_env_vars,
)
from dev_playbook.stint import workcopy
from dev_playbook.stint.receiver import NETWORK, Receiver, ReceiverFault
from dev_playbook.stint.records import CallRecord, CheckRecord, Usage

AGENT_HOME = "/home/agent"
WORKSPACE = f"{AGENT_HOME}/workspace"
CONFIG_MOUNT = f"{WORKSPACE}/dev-playbook"
CREDENTIALS_MOUNT = f"{AGENT_HOME}/.claude/.credentials.json"
SINK_MOUNT = f"{AGENT_HOME}/.local/share/claude-measure/sink"
CACHE_MOUNT = f"{AGENT_HOME}/.cache"
"""Where pre-commit, uv, and npm keep their downloads; the stint's cache folder."""
CACHE = "cache"
"""The stint's cache folder, in its folder: every call mounts it read-write.

It is the stint's own, never the host's ``~/.cache``, and never another
stint's: an agent can write it, so sharing it would let one stint's agent
change the hook environments of the next. Deleted when the stint ends.
"""
AGENT_ENV = {"CLAUDE_CODE_TMPDIR": "/tmp/agent-tmp"}
"""Claude's temp folder moves off ``/tmp/claude-<uid>``, which a mount can make root-owned."""

Runner = Callable[[dict], dict]
"""Hand a request to Sandcastle and return its response."""


class CallFault(Exception):
    """The call could not be made, or its result cannot be trusted."""


class BillingFault(CallFault):
    """The call would go, or went, to something other than the subscription."""


def container_repo(copy: Path) -> str:
    """Where the work copy sits inside the container."""
    return f"{AGENT_HOME}/assignment/{copy.name}"


def billing_guard(config: Path, copy: Path) -> None:
    """Refuse a call that anything it hands in would route to metered billing.

    Checked: the host environment Node runs in; the config copy's
    ``settings.json``, which becomes the container's user settings; the work
    copy's ``.claude/`` settings, which are the project's; and the work copy's
    ``.sandcastle/.env``, whose names Sandcastle fills from the host
    environment and passes into the container.
    """
    problems = [f"{name} is set on the host" for name in metered_env_vars(os.environ)]
    sources = [
        (
            "the config copy's settings.json",
            config / "dotfiles" / "dot-claude" / "settings.json",
        )
    ]
    try:
        found = [(label, read_settings(path)) for label, path in sources]
        for name in SETTINGS_FILES:
            rel = f".claude/{name}"
            if os.path.lexists(copy / rel):
                found.append(
                    (
                        f"the work copy's {rel}",
                        json.loads(workcopy.read_plain(copy, rel)),
                    )
                )
    except (CannotRead, workcopy.CopyFault, ValueError) as err:
        raise BillingFault(f"cannot read a settings file: {err}") from err
    for label, settings in found:
        if not isinstance(settings, dict):
            raise BillingFault(f"{label} does not hold a JSON object")
        problems += [
            f"{label} has {key}" for key in CREDENTIAL_SETTINGS_KEYS if key in settings
        ]
        problems += [f"{label} sets {var}" for var in settings_env_vars(settings)]
    if os.path.lexists(copy / ".sandcastle" / ".env"):
        problems.append("the work copy has .sandcastle/.env")
    if problems:
        raise BillingFault("would route to metered billing: " + "; ".join(problems))


def read_stream(lines: list[str]) -> tuple[str, str, bool]:
    """The billing source, the final answer, and whether the call ended in error.

    Read from Claude's raw stream: the ``system``/``init`` line and the
    ``result`` line. A stream with no result line ended in error.
    """
    messages = []
    for line in lines:
        try:
            messages.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    messages = [m for m in messages if isinstance(m, dict)]
    init = next(
        (
            m
            for m in messages
            if m.get("type") == "system" and m.get("subtype") == "init"
        ),
        None,
    )
    if init is None or "apiKeySource" not in init:
        raise BillingFault(
            "the stream has no init line, so the billing source is unknown"
        )
    result = next((m for m in messages if m.get("type") == "result"), None)
    if result is None:
        return init["apiKeySource"], "", True
    return init["apiKeySource"], result.get("result", ""), bool(result.get("is_error"))


def usage_of(reported: dict | None) -> Usage | None:
    """Sandcastle's usage, which names its fields in camel case, as a Usage."""
    if reported is None:
        return None
    return Usage(
        input_tokens=reported["inputTokens"],
        cache_creation_input_tokens=reported["cacheCreationInputTokens"],
        cache_read_input_tokens=reported["cacheReadInputTokens"],
        output_tokens=reported["outputTokens"],
    )


def uncommitted(probe: list[str]) -> list[str]:
    """The probe's git short status lines, without the blank ones."""
    return [line for line in probe if len(line) > 3 and line[2] == " "]


def run_node(request: dict) -> dict:
    """Run ``sandcastle/run.mjs`` on the request and return its response."""
    script = resources.files("dev_playbook.stint").joinpath("sandcastle", "run.mjs")
    done = subprocess.run(
        ["node", str(script)],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        check=False,
    )
    if done.returncode:
        raise CallFault(f"run.mjs exited {done.returncode}: {done.stderr[-2000:]}")
    lines = done.stdout.strip().splitlines()
    if not lines:
        raise CallFault("run.mjs printed no response")
    response: dict = json.loads(lines[-1])
    return response


@dataclass(frozen=True)
class Sealed:
    """Makes the stint's calls, each in a new container on the same work copy."""

    config: Path
    """The config copy: dev-playbook, mounted read-only."""
    siblings: tuple[Path, ...]
    """The sibling copies, each mounted read-only at ``~/workspace/<name>``."""
    copy: Path
    """The work copy."""
    folder: Path
    """The stint's folder, which keeps the records and the session files."""
    model: str
    image: str
    """The container image, built by ``stint setup``."""
    credentials: Path
    """The host's subscription credential, copied for each call."""
    events: Path
    """The measurement store the hook rows go into."""
    runner: Runner
    """Hands a request to Sandcastle; ``run_node`` except in a test."""

    def request(self, job: str, name: str, *mounts: dict) -> dict:
        """The fields every job's request holds; ``mounts`` go after the config copy's."""
        calls = self.folder / "calls"
        calls.mkdir(parents=True, exist_ok=True)
        cache = self.folder / CACHE
        cache.mkdir(exist_ok=True)
        return {
            "job": job,
            "copy": str(self.copy),
            "repo": container_repo(self.copy),
            "image": self.image,
            "network": NETWORK,
            "mounts": [
                {
                    "hostPath": str(self.config),
                    "sandboxPath": CONFIG_MOUNT,
                    "readonly": True,
                },
                *mounts,
                *[
                    {
                        "hostPath": str(sibling),
                        "sandboxPath": f"{WORKSPACE}/{sibling.name}",
                        "readonly": True,
                    }
                    for sibling in self.siblings
                ],
                {
                    "hostPath": str(cache),
                    "sandboxPath": CACHE_MOUNT,
                    "readonly": False,
                },
            ],
            "log": str(calls / f"{name}.log"),
            "probeLog": str(calls / f"{name}-probe.log"),
        }

    def keep(self, name: str, request: dict) -> None:
        """Write what the job asks Sandcastle to ``calls/<name>.request.json``."""
        (self.folder / "calls" / f"{name}.request.json").write_text(
            json.dumps(request, indent=2) + "\n", encoding="utf-8"
        )

    def check(self, name: str, command: str) -> CheckRecord:
        """Run the target check; a fault in the run raises CallFault.

        The check is a shell command, not an agent, so it has no credential,
        no hook receiver, and no billing to guard.
        """
        request = {**self.request("check", name), "command": command}
        self.keep(name, request)
        started = time.monotonic()
        response = self.runner(request)
        record = CheckRecord(
            name=name,
            seconds=round(time.monotonic() - started),
            exit=response["exit"],
            output=response["output"],
            uncommitted=uncommitted(response["probe"]),
        )
        record.write(self.folder / "calls")
        return record

    def __call__(self, name: str, prompt: str, resume: str | None) -> CallRecord:
        """Make one call; a fault in it raises CallFault after the record is kept."""
        billing_guard(self.config, self.copy)
        temp = self.folder / f"tmp-{name}"
        temp.mkdir(parents=True)
        try:
            shutil.copyfile(self.credentials, temp / ".credentials.json")
            request = self.request(
                "agent",
                name,
                {
                    "hostPath": str(temp / ".credentials.json"),
                    "sandboxPath": CREDENTIALS_MOUNT,
                    "readonly": True,
                },
                {
                    "hostPath": str(temp / "sink"),
                    "sandboxPath": SINK_MOUNT,
                    "readonly": True,
                },
            )
            calls = self.folder / "calls"
            request |= {
                "env": AGENT_ENV,
                "sessions": str(self.folder / "sessions"),
                "setupLog": str(calls / f"{name}-setup.log"),
                "model": self.model,
                "prompt": prompt,
                "resume": resume,
            }
            self.keep(name, request)
            receiver = Receiver(temp / "sink", self.events)
            started = time.monotonic()
            try:
                response = self.runner(request)
            finally:
                try:
                    receiver.stop()
                except ReceiverFault as err:
                    raise CallFault(str(err)) from err
            seconds = round(time.monotonic() - started)
        finally:
            shutil.rmtree(temp)
        source, answer, is_error = read_stream(response["raw"])
        record = CallRecord(
            name=name,
            session=response["session"],
            resumed=resume,
            api_key_source=source,
            seconds=seconds,
            is_error=is_error,
            usage=usage_of(response["usage"]),
            commits=response["commits"],
            uncommitted=uncommitted(response["probe"]),
            answer=answer,
        )
        record.write(self.folder / "calls")
        if source != "none":
            raise BillingFault(f"billed to {source}, not the subscription")
        return record
