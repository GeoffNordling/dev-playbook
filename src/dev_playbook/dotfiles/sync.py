"""Install the dotfiles tree into $HOME: stow the packages.

What lands where, and the workflow around it: /dotfiles/README.md.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# Package directory in dotfiles/ -> the directory under $HOME it installs into.
#
# Stow puts a package's *contents* in the target, not the package directory
# itself, so each package must be targeted at the directory it is named for.
# Targeting $HOME scatters the contents one level too high.
PACKAGES = {
    ".bashrc.d": ".bashrc.d",
    "dot-claude": ".claude",
}

# stow itself, plus what the hooks this installs go on to call.
REQUIRED_TOOLS = ("stow", "git", "jq", "python3")

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


def _inside(path: Path, root: Path) -> bool:
    """Whether path is root itself or sits somewhere under it."""
    return path == root or root in path.parents


def claim_targets(home: Path, dotfiles: Path) -> list[Path]:
    """Make every package target a real directory. Returns the ones replaced.

    A target that is a symlink into this repo points at the package about to be
    stowed there, so stow is handed the same directory as both source and
    destination and asked to link every file over itself. It aborts, and the
    install stops on its first package.
    """
    replaced = []
    for package in PACKAGES:
        target = target_for(home, package)
        if target.is_symlink():
            if not _inside(target.resolve(), dotfiles.resolve()):
                raise SyncError(
                    f"{target} is a symlink to {target.resolve()}, which this "
                    f"install does not manage. Move it aside and re-run."
                )
            target.unlink()
            replaced.append(target)
        elif target.exists() and not target.is_dir():
            raise SyncError(f"{target} is a file; package {package} needs a directory")
        target.mkdir(parents=True, exist_ok=True)
    return replaced


def stray_links(home: Path, dotfiles: Path) -> list[Path]:
    """Links loose in $HOME that point into this repo.

    A package stowed at $HOME rather than at its own directory scatters its
    contents here, one level above where they belong. They are this install's
    own links and no current package claims them.
    """
    dotfiles = dotfiles.resolve()
    claimed = set(PACKAGES.values())
    return [
        path
        for path in sorted(home.iterdir())
        if path.name not in claimed
        and path.is_symlink()
        and _inside(path.resolve(), dotfiles)
    ]


def managed_links(home: Path) -> set[Path]:
    """Every symlink inside the package targets — what stow has installed."""
    found: set[Path] = set()
    for name in PACKAGES.values():
        directory = home / name
        if directory.is_dir():
            found.update(path for path in directory.rglob("*") if path.is_symlink())
    return found


def missing_tools() -> list[str]:
    """The required tools this host does not have, in declaration order."""
    return [tool for tool in REQUIRED_TOOLS if shutil.which(tool) is None]


def stale_links(home: Path, dotfiles: Path) -> list[Path]:
    """Managed links pointing at something this repo no longer has.

    A rename or a deletion inside a package leaves its link behind pointing at
    nothing, and stow never returns to a path it has nothing to place at. A
    live link is stow's own and stow keeps it current, so only the broken ones
    are anyone's business here — and only those into this repo: a target
    directory holds unmanaged content too, and someone else's broken link is
    not this install's to remove.
    """
    found = []
    dotfiles = dotfiles.resolve()
    for name in PACKAGES.values():
        directory = home / name
        if not directory.is_dir():
            continue
        for path in directory.rglob("*"):
            if (
                path.is_symlink()
                and not path.exists()
                and _inside(path.resolve(), dotfiles)
            ):
                found.append(path)
    return found


def stow_packages(home: Path, dotfiles: Path) -> None:
    """Link every package's contents into the directory it is named for.

    Every target must already be a real directory; claim_targets makes it one.
    """
    for package in PACKAGES:
        subprocess.run(
            [
                "stow",
                "-d",
                str(dotfiles),
                "-t",
                str(target_for(home, package)),
                package,
            ],
            check=True,
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


def clear_generated_settings(home: Path) -> bool:
    """Remove a regular-file ~/.claude/settings.json so stow can link one there.

    The settings file used to be generated in place (a base fragment merged
    with a machine fragment); today it is one shared file in the dot-claude
    package, stowed like everything else. Stow aborts on a regular file where
    its link belongs, so the leftover from the generated era must go first —
    its content was a rendering of the same sources, so nothing is lost. A
    symlink is left for stow to judge: its own link is kept current, and
    someone else's makes stow abort loudly rather than being silently replaced.
    """
    target = home / ".claude" / "settings.json"
    if target.is_symlink() or not target.is_file():
        return False
    target.unlink()
    return True


def sync(repo: Path, home: Path) -> list[str]:
    """Run every install step. Returns one line per thing that changed."""
    if missing := missing_tools():
        raise SyncError(
            f"missing required tools: {' '.join(missing)}\n"
            "Install them and re-run; this manages no package manager."
        )

    dotfiles = repo / "dotfiles"

    changed = []
    for target in claim_targets(home, dotfiles):
        changed.append(f"replaced the {target} link with a real directory")
    for link in stray_links(home, dotfiles):
        link.unlink()
        changed.append(f"removed stray link: {link}")

    if clear_generated_settings(home):
        changed.append("removed the generated settings.json; stow links it now")

    installed = managed_links(home)
    stow_packages(home, dotfiles)
    if new := managed_links(home) - installed:
        changed.append(f"stowed {len(new)} link(s)")

    for link in stale_links(home, dotfiles):
        link.unlink()
        changed.append(f"removed dead link: {link}")

    if ensure_bashrc_loader(home / ".bashrc"):
        changed.append("appended the ~/.bashrc.d loader (open a new shell for it)")

    return changed


def run_cli() -> int:
    """Entry point for scripts/sync-dotfiles."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    repo = Path(__file__).resolve().parents[3]
    home = Path.home()

    try:
        if not (changed := sync(repo, home)):
            print("already installed; nothing to do")
        for line in changed:
            print(line)
    except (SyncError, subprocess.CalledProcessError, ValueError) as error:
        print(f"sync-dotfiles: {error}", file=sys.stderr)
        return 2
    return 0
