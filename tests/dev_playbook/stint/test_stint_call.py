"""One sealed call around a fake Sandcastle: the guard, the receiver, the record.

The fake runner plays Node's part: it reads the request, sends a hook row
through the sink file as a container's hook would, and answers with a
stream. No container and no tokens.
"""

import json
import os
import socket
import sqlite3
from pathlib import Path

import pytest

from dev_playbook.checks.billing import BILLING_ENV_VARS
from dev_playbook.stint.call import (
    BillingFault,
    CallFault,
    Runner,
    Sealed,
    billing_guard,
    read_stream,
)
from dev_playbook.stint.receiver import Receiver, ReceiverFault

INIT = json.dumps({"type": "system", "subtype": "init", "apiKeySource": "none"})
RESULT = json.dumps({"type": "result", "result": "the answer", "is_error": False})
USAGE = {
    "inputTokens": 2,
    "cacheCreationInputTokens": 300,
    "cacheReadInputTokens": 10000,
    "outputTokens": 100,
}


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in BILLING_ENV_VARS:
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def events(tmp_path: Path) -> Path:
    db = tmp_path / "events.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE events (received_at, event, session_id, prompt_id, payload)"
        )
    return db


def send(sink: Path, row: object) -> None:
    """Send one row as the container's hook does, to the port the sink names."""
    port = int(sink.read_text().split()[1])
    with socket.create_connection(("127.0.0.1", port)) as conn:
        conn.sendall(json.dumps(row).encode())


def stored(db: Path) -> int:
    with sqlite3.connect(db) as conn:
        count: int = conn.execute("SELECT count(*) FROM events").fetchone()[0]
        return count


def test_the_receiver_stores_each_row(tmp_path: Path, events: Path) -> None:
    receiver = Receiver(tmp_path / "sink", events)
    assert (tmp_path / "sink").read_text().startswith("169.254.1.2 ")
    send(tmp_path / "sink", ["t", "Stop", "s", "p", "{}"])
    assert receiver.stop() == 1
    assert stored(events) == 1


def test_the_receiver_fails_loud_on_a_lost_row(tmp_path: Path, events: Path) -> None:
    receiver = Receiver(tmp_path / "sink", events)
    send(tmp_path / "sink", ["too few columns"])
    with pytest.raises(ReceiverFault, match="1 hook rows lost"):
        receiver.stop()


@pytest.fixture
def config(tmp_path: Path) -> Path:
    config = tmp_path / "config"
    (config / "dotfiles" / "dot-claude").mkdir(parents=True)
    (config / "dotfiles" / "dot-claude" / "settings.json").write_text("{}")
    return config


@pytest.fixture
def copy(tmp_path: Path) -> Path:
    copy = tmp_path / "mc"
    copy.mkdir()
    return copy


def test_the_guard_passes_a_clean_call(config: Path, copy: Path) -> None:
    billing_guard(config, copy)


def test_the_guard_refuses_a_host_variable(
    config: Path, copy: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-x")
    with pytest.raises(BillingFault, match="ANTHROPIC_API_KEY is set on the host"):
        billing_guard(config, copy)


def test_the_guard_refuses_a_credential_in_the_config(config: Path, copy: Path) -> None:
    settings = config / "dotfiles" / "dot-claude" / "settings.json"
    settings.write_text(json.dumps({"apiKeyHelper": "x"}))
    with pytest.raises(
        BillingFault, match="config copy's settings.json has apiKeyHelper"
    ):
        billing_guard(config, copy)


def test_the_guard_refuses_a_variable_in_the_copys_settings(
    config: Path, copy: Path
) -> None:
    (copy / ".claude").mkdir()
    (copy / ".claude" / "settings.local.json").write_text(
        json.dumps({"env": {"ANTHROPIC_BASE_URL": "http://x"}})
    )
    with pytest.raises(BillingFault, match="sets ANTHROPIC_BASE_URL"):
        billing_guard(config, copy)


def test_the_guard_refuses_a_linked_settings_file(
    config: Path, copy: Path, tmp_path: Path
) -> None:
    (tmp_path / "host.json").write_text("{}")
    (copy / ".claude").mkdir()
    os.symlink(tmp_path / "host.json", copy / ".claude" / "settings.json")
    with pytest.raises(BillingFault, match="symlink in the copy"):
        billing_guard(config, copy)


def test_the_guard_refuses_a_sandcastle_env_file(config: Path, copy: Path) -> None:
    (copy / ".sandcastle").mkdir()
    (copy / ".sandcastle" / ".env").write_text("ANTHROPIC_API_KEY=\n")
    with pytest.raises(BillingFault, match=r"\.sandcastle/\.env"):
        billing_guard(config, copy)


def test_the_stream_gives_source_answer_and_error() -> None:
    assert read_stream(["not json", INIT, RESULT]) == ("none", "the answer", False)


def test_a_stream_with_no_result_ended_in_error() -> None:
    assert read_stream([INIT]) == ("none", "", True)


def test_a_stream_with_no_init_line_is_refused() -> None:
    with pytest.raises(BillingFault, match="billing source is unknown"):
        read_stream([RESULT])


def fake_node(source: str = "none") -> tuple[list[dict], Runner]:
    """A runner that checks what the container would mount, then answers."""
    seen: list[dict] = []

    def runner(request: dict) -> dict:
        seen.append(request)
        mounts = {m["sandboxPath"]: Path(m["hostPath"]) for m in request["mounts"]}
        writable = [m["sandboxPath"] for m in request["mounts"] if not m["readonly"]]
        assert writable == ["/home/agent/.cache"]
        assert mounts["/home/agent/.cache"].is_dir()
        assert mounts["/home/agent/workspace/alpha"].name == "alpha"
        credentials = mounts["/home/agent/.claude/.credentials.json"]
        assert credentials.read_text() == "secret"
        send(
            mounts["/home/agent/.local/share/claude-measure/sink"],
            ["t", "e", "s", "p", "{}"],
        )
        init = json.dumps({"type": "system", "subtype": "init", "apiKeySource": source})
        return {
            "session": "s1",
            "usage": USAGE,
            "commits": ["abc"],
            "raw": [init, RESULT],
            "probe": [" M a.txt", "?? b.txt", ""],
        }

    return seen, runner


def sealed(
    tmp_path: Path, config: Path, copy: Path, events: Path, runner: Runner
) -> Sealed:
    (tmp_path / "credentials.json").write_text("secret")
    sibling = tmp_path / "siblings" / "alpha"
    sibling.mkdir(parents=True, exist_ok=True)
    return Sealed(
        config=config,
        siblings=(sibling,),
        copy=copy,
        folder=tmp_path / "stint",
        model="m",
        image="i",
        credentials=tmp_path / "credentials.json",
        events=events,
        runner=runner,
    )


def test_a_call_keeps_its_record_and_deletes_its_temp_folder(
    tmp_path: Path, config: Path, copy: Path, events: Path
) -> None:
    seen, runner = fake_node()
    rec = sealed(tmp_path, config, copy, events, runner)("iter-1", "do it", None)
    assert rec.answer == "the answer"
    assert rec.usage is not None and rec.usage.context == 10402
    assert rec.uncommitted == [" M a.txt", "?? b.txt"]
    assert seen[0]["repo"] == "/home/agent/assignment/mc"
    folder = tmp_path / "stint"
    assert json.loads((folder / "calls" / "iter-1.json").read_text())["session"] == "s1"
    assert (folder / "calls" / "iter-1.request.json").is_file()
    assert not (folder / "tmp-iter-1").exists()
    assert stored(events) == 1


def test_a_billed_call_is_kept_and_refused(
    tmp_path: Path, config: Path, copy: Path, events: Path
) -> None:
    _, runner = fake_node("ANTHROPIC_API_KEY")
    with pytest.raises(BillingFault, match="billed to ANTHROPIC_API_KEY"):
        sealed(tmp_path, config, copy, events, runner)("iter-1", "do it", None)
    assert (tmp_path / "stint" / "calls" / "iter-1.json").is_file()


def test_a_failed_runner_still_deletes_the_temp_folder(
    tmp_path: Path, config: Path, copy: Path, events: Path
) -> None:
    def runner(request: dict) -> dict:
        raise CallFault("run.mjs exited 1")

    with pytest.raises(CallFault, match="exited 1"):
        sealed(tmp_path, config, copy, events, runner)("iter-1", "do it", None)
    assert not (tmp_path / "stint" / "tmp-iter-1").exists()
