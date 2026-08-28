"""Everything that talks to podman.

The rest of the probe deals in plain data — paths, strings, lists. This is the
only module that turns that data into a container, so it is the only one where
a system-level detail can hide.
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path

IMAGE = "sandbox-probe"

# The directory holding the Containerfile: this file's parent's parent.
PROBE_DIR = Path(__file__).resolve().parent.parent

# The build context — the one directory a build may copy from. It is the repo
# root, not PROBE_DIR, because the Containerfile copies in src/, scripts/, and
# dotfiles/ so it can run sync-dotfiles. .containerignore keeps the rest out.
REPO_ROOT = PROBE_DIR.parent


@dataclass(frozen=True)
class Mount:
    """One host path made visible inside the container at one chosen path.

    The host path is always a copy — a throwaway clone, a copied credentials
    file — never something the host still needs. to_arg() explains why.
    """

    host: Path
    inside: Path
    writable: bool = False

    def to_arg(self) -> str:
        """The --volume argument podman wants for this mount.

        The trailing Z asks SELinux to retag the host path so the container is
        allowed to read it. This machine runs SELinux in enforcing mode, so
        without the Z the mount still appears inside but every read is denied.

        The retag is permanent and applies even to a read-only mount, which is
        why the host path is always a copy.
        """
        mode = "rw" if self.writable else "ro"
        return f"--volume={self.host}:{self.inside}:{mode},Z"


def container_argv(
    *,
    mounts: list[Mount],
    env: dict[str, str],
    command: list[str],
    workdir: str | None = None,
    name: str | None = None,
    timeout: int | None = None,
    image: str = IMAGE,
) -> list[str]:
    """The full podman command line for one run. Nothing is executed here.

    Kept separate from running it so the fence can be read before it is
    trusted: print the list and every host path the container can reach is on
    one screen.
    """
    argv = [
        "podman",
        "run",
        "--rm",  # delete the container once the command inside exits
        # Without this, files the container writes into a mount come back
        # owned by a user that does not exist on the host, and you cannot
        # delete them normally.
        "--userns=keep-id",
    ]
    # The container otherwise starts in /, and an agent told to edit a file
    # needs to start in the repo holding it.
    if workdir:
        argv.append(f"--workdir={workdir}")
    # Podman invents a name when you do not give one, so a container has to be
    # named to be looked for afterwards.
    if name:
        argv.append(f"--name={name}")
    # A container outlives a runner that was killed with SIGKILL, because
    # nothing gets to run cleanup code on SIGKILL. Podman enforces this
    # deadline from inside instead, so a stranded container ends on its own.
    if timeout:
        argv.append(f"--timeout={timeout}")
    argv += [mount.to_arg() for mount in mounts]
    argv += [f"--env={name}={value}" for name, value in env.items()]
    argv.append(image)
    argv += command
    return argv


def build_image(tag: str = IMAGE) -> None:
    """Build the image from the Containerfile next to this package.

    --file and the context are separate: the recipe lives in sandbox_probe/,
    but it copies from the repo root, so that is what the build is pointed at.
    """
    run(
        [
            "podman",
            "build",
            "--tag",
            tag,
            "--file",
            str(PROBE_DIR / "Containerfile"),
            str(REPO_ROOT),
        ]
    )


def start(argv: list[str]) -> subprocess.Popen:
    """Start a command and return without waiting for it to finish.

    run() blocks until the container exits, which is no use when the point is
    to kill it partway through.
    """
    print("+", " ".join(argv), flush=True)
    return subprocess.Popen(argv)


def container_exists(name: str) -> bool:
    """Whether a container of this name is around, running or stopped.

    Not printed, unlike run(): this gets polled, and the echo would bury the
    answer it is looking for.
    """
    listed = subprocess.run(
        ["podman", "ps", "--all", "--filter", f"name={name}", "--format", "{{.Names}}"],
        check=True,
        capture_output=True,
        text=True,
    )
    return bool(listed.stdout.split())


def remove_container(name: str) -> None:
    """Delete a container by name. --ignore makes a missing one not an error."""
    subprocess.run(
        ["podman", "rm", "--force", "--ignore", name],
        check=True,
        capture_output=True,
        text=True,
    )


def run(argv: list[str], *, capture: bool = False) -> subprocess.CompletedProcess:
    """Run a command, printing it first, and raise if it fails.

    check=True is deliberate: a failed step should stop the probe where it
    broke rather than let a later command report a confusing symptom.
    """
    print("+", " ".join(argv), flush=True)
    return subprocess.run(argv, check=True, capture_output=capture, text=True)
