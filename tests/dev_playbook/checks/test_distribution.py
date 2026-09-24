"""Unit tests for the distribution family's checks."""

from collections.abc import Callable, Iterator
from pathlib import Path

from dev_playbook.check_registry import Finding
from dev_playbook.checks.distribution import (
    LOCAL_ENTRY,
    a_consumer_gates_only_through_its_checks,
    a_host_runs_its_own_checks,
    a_hosts_dev_playbook_rides_the_pin,
    dogfoods_its_manifest,
)
from dev_playbook.model import Repo

URL = "https://github.com/GeoffNordling/dev-playbook"
SHA = "a" * 40
CONFIG = ".pre-commit-config.yaml"
RULE = "# Local\n\n## One\n\nP.\n\n`local.one` · deterministic\n".encode()
LOCAL_BLOCK = """\
  - repo: local
    hooks:
      - id: playbook-check-local
        name: playbook check --local
        entry: {entry}
        language: system
        pass_filenames: false
        always_run: true
"""
PINNED_SOURCE = f'dev-playbook = {{ git = "{URL}", rev = "{SHA}" }}'


def host_config(entry: str | None = LOCAL_ENTRY) -> bytes:
    text = f"repos:\n  - repo: {URL}\n    rev: {SHA}\n    hooks:\n"
    text += "      - id: playbook-check\n"
    if entry is not None:
        text += LOCAL_BLOCK.format(entry=entry)
    return text.encode()


def host_pyproject(source: str) -> bytes:
    return (
        '[project]\nname = "a-host"\n\n'
        '[dependency-groups]\ndev = ["pytest>=9.0", "dev-playbook"]\n\n'
        f"[tool.uv.sources]\n{source}\n"
    ).encode()


def host_findings(
    check: Callable[[Repo], Iterator[Finding]], contents: dict[str, bytes]
) -> list[tuple[str, str]]:
    repo = Repo.from_files(Path("/r"), contents)
    return [(f.path, f.message) for f in check(repo)]


def test_a_host_runs_its_own_checks() -> None:
    check = a_host_runs_its_own_checks
    assert host_findings(check, {CONFIG: host_config(None)}) == []
    rule = {"standards/local/one.md": RULE}
    assert host_findings(check, rule | {CONFIG: host_config()}) == []
    [(path, message)] = host_findings(check, rule | {CONFIG: host_config(None)})
    assert path == CONFIG
    assert "playbook-check-local" in message
    [(_, message)] = host_findings(
        check,
        {
            "pyproject.toml": b'[project]\nname = "a-host"\n',
            "src/a_host/checks/local.py": b"",
            CONFIG: host_config("uv run playbook check --local"),
        },
    )
    assert f"entry: {LOCAL_ENTRY}" in message


def test_a_hosts_dev_playbook_rides_the_pin() -> None:
    check = a_hosts_dev_playbook_rides_the_pin
    assert host_findings(check, {CONFIG: host_config(None)}) == []
    pinned = {CONFIG: host_config(), "pyproject.toml": host_pyproject(PINNED_SOURCE)}
    assert host_findings(check, pinned) == []
    stale = PINNED_SOURCE.replace(SHA, "b" * 40)
    path_source = 'dev-playbook = { path = "/home/x/dev-playbook", editable = true }'
    for source in (stale, path_source):
        [(path, message)] = host_findings(
            check, {CONFIG: host_config(), "pyproject.toml": host_pyproject(source)}
        )
        assert path == "pyproject.toml"
        assert PINNED_SOURCE in message
    unlisted = host_pyproject(PINNED_SOURCE).replace(b', "dev-playbook"', b"")
    assert host_findings(
        check, {CONFIG: host_config(), "pyproject.toml": unlisted}
    ) == [("pyproject.toml", "`[dependency-groups] dev` must list dev-playbook")]


def test_a_consumer_gates_only_through_its_checks() -> None:
    check = a_consumer_gates_only_through_its_checks
    assert host_findings(check, {CONFIG: host_config()}) == []
    assert host_findings(check, {CONFIG: host_config(None)}) == []
    lint = host_config() + b"      - id: stories-lint\n        entry: scripts/x\n"
    [(path, message)] = host_findings(check, {CONFIG: lint})
    assert path == CONFIG
    assert "(also: stories-lint)" in message
    [(path, _)] = host_findings(
        check, {CONFIG: host_config(), ".pre-commit-hooks.yaml": MANIFEST}
    )
    assert path == ".pre-commit-hooks.yaml"
    dev_playbook = {
        "standards/build/canonical/Makefile": b"",
        CONFIG: lint,
        ".pre-commit-hooks.yaml": MANIFEST,
    }
    assert host_findings(check, dev_playbook) == []


MANIFEST = b"""\
- id: alpha-lint
  name: alpha-lint
  entry: scripts/alpha-lint
  language: script
- id: beta-lint
  name: beta-lint
  entry: scripts/beta-lint
  language: script
"""

DOGFOODED = b"""\
repos:
  - repo: https://example.com/other
    rev: v1
    hooks:
      - id: beta-lint
  - repo: local
    hooks:
      - id: alpha-lint
      - id: make-check
  - repo: local
    hooks:
      - id: beta-lint
"""

HALF_DOGFOODED = b"""\
repos:
  - repo: https://example.com/other
    rev: v1
    hooks:
      - id: beta-lint
  - repo: local
    hooks:
      - id: alpha-lint
"""


def findings(contents: dict[str, bytes]) -> list[tuple[str, int | None, str]]:
    repo = Repo.from_files(Path("/r"), contents)
    return [(f.path, f.line, f.message) for f in dogfoods_its_manifest(repo)]


def test_a_publisher_dogfoods_its_manifest() -> None:
    assert findings({".pre-commit-config.yaml": HALF_DOGFOODED}) == []
    assert (
        findings(
            {".pre-commit-hooks.yaml": MANIFEST, ".pre-commit-config.yaml": DOGFOODED}
        )
        == []
    )
    assert [
        (path, line)
        for path, line, _ in findings(
            {
                ".pre-commit-hooks.yaml": MANIFEST,
                ".pre-commit-config.yaml": HALF_DOGFOODED,
            }
        )
    ] == [(".pre-commit-config.yaml", None)]
    assert (
        "missing: alpha-lint, beta-lint"
        in findings({".pre-commit-hooks.yaml": MANIFEST})[0][2]
    )
    assert findings({".pre-commit-hooks.yaml": b"- id: [unclosed\n"})[0][:2] == (
        ".pre-commit-hooks.yaml",
        None,
    )
