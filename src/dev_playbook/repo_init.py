"""Fresh-repo scaffolding: the conforming tree behind ``scripts/repo-init``.

Renders every base-layer (and, with the python flag, python-layer) file for a
new workspace repository from the canonical artifacts under
``standards/build/canonical/``, then runs the local setup steps: ``git init``,
``uv lock``, staging, pre-commit hook installation, and a ``repo-lint``
self-check. The GitHub-side tail of the procedure is prose, not code:
``standards/build/bootstrap.md``.
"""

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from dev_playbook import voice

PLAYBOOK_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_DIR = PLAYBOOK_ROOT / "standards" / "build" / "canonical"
REV_PLACEHOLDER = "<pinned-sha>"


class RepoInitError(Exception):
    """The scaffold could not be produced or failed its self-check."""


@dataclass(frozen=True)
class RepoSpec:
    """What to scaffold: the repo name, its one-line purpose, and its layers."""

    name: str
    description: str
    python: bool

    @property
    def project(self) -> str:
        """The project name per the build standard's name mapping."""
        return self.name.lower()

    @property
    def package(self) -> str:
        """The import package per the build standard's name mapping."""
        return self.project.replace("-", "_")


def canonical(name: str) -> str:
    """Read one canonical artifact from the dev-playbook checkout."""
    return (CANONICAL_DIR / name).read_text(encoding="utf-8")


def pinned_rev() -> str:
    """The rev a fresh repo pins: dev-playbook's ``origin/main`` at init time."""
    out = subprocess.run(
        ["git", "-C", str(PLAYBOOK_ROOT), "rev-parse", "origin/main"],
        check=True,
        capture_output=True,
        text=True,
    )
    return out.stdout.strip()


def render_tree(spec: RepoSpec, rev: str) -> dict[str, str]:
    """Map each file the new repo needs to its content, per the skeleton."""
    # The name becomes the CLAUDE.md H1, which repo-lint reads as agent-facing
    # prose. Refuse it here, before anything is written, rather than let the
    # scaffold fail its own self-check with the tree already on disk.
    fault = voice.first_fault(spec.name)
    if fault is not None:
        raise RepoInitError(
            f"'{spec.name}' would write a CLAUDE.md that repo-lint rejects — "
            f"{fault}; choose another name"
        )
    if spec.python and not spec.package.isidentifier():
        raise RepoInitError(
            f"'{spec.name}' maps to '{spec.package}', not a valid import package"
        )
    tree = {
        "README.md": _readme(spec),
        "CLAUDE.md": f"# {spec.name}\n",
        "index.md": _bundle_index(spec),
        ".gitignore": canonical(".gitignore"),
        ".pre-commit-config.yaml": canonical(".pre-commit-config.yaml").replace(
            REV_PLACEHOLDER, rev
        ),
        ".github/workflows/ci.yml": canonical("ci.yml"),
    }
    if spec.python:
        # A fresh python repo's only .py roots are src/ and tests/, so those
        # are exactly the <code-roots> mypy can walk without exiting 2.
        tree["Makefile"] = canonical("Makefile.python").replace(
            "<code-roots>", "src tests"
        )
        tree["pyproject.toml"] = (
            canonical("pyproject.toml")
            .replace("<repo>", spec.project)
            .replace("<package>", spec.package)
        )
        tree[".python-version"] = canonical(".python-version")
        tree[f"src/{spec.package}/__init__.py"] = ""
        # tests/ must be non-empty once src/ exists; conftest.py is the one
        # pytest file exempt from the mirror-layout rule.
        tree["tests/conftest.py"] = ""
    else:
        tree["Makefile"] = canonical("Makefile.base")
    return tree


def write_tree(target: Path, tree: dict[str, str]) -> None:
    """Write every rendered file beneath ``target``, creating directories."""
    for rel, content in tree.items():
        path = target / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def init_repo(spec: RepoSpec, parent: Path) -> Path:
    """Scaffold ``parent/<name>``, run the local setup steps, and self-check.

    Steps: render and write the tree, ``git init -b main``, ``uv lock``
    (python layer only), stage everything, install both pre-commit stages,
    then run ``repo-lint`` over the result. Raises ``RepoInitError`` if the
    target already exists or the self-check reports findings; subprocess
    failures propagate as ``CalledProcessError``.
    """
    target = parent / spec.name
    if target.exists():
        raise RepoInitError(f"{target} already exists")
    write_tree(target, render_tree(spec, pinned_rev()))
    _run(["git", "init", "-b", "main"], target)
    if spec.python:
        _run(["uv", "lock"], target)
    _run(["git", "add", "-A"], target)
    _run(["uvx", "pre-commit", "install"], target)
    lint = subprocess.run(
        [str(PLAYBOOK_ROOT / "scripts" / "repo-lint"), str(target)],
        cwd=target,
        check=False,
    )
    if lint.returncode != 0:
        raise RepoInitError("repo-lint reported findings on the fresh scaffold")
    return target


def main(argv: list[str] | None = None) -> int:
    """Parse CLI arguments, scaffold the repo, and report the next steps."""
    parser = argparse.ArgumentParser(
        prog="repo-init",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "name", help="repository name; the directory created under --parent"
    )
    parser.add_argument(
        "--description",
        required=True,
        help="one-line purpose, written into README.md and the bundle index",
    )
    parser.add_argument(
        "--python",
        action="store_true",
        help="add the python layer: pyproject.toml, src/<package>/, tests/",
    )
    parser.add_argument(
        "--parent",
        type=Path,
        default=Path.home() / "workspace",
        help="directory the repo is created in (default: ~/workspace)",
    )
    args = parser.parse_args(argv)
    spec = RepoSpec(name=args.name, description=args.description, python=args.python)
    try:
        target = init_repo(spec, args.parent)
    except RepoInitError as err:
        print(f"repo-init: {err}", file=sys.stderr)
        return 1
    print(f"initialized {target}")
    print(
        "next: review and commit, then follow standards/build/bootstrap.md "
        "for the GitHub tail"
    )
    return 0


def _readme(spec: RepoSpec) -> str:
    return (
        "---\n"
        "type: README\n"
        f"title: {spec.name}\n"
        f"description: {spec.description}\n"
        "---\n"
        "\n"
        f"# {spec.name}\n"
        "\n"
        f"{spec.description}\n"
    )


def _bundle_index(spec: RepoSpec) -> str:
    return (
        "---\n"
        'okf_version: "0.1"\n'
        "---\n"
        "\n"
        f"# {spec.name} — bundle index\n"
        "\n"
        f"- [{spec.name}](/README.md) — {spec.description}\n"
    )


def _run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)
