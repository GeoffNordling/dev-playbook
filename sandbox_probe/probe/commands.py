"""One function per probe command.

Each is a handful of lines over the helpers in podman.py, so what a command
does is visible without reading anything else.
"""

import contextlib
import shutil
import signal
import tempfile
import time
from pathlib import Path

from probe import billing, podman, stream

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
    """Give the agent a real job in the clone, and show what it changed."""
    clone_repo()
    env = {"HOME": HOME}
    billing.refuse_if_metered(env, clone_settings())

    with credential_copy() as credential:
        finished = podman.run(
            podman.container_argv(
                mounts=repo_mounts(writable_repo=True) + [credential],
                env=env,
                workdir=REPO_INSIDE,
                timeout=TASK_TIMEOUT,
                command=ask_claude(prompt, skip_permissions=True),
            ),
            capture=True,
        )

    result = stream.parse_result(finished.stdout)
    print(
        f"{result.subtype}, {result.num_turns} turns, {result.duration_ms / 1000:.0f}s"
    )
    print(result.text)
    if result.is_error:
        raise RuntimeError("the run reported an error; see the text above")

    show_changes()


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
