"""Install the dotfiles tree into $HOME: stow the packages, generate the settings.

What lands where, and the workflow around it: /dotfiles/README.md.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from dev_playbook.dotfiles import settings
from dev_playbook.dotfiles.machine import detect_machine

# Package directory in dotfiles/ -> the directory under $HOME it installs into.
#
# Stow puts a package's *contents* in the target, not the package directory
# itself, so each package must be targeted at the directory it is named for.
# Targeting $HOME scatters the contents one level too high.
PACKAGES = {
    ".agents": ".agents",
    ".bashrc.d": ".bashrc.d",
    "dot-claude": ".claude",
}

# stow itself, plus what the hooks this installs go on to call.
REQUIRED_TOOLS = ("stow", "git", "jq")

LOADER_MARKER = "# >>> dev-playbook bashrc.d loader >>>"
LOADER = f"""
{LOADER_MARKER}
for _rc in "$HOME"/.bashrc.d/*.sh; do
\t[ -r "$_rc" ] && . "$_rc"
done
unset _rc
# <<< dev-playbook bashrc.d loader <<<
"""


class SyncError(Exception):
    """The sync cannot proceed. Reported as a message, never a traceback."""


def target_for(home: Path, package: str) -> Path:
    """The directory a package's contents install into."""
    return home / PACKAGES[package]


def missing_tools() -> list[str]:
    """The required tools this host does not have, in declaration order."""
    return [tool for tool in REQUIRED_TOOLS if shutil.which(tool) is None]


def mirror_skills(dotfiles: Path) -> list[str]:
    """Point dot-claude/skills/ at every .agents/skills/ entry. Names mirrored.

    Claude Code discovers skills only under ~/.claude/skills/, so an externally
    managed skill is unreachable until it has a symlink in the stowed package.
    """
    source = dotfiles / ".agents" / "skills"
    mirror = dotfiles / "dot-claude" / "skills"
    if not source.is_dir() or not mirror.is_dir():
        return []

    for link in mirror.iterdir():
        if link.is_symlink() and not link.exists():
            link.unlink()

    mirrored = []
    for entry in sorted(p for p in source.iterdir() if p.is_dir()):
        link = mirror / entry.name
        if link.is_symlink():
            continue
        if link.exists():
            raise SyncError(
                f"{link} is an authored skill; cannot mirror .agents/skills/{entry.name}"
            )
        link.symlink_to(Path("../../.agents/skills") / entry.name)
        mirrored.append(entry.name)
    return mirrored


def stale_links(home: Path, dotfiles: Path) -> list[Path]:
    """Managed links stow should be left to recreate from scratch.

    Two kinds qualify: a broken link, whose target the repo renamed or deleted,
    and a live link into this repo that stow did not make itself — stow refuses
    to touch a link it does not own, so one it did not make blocks the package
    that claims that path. Anything that is not a link into this repo is
    someone else's and is left alone; a target directory holds unmanaged
    content too (~/.claude also keeps session data).
    """
    found = []
    dotfiles = dotfiles.resolve()
    for name in PACKAGES.values():
        directory = home / name
        if not directory.is_dir():
            continue
        for path in directory.rglob("*"):
            if path.is_symlink() and (
                not path.exists() or dotfiles in path.resolve().parents
            ):
                found.append(path)
    return found


def stow_packages(home: Path, dotfiles: Path) -> None:
    """Link every package's contents into the directory it is named for."""
    for package in PACKAGES:
        target = target_for(home, package)
        target.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["stow", "-d", str(dotfiles), "-t", str(target), package], check=True
        )


def ensure_bashrc_loader(bashrc: Path) -> bool:
    """Append a ~/.bashrc.d loader unless one is already wired up. True if added.

    Fedora's stock ~/.bashrc sources ~/.bashrc.d/*.sh; Ubuntu's does not, so on
    a secondary the stowed snippets would be inert. Keyed on the marker, so
    re-runs add nothing and a hand-rolled loader is left alone.
    """
    if not bashrc.is_file():
        return False
    text = bashrc.read_text()
    if LOADER_MARKER in text or ".bashrc.d" in text:
        return False
    bashrc.write_text(text + LOADER)
    return True


def sync(repo: Path, home: Path) -> list[str]:
    """Run every install step. Returns one line per thing that changed."""
    if missing := missing_tools():
        raise SyncError(
            f"missing required tools: {' '.join(missing)}\n"
            "Install them and re-run; this manages no package manager."
        )

    dotfiles = repo / "dotfiles"
    machine = detect_machine()

    changed = [f"mirrored skill: {name}" for name in mirror_skills(dotfiles)]

    for link in stale_links(home, dotfiles):
        link.unlink()
    stow_packages(home, dotfiles)
    changed.append(f"stowed: {' '.join(PACKAGES)}")

    if ensure_bashrc_loader(home / ".bashrc"):
        changed.append("appended the ~/.bashrc.d loader (open a new shell for it)")

    target = home / ".claude" / "settings.json"
    if settings.install(dotfiles / "settings", machine, target):
        changed.append(f"installed settings for {machine}")
    else:
        changed.append(f"settings already current ({machine})")

    return changed


def drift_report(repo: Path, home: Path) -> str | None:
    """What to tell the user about stale settings, or None when they are current."""
    settings_dir = repo / "dotfiles" / "settings"
    target = home / ".claude" / "settings.json"
    machine = detect_machine()
    if settings.is_current(settings_dir, machine, target):
        return None
    return (
        f"Claude Code settings are out of date for this machine ({machine}).\n"
        f"  installed: {target}\n"
        f"  source:    {settings_dir}/base.json + {machine}.json\n"
        f"Run {repo}/scripts/sync-dotfiles to reinstall. If you edited the\n"
        "installed file directly, move the change into the source instead --\n"
        "the installed copy is generated and the edit will be overwritten."
    )


def run_cli() -> int:
    """Entry point for scripts/sync-dotfiles."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="report whether the installed settings match, changing nothing",
    )
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[3]
    home = Path.home()

    try:
        if args.check:
            if (report := drift_report(repo, home)) is None:
                return 0
            print(report)
            return 1

        for line in sync(repo, home):
            print(line)
    except (SyncError, subprocess.CalledProcessError, ValueError) as error:
        print(f"sync-dotfiles: {error}", file=sys.stderr)
        return 2
    return 0
