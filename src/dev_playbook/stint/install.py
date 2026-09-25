"""What a stint needs on the host before it runs: Sandcastle, and the image.

``stint setup`` installs Sandcastle beside ``sandcastle/run.mjs`` from the
committed lock file, and builds the image ``localhost/stint:latest`` from a
config copy and the host's ``claude`` binary. Run it again after either
changes: the image carries the dotfile links and the binary, so a stale
image runs a stale agent.
"""

import shutil
import subprocess
import tarfile
import tempfile
from importlib import resources
from pathlib import Path

from dev_playbook.errors import ToolError
from dev_playbook.stint.config import make_config
from dev_playbook.stint.workcopy import CopyFault, git_in

IMAGE = "localhost/stint:latest"
PACKAGE = Path(str(resources.files("dev_playbook.stint")))
SANDCASTLE = PACKAGE / "sandcastle"
IMAGE_TREE = ("src", "scripts", "dotfiles", "pyproject.toml")
"""What the image copies from the config copy, so ``sync-dotfiles`` can run."""


def run(*command: str) -> None:
    """Run a command; a nonzero exit is a ToolError carrying its output."""
    done = subprocess.run(command, capture_output=True, text=True, check=False)
    if done.returncode:
        raise ToolError(
            f"{command[0]} exited {done.returncode}: {(done.stdout + done.stderr)[-2000:]}"
        )


def setup(playbook: Path, claude: Path) -> None:
    """Install Sandcastle and build the image from ``playbook``'s main and ``claude``."""
    if not claude.is_file():
        raise ToolError(f"{claude} is not a file")
    run("npm", "ci", "--prefix", str(SANDCASTLE))
    with tempfile.TemporaryDirectory(prefix="stint-setup-") as temp:
        config, context = Path(temp) / "config", Path(temp) / "context"
        try:
            make_config(playbook, config)
            git_in(config, "archive", "-o", f"{temp}/tree.tar", "HEAD", *IMAGE_TREE)
        except CopyFault as err:
            raise ToolError(f"cannot make the config copy: {err}") from err
        with tarfile.open(f"{temp}/tree.tar") as tree:
            tree.extractall(context, filter="data")
        shutil.copyfile(claude.resolve(), context / "claude")
        (context / "claude").chmod(0o755)
        run(
            "podman",
            "build",
            "-q",
            "-t",
            IMAGE,
            "-f",
            str(PACKAGE / "Containerfile"),
            str(context),
        )


def check_installed() -> None:
    """Refuse to run a stint before ``stint setup`` has."""
    if not (SANDCASTLE / "node_modules" / "@ai-hero" / "sandcastle").is_dir():
        raise ToolError(f"Sandcastle is not installed in {SANDCASTLE}; run stint setup")
    done = subprocess.run(["podman", "image", "exists", IMAGE], check=False)
    if done.returncode:
        raise ToolError(f"the image {IMAGE} is not built; run stint setup")
