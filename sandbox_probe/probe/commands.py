"""One function per probe command.

Each is a handful of lines over the helpers in podman.py, so what a command
does is visible without reading anything else.
"""

import contextlib
import json
import shutil
import signal
import socket
import sqlite3
import tempfile
import threading
import time
from datetime import UTC, datetime
from pathlib import Path

from probe import billing, podman, sink, stream

HOME = "/home/geoff"

# The throwaway clone lives here. .gitignore keeps it out of the repo. Nothing
# is handed from one run to the next; this exists only so the host can look at
# what a run left behind.
SCRATCH = podman.PROBE_DIR / "scratch"

# The subscription login. The copy is what gets mounted: :Z retags whatever it
# is pointed at, and this is the credential your own Claude session uses.
CREDENTIALS_ON_HOST = Path.home() / ".claude/.credentials.json"
CREDENTIALS_INSIDE = f"{HOME}/.claude/.credentials.json"

# A Containerfile can only COPY files from the build context, so the binary
# has to be staged there first. .gitignore keeps it out of the repo.
CLAUDE_ON_HOST = Path.home() / ".local/bin/claude"
CLAUDE_IN_CONTEXT = podman.REPO_ROOT / "claude"

# Everything the agent is handed is handed deliberately, so anything found at
# one of these paths got in by accident.
FORBIDDEN = (
    f"{HOME}/.config/gh",  # the GitHub token
    f"{HOME}/.ssh",  # ssh keys
    f"{HOME}/.aws",  # cloud credentials
    f"{HOME}/.local/share/claude",  # the host's Claude install and history
)

# Report every reachable path rather than stopping at the first, then exit
# non-zero if there were any. run() raises on a non-zero exit.
FENCE_SCRIPT = f"""
found=""
for path in {" ".join(FORBIDDEN)}; do
    if [ -e "$path" ]; then
        echo "REACHABLE: $path"
        found=yes
    fi
done
echo "--- contents of {HOME} ---"
ls -A {HOME}
echo "--- end ---"
[ -z "$found" ]
"""


def build_image() -> None:
    """Stage the claude binary, then build the sandbox image."""
    # copy follows the symlink, so this is the real 214 MB program.
    shutil.copy(CLAUDE_ON_HOST, CLAUDE_IN_CONTEXT)
    print(f"staged {CLAUDE_ON_HOST.resolve()}")
    podman.build_image()


# sync-dotfiles refuses to run without the first four; uv is what launches it.
REQUIRED_TOOLS = ("git", "stow", "jq", "python3", "uv")


def check_tools() -> None:
    """Show that every tool sync-dotfiles needs is installed in the image."""
    versions = "; ".join(f"{tool} --version" for tool in REQUIRED_TOOLS)
    podman.run(
        podman.container_argv(
            mounts=[],
            env={},
            command=["sh", "-c", versions],
        )
    )


def check_claude() -> None:
    """Show that the host-compiled claude binary runs inside the image."""
    podman.run(
        podman.container_argv(
            mounts=[],
            env={"HOME": HOME},
            command=["claude", "--version"],
        )
    )


@contextlib.contextmanager
def credential_copy():
    """The login copied into a temporary directory, as a mount of the copy.

    The temporary directory is deleted on the way out, so the copy exists only
    while the container is running.
    """
    with tempfile.TemporaryDirectory() as scratch:
        copy = Path(scratch) / ".credentials.json"
        shutil.copy(CREDENTIALS_ON_HOST, copy)
        yield podman.Mount(copy, Path(CREDENTIALS_INSIDE))


def ask_claude(prompt: str, *, skip_permissions: bool = False) -> list[str]:
    """The command line for one headless question, answered as JSON lines.

    skip_permissions turns off the approval prompt for every tool. A headless
    run has nobody to ask, so without it every edit is refused and the agent
    reports it could not do the job.

    It is safe here for one reason: the container is the fence. The approval
    prompt asks the agent to police itself; the mount list does not.
    """
    argv = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose"]
    if skip_permissions:
        argv.append("--dangerously-skip-permissions")
    return argv


def check_billing() -> None:
    """Ask Claude one trivial question and report which account paid for it."""
    env = {"HOME": HOME}
    # No repo is mounted, so the baked settings.json symlink dangles and there
    # is no settings file to read. check-config is where that changes.
    billing.refuse_if_metered(env, {})

    with credential_copy() as credential:
        finished = podman.run(
            podman.container_argv(
                mounts=[credential],
                env=env,
                command=ask_claude("Reply with the single word: hi"),
            ),
            capture=True,
        )

    init = stream.parse_init(finished.stdout)
    print(f"apiKeySource: {init.api_key_source!r}   model: {init.model}")
    if not stream.billed_subscription(init):
        raise billing.MeteredBilling(
            f"the run billed {init.api_key_source!r}, not the subscription"
        )
    print("billed the subscription")


REPO_ON_HOST = Path.home() / "workspace/dev-playbook"
REPO_INSIDE = f"{HOME}/workspace/dev-playbook"

CLONE = SCRATCH / "dev-playbook"


def repo_mounts(*, writable_repo: bool = False) -> list[podman.Mount]:
    """The clone, at the path the baked symlinks point into.

    The home directory is not mounted. The image already carries
    /home/geoff/.claude, built by sync-dotfiles at build time, and those
    symlinks aim at REPO_INSIDE — so this one mount is what makes them resolve.

    Nothing of the host is mounted at /home/geoff, which is why a directory
    podman creates for a missing mountpoint stays inside the container instead
    of appearing on your disk owned by a user that does not exist out here.

    The clone is read-only by default, so a command has to say it lets the
    agent write. run-task is the only one that does.
    """
    return [podman.Mount(CLONE, Path(REPO_INSIDE), writable=writable_repo)]


def clone_repo() -> Path:
    """A fresh throwaway clone of dev-playbook, replacing any previous one.

    --no-hardlinks matters. Cloning a directory on the same machine normally
    shares the file contents rather than copying them, and the :Z retag would
    then reach the real repo through the sharing.
    """
    shutil.rmtree(CLONE, ignore_errors=True)
    podman.run(["git", "clone", "--no-hardlinks", str(REPO_ON_HOST), str(CLONE)])
    return CLONE


def clone_settings() -> dict:
    """The settings file a run reads, reached from outside the container.

    /home/geoff/.claude/settings.json in the image is a symlink into the repo,
    so the file behind it is the one in whichever clone is mounted.
    """
    return billing.read_settings(CLONE / "dotfiles/dot-claude/settings.json")


def check_config() -> None:
    """Show that Claude inside picked up the config baked into the image."""
    clone_repo()
    env = {"HOME": HOME}
    billing.refuse_if_metered(env, clone_settings())

    with credential_copy() as credential:
        finished = podman.run(
            podman.container_argv(
                mounts=repo_mounts() + [credential],
                env=env,
                command=ask_claude("Reply with the single word: hi"),
            ),
            capture=True,
        )

    init = stream.parse_init(finished.stdout)
    print(f"agents ({len(init.agents)}): {', '.join(init.agents)}")
    print(f"skills ({len(init.skills)}): {', '.join(init.skills)}")


# The longest a task may run, in seconds. Deliberately past anything a real
# task would reach: its job is to end a container that survived a SIGKILL, not
# to discipline slow work. A cap on how long work may take is a different
# decision, and should say why it stopped rather than kill silently.
TASK_TIMEOUT = 4 * 60 * 60

# A job that needs both halves of the repo mount: read a file, then write one.
TASK = (
    "Read README.md and write a one-paragraph summary of what this repository "
    "is for to NOTES.md in the repository root. Do not commit."
)


def run_task(prompt: str = TASK) -> None:
    """Give the agent a real job in the clone, and show what it changed.

    Measurement rides along: the run gets a receiver, the sink mount, and the
    loopback mapping, so the agent's own hooks write to this machine's store
    the way a host session's do. Nothing in the prompt asks for that — the
    events are the ones Claude raises on its own.
    """
    clone_repo()
    stage_working_hook()
    env = {"HOME": HOME}
    billing.refuse_if_metered(env, clone_settings())

    with credential_copy() as credential, sink.receiving() as (receiver, sink_mount):
        finished = podman.run(
            podman.container_argv(
                mounts=repo_mounts(writable_repo=True) + [credential, sink_mount],
                env=env,
                workdir=REPO_INSIDE,
                timeout=TASK_TIMEOUT,
                network=sink.NETWORK,
                command=ask_claude(prompt, skip_permissions=True),
            ),
            capture=True,
        )
    print(f"the receiver took {receiver.rows} rows from the run")

    show_session_rows(stream.parse_init(finished.stdout).session_id)

    result = stream.parse_result(finished.stdout)
    print(
        f"{result.subtype}, {result.num_turns} turns, {result.duration_ms / 1000:.0f}s"
    )
    print(result.text)
    if result.is_error:
        raise RuntimeError("the run reported an error; see the text above")

    show_changes()


def stage_working_hook() -> None:
    """Put the working tree's measure-event into the clone, over the cloned one.

    A clone carries committed state, so without this a run exercises whatever
    hook is on the branch it was cloned from rather than the one being edited.
    The clone is a throwaway, and this is the file the run's hooks execute:
    /home/geoff/.claude/hooks in the image is a symlink into the mount.
    """
    shutil.copy(MEASURE_HOOK, CLONE / "dotfiles/dot-claude/hooks/measure-event")


def show_session_rows(session_id: str) -> None:
    """What the run's own hooks put in the store, counted by kind of event."""
    with sqlite3.connect(sink.DB_PATH) as connection:
        rows = connection.execute(
            "SELECT min(id), max(id), event, count(*) FROM events"
            " WHERE session_id = ? GROUP BY event ORDER BY min(id)",
            (session_id,),
        ).fetchall()

    if not rows:
        raise RuntimeError(f"no row of session {session_id} reached {sink.DB_PATH}")
    print(f"session {session_id} in {sink.DB_PATH}:")
    for first, last, event, count in rows:
        print(f"  {event:18} {count:3}  ids {first}-{last}")


def show_changes() -> None:
    """What the agent left behind in the clone, and who owns it.

    Ownership is the point as much as the change is: --userns=keep-id is what
    makes a file written inside come back belonging to you rather than to a
    user that does not exist out here.
    """
    status = podman.run(
        ["git", "-C", str(CLONE), "status", "--short"], capture=True
    ).stdout
    if not status.strip():
        raise RuntimeError("the agent changed nothing in the clone")

    for line in status.splitlines():
        path = CLONE / line.split()[-1]
        print(f"{path.owner()}  {line}")


CLEANUP_CONTAINER = "sandbox-probe-cleanup"

# Short enough to watch expire during the check.
CLEANUP_TIMEOUT = 10


def wait_for(condition, *, seconds: float, description: str) -> None:
    """Poll until condition() is true, or fail saying what never happened."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if condition():
            return
        time.sleep(0.2)
    raise RuntimeError(f"waited {seconds}s for {description}, and it did not")


def kill_runner_with(sig: int) -> None:
    """Start a container that sleeps, wait for it to be up, and kill the runner."""
    podman.remove_container(CLEANUP_CONTAINER)
    runner = podman.start(
        podman.container_argv(
            mounts=[],
            env={},
            command=["sleep", "300"],
            name=CLEANUP_CONTAINER,
            timeout=CLEANUP_TIMEOUT,
        )
    )
    wait_for(
        lambda: podman.container_exists(CLEANUP_CONTAINER),
        seconds=30,
        description="the container to start",
    )
    runner.send_signal(sig)
    runner.wait()


def check_cleanup() -> None:
    """Show what a killed runner leaves behind, and that it does not last.

    A container that outlives its runner still holds every mount it was given,
    including the copy of your login. So this checks both ways a run ends
    early, because they do not behave the same.

    Ctrl-C is the everyday one, and podman handles it: the container goes.
    kill -9 is the one nothing can catch, so the container keeps running.
    --timeout is what ends it, enforced by podman rather than by the runner
    that is no longer alive to enforce anything.
    """
    kill_runner_with(signal.SIGINT)
    wait_for(
        lambda: not podman.container_exists(CLEANUP_CONTAINER),
        seconds=30,
        description="Ctrl-C to take the container with it",
    )
    print("SIGINT: gone with the runner")

    kill_runner_with(signal.SIGKILL)
    if not podman.container_exists(CLEANUP_CONTAINER):
        raise RuntimeError("kill -9 was expected to strand the container, and did not")
    print(f"SIGKILL: stranded, as expected. Waiting out --timeout={CLEANUP_TIMEOUT}s")

    wait_for(
        lambda: not podman.container_exists(CLEANUP_CONTAINER),
        seconds=CLEANUP_TIMEOUT + 30,
        description="--timeout to end the stranded container",
    )
    print("--timeout ended it. Nothing left behind either way")


def check_host_tcp() -> None:
    """Show that a program inside can send a message to a listener on the host.

    This is the fact the measurement fix rests on: the guarded-hole option died
    because SELinux forbids a container talking to a host program over a unix
    socket. Over TCP no such process-to-process check exists — the same policy
    path that lets Claude inside reach Anthropic. This proves it on this
    machine, through the real image, with the real run flags.

    The listener binds the host's 127.0.0.1 only. pasta maps sink.HOST_ALIAS
    inside the container to that loopback, so nothing is opened to the network.
    """
    listener = socket.create_server(("127.0.0.1", 0))
    port = listener.getsockname()[1]
    received: list[bytes] = []

    def accept_one() -> None:
        conn, _ = listener.accept()
        with conn:
            received.append(conn.recv(4096))

    waiter = threading.Thread(target=accept_one, daemon=True)
    waiter.start()

    message = "hello from the container"
    sender = (
        "import socket\n"
        f"s = socket.create_connection(('{sink.HOST_ALIAS}', {port}), timeout=10)\n"
        f"s.sendall({message!r}.encode())\n"
        "s.close()\n"
        "print('sent')\n"
    )
    podman.run(
        podman.container_argv(
            mounts=[],
            env={"HOME": HOME},
            network=sink.NETWORK,
            command=["python3", "-c", sender],
        )
    )

    waiter.join(timeout=10)
    listener.close()
    if not received or received[0].decode() != message:
        raise RuntimeError(f"the listener never got the message; got {received!r}")
    print(f"host listener on 127.0.0.1:{port} received: {received[0].decode()!r}")


# The hook under test, and where the run reads it from. The real image reaches
# it through a symlink into the mounted clone; this mounts the file itself, so
# the hook being rehearsed is the one in this working tree rather than whatever
# the clone happens to carry.
MEASURE_HOOK = podman.REPO_ROOT / "dotfiles/dot-claude/hooks/measure-event"
HOOK_INSIDE = f"{HOME}/measure-event"

# The session_id every rehearsal row carries, so the rows this check wrote can
# be told from a real session's afterwards.
SINK_SESSION = "sink-rehearsal"

# Feeds every payload to its own copy of the hook at once, the way an async
# hook fires. Payloads come in on argv, so nothing has to survive quoting.
HOOK_RUNNER = f"""
import subprocess, sys

running = []
for payload in sys.argv[1:]:
    hook = subprocess.Popen(["python3", "{HOOK_INSIDE}"], stdin=subprocess.PIPE)
    hook.stdin.write(payload.encode())
    hook.stdin.close()
    running.append(hook)

for hook in running:
    if hook.wait() != 0:
        raise SystemExit("a hook exited non-zero, which it is never allowed to do")
print("sent", len(running), "events")
"""


def sink_payloads() -> list[str]:
    """The events the rehearsal sends: the shapes that have broken things before.

    The large one is the point of TCP over a named pipe — 8.98% of live rows
    are past a pipe's 4096-byte atomic write. The non-Bash PostToolUse proves
    the trim still happens before the row leaves the container.
    """
    session = SINK_SESSION
    events = [
        {"hook_event_name": "SessionStart", "session_id": session},
        {
            "hook_event_name": "UserPromptSubmit",
            "session_id": session,
            "prompt_id": "p1",
        },
        {
            "hook_event_name": "PostToolUse",
            "session_id": session,
            "prompt_id": "p1",
            "tool_name": "Read",
            "tool_input": {"file_path": "/dev/null"},
            "tool_response": "dropped before storage",
        },
        {
            "hook_event_name": "PostToolUse",
            "session_id": session,
            "prompt_id": "p1",
            "tool_name": "Bash",
            "tool_response": "x" * 100_000,
        },
        {"hook_event_name": "Stop", "session_id": session},
    ]
    return [json.dumps(event) for event in events]


def check_measure_sink() -> None:
    """Show that a hook event raised inside the container lands in a host database.

    The whole measurement fix end to end: a receiver on the host, the one-line
    sink file mounted read-only where the hook looks for it, and the real
    measure-event hook run inside with an event on stdin. What proves it is a
    row on the host, written by a process the container never touched.

    The rows land in the real store, at the ID the arrival order gives them,
    which is the behaviour being checked. They stay there, marked as this
    check's by their session_id.
    """
    payloads = sink_payloads()

    with tempfile.TemporaryDirectory() as scratch:
        hook_copy = Path(scratch) / "measure-event"
        shutil.copy(MEASURE_HOOK, hook_copy)
        with sink.receiving() as (receiver, sink_mount):
            print(f"receiver listening on 127.0.0.1:{receiver.port}")
            podman.run(
                podman.container_argv(
                    mounts=[sink_mount, podman.Mount(hook_copy, Path(HOOK_INSIDE))],
                    env={"HOME": HOME},
                    network=sink.NETWORK,
                    command=["python3", "-c", HOOK_RUNNER, *payloads],
                )
            )

    show_sink_rows(len(payloads))


def show_sink_rows(expected: int) -> None:
    """Read this run's rows back out of the real store, and check them.

    Only this run's rows: the store holds every session this machine has ever
    had, so the check reads the newest rows carrying SINK_SESSION rather than
    the table.
    """
    with sqlite3.connect(sink.DB_PATH) as connection:
        rows = connection.execute(
            "SELECT received_at, event, session_id, prompt_id, length(payload)"
            " FROM events WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (SINK_SESSION, expected),
        ).fetchall()
    rows.reverse()

    for received_at, event, session_id, prompt_id, size in rows:
        print(
            f"{received_at}  {event:16} {session_id} {prompt_id or '-':4} {size} bytes"
        )

    # A row that arrived without its promoted session_id fails here too: the
    # query above cannot see it, so it reads as a row that never landed.
    if len(rows) != expected:
        raise RuntimeError(f"sent {expected} events, and {len(rows)} rows landed")
    if not any(size > 4096 for *_, size in rows):
        raise RuntimeError("the large payload did not arrive whole")

    # The hook stamps the time inside the container, so a clock that disagrees
    # with the host's would put sandboxed rows in the wrong place in the story.
    stamps = [datetime.fromisoformat(row[0]) for row in rows]
    skew = max(abs((datetime.now(UTC) - stamp).total_seconds()) for stamp in stamps)
    print(f"{len(rows)} rows on the host; container clock within {skew:.1f}s of ours")


def check_fence(mounts: list[podman.Mount] | None = None) -> None:
    """Show that nothing sensitive on the host is reachable from inside.

    Takes the mount list so it can be re-run against a real fence later:
    check-config and run-task both add a mount, and that is how a fence gets
    widened by accident.
    """
    podman.run(
        podman.container_argv(
            mounts=mounts or [],
            env={"HOME": HOME},
            command=["sh", "-c", FENCE_SCRIPT],
        )
    )
