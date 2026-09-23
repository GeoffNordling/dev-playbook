"""Unit tests for the distribution family's checks."""

from pathlib import Path

from dev_playbook.checks.distribution import dogfoods_its_manifest
from dev_playbook.model import Repo

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
