"""The shell family: the rules of ``standards/shell/``.

Two of its rules are decided by tools, and are registered by hook name. The
other three are functions over the model. A shell file is what pre-commit's
``types: [shell]`` selects: a file whose name marks it as shell, or, where the
name says nothing, an executable file whose shebang names a shell. An
executable script is a shell file with the executable bit; a sourced fragment
is a shell file under a ``.bashrc.d/`` directory.
"""

import re
from collections.abc import Iterator
from pathlib import PurePosixPath

from dev_playbook.check_registry import Finding, check, tool_check
from dev_playbook.model import Repo

tool_check("shell.shellcheck-clean", hook="shellcheck", module=__name__)
tool_check("shell.formatted-by-shfmt", hook="shfmt", module=__name__)

# The file names and extensions pre-commit's ``identify`` tags ``shell``.
SHELL_NAMES = frozenset(
    {
        ".bash_aliases",
        ".bash_profile",
        ".bashrc",
        ".cshrc",
        ".envrc",
        ".zlogin",
        ".zlogout",
        ".zprofile",
        ".zshenv",
        ".zshrc",
        "direnvrc",
        "PKGBUILD",
    }
)
SHELL_EXTENSIONS = frozenset({"bash", "bats", "csh", "sh", "zsh"})
# The shebang interpreters ``identify`` tags ``shell``.
SHELL_INTERPRETERS = frozenset(
    {"ash", "bash", "bats", "cbsd", "csh", "dash", "ksh", "sh", "tcsh", "zsh"}
)
BASH_INTERPRETERS = frozenset({"bash", "bats"})
FRAGMENT_DIRECTORY = ".bashrc.d"
STRICT_SHEBANG = "#!/usr/bin/env bash"
STRICT_MODE = "set -euo pipefail"
# A file-wide shellcheck directive that sets the dialect to bash.
BASH_DIRECTIVE = re.compile(r"^#\s*shellcheck\s+(?:\S+\s+)*shell=bash(?:\s|$)")


def _interpreter(first_line: str) -> str | None:
    """The basename of the interpreter a ``#!`` line names, else None."""
    if not first_line.startswith("#!"):
        return None
    words = first_line[2:].split()
    if words[:2] == ["/usr/bin/env", "-S"]:
        words = words[2:]
    elif words[:1] == ["/usr/bin/env"]:
        words = words[1:]
    if not words:
        return None
    return words[0].rpartition("/")[2]


def _named_as_shell(path: str) -> bool | None:
    """Whether the file name marks shell; None where the name marks nothing."""
    name = PurePosixPath(path).name
    if any(part in SHELL_NAMES for part in [name, *name.split(".")]):
        return True
    suffix = PurePosixPath(name).suffix
    if suffix:
        return suffix[1:].lower() in SHELL_EXTENSIONS or None
    return None


def _shell_files(repo: Repo) -> Iterator[tuple[str, list[str]]]:
    """Each shell file, with its lines."""
    for path in repo.files:
        named = _named_as_shell(path)
        if named is None and path in repo.executable:
            first = repo.contents[path].split(b"\n", 1)[0]
            interpreter = _interpreter(first.decode("utf-8", "replace"))
            named = interpreter in SHELL_INTERPRETERS
        if named:
            yield path, repo.text(path).splitlines()


def _is_comment_or_blank(line: str) -> bool:
    """Whether the line holds no command: blank, or a comment."""
    stripped = line.strip()
    return not stripped or stripped.startswith("#")


@check("shell.bash-declared")
def bash_declared(repo: Repo) -> Iterator[Finding]:
    """A shell file names bash in its shebang or a directive before any command."""
    for path, lines in _shell_files(repo):
        if lines and _interpreter(lines[0]) in BASH_INTERPRETERS:
            continue
        header = []
        for line in lines:
            if not _is_comment_or_blank(line):
                break
            header.append(line.strip())
        if any(BASH_DIRECTIVE.match(line) for line in header):
            continue
        yield Finding(
            path,
            1,
            "declare bash: a shebang naming bash, or '# shellcheck shell=bash' "
            "before the first command",
        )


@check("shell.strict-mode-first")
def strict_mode_first(repo: Repo) -> Iterator[Finding]:
    """An executable script opens with the bash shebang, then ``set -euo pipefail``."""
    for path, lines in _shell_files(repo):
        if path not in repo.executable:
            continue
        if not lines or lines[0] != STRICT_SHEBANG:
            yield Finding(path, 1, f"line 1 must be exactly '{STRICT_SHEBANG}'")
            continue
        first = next(
            (
                (number, line)
                for number, line in enumerate(lines[1:], start=2)
                if not _is_comment_or_blank(line)
            ),
            None,
        )
        if first is None or first[1] != STRICT_MODE:
            line = None if first is None else first[0]
            yield Finding(path, line, f"the first command must be '{STRICT_MODE}'")


@check("shell.no-shebang-no-strict-mode")
def no_shebang_no_strict_mode(repo: Repo) -> Iterator[Finding]:
    """A sourced fragment has no shebang on line 1 and no ``set -euo pipefail``."""
    for path, lines in _shell_files(repo):
        if FRAGMENT_DIRECTORY not in PurePosixPath(path).parent.parts:
            continue
        if lines and lines[0].startswith("#!"):
            yield Finding(path, 1, "a sourced fragment carries no shebang")
        for number, line in enumerate(lines, start=1):
            if line.strip() == STRICT_MODE:
                yield Finding(
                    path, number, f"a sourced fragment carries no '{STRICT_MODE}'"
                )
