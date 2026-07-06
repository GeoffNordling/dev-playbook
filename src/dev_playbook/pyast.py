"""Shared Python-source discovery and AST helpers for the pre-commit hooks.

`python-lint` runs three rules over one walk of a repo's Python sources; this
module is that walk. Discovery goes through `git ls-files`, so it is
gitignore-aware and worktree-scoped in the same way as dev_playbook.md.find_md_files:
from inside a worktree only that worktree's files are listed, and gitignored
caches and virtualenvs never appear. Discovery returns every Python file git
lists; which trees each rule polices is per-rule policy that lives in
`python-lint`, not here — the three retired hooks had different scopes and the
consolidation preserves each rather than imposing one shared exclusion set.
"""

import ast
import subprocess
from pathlib import Path

PYTHON_SHEBANG_PREFIXES = (
    "#!/usr/bin/env python",
    "#!/usr/bin/python",
    "#!/usr/bin/env -S uv run --script",
)


def looks_python(path: Path) -> bool:
    """True for a ``.py`` file or an extensionless file with a Python shebang.

    The pre-commit hook scripts in ``scripts/`` are extensionless but are
    Python, so a shebang sniff brings them into scope alongside ``.py`` files.
    """
    if path.suffix == ".py":
        return True
    if path.suffix:
        return False
    try:
        with path.open("rb") as fh:
            first = fh.readline(256).decode("utf-8", errors="replace")
    except OSError:
        return False
    return any(first.startswith(s) for s in PYTHON_SHEBANG_PREFIXES)


def find_python_files(root: Path) -> list[Path]:
    """All Python files in ``root``'s git checkout, honoring ``.gitignore``.

    ``--cached`` lists tracked files, ``--others`` untracked ones,
    ``--exclude-standard`` drops anything ``.gitignore`` matches — so caches
    and virtualenvs never appear. A ``--cached`` entry whose file was deleted
    from the working tree is skipped by ``is_file``. Every Python file git
    lists is returned; the caller applies its own per-rule directory scoping.
    """
    result = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    files = []
    for rel in result.stdout.split("\0"):
        if not rel:
            continue
        path = root / rel
        if path.is_file() and looks_python(path):
            files.append(path)
    return sorted(files)


def parse(path: Path) -> ast.Module | None:
    """Parse ``path`` into an AST, or return None if it can't be read or parsed.

    Read and syntax errors yield None rather than raising: a file that does not
    parse cannot violate an AST-level rule, and syntax itself is ruff's job.
    """
    try:
        source = path.read_text(encoding="utf-8")
    except OSError:
        return None
    try:
        return ast.parse(source, filename=str(path))
    except SyntaxError:
        return None
