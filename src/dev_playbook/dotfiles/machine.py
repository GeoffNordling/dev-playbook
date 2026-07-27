"""Machine identity: which of the workspace's machines this host is.

The inventory and what differs between them: /docs/machines.md.
"""

from pathlib import Path

FEDORA = "fedora"
WSL = "wsl"
MACHINES = (FEDORA, WSL)

# $WSL_DISTRO_NAME is friendlier but is exported only into interactive shells,
# so it is absent exactly where detection matters — a hook, a cron job.
PROC_VERSION = Path("/proc/version")
OS_RELEASE = Path("/etc/os-release")


def detect_machine() -> str:
    """The machine key for this host, as used to name a settings fragment."""
    if "microsoft" in PROC_VERSION.read_text().lower():
        return WSL

    for line in OS_RELEASE.read_text().splitlines():
        if line.startswith("ID="):
            distro = line.removeprefix("ID=").strip().strip('"')
            if distro == FEDORA:
                return FEDORA
            raise ValueError(
                f"unknown machine: /etc/os-release ID={distro!r} is not WSL and "
                f"not Fedora. Add a fragment for it and extend MACHINES."
            )

    raise ValueError(f"unknown machine: no ID= line in {OS_RELEASE}")
