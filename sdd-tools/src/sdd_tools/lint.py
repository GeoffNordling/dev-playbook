"""Lint aggregator: dispatches every lint_* module against a spec file.

Each ``lint_*`` module owns one rule family and exposes a uniform
``check(spec_file, raw_text) -> list[Finding]`` entry point. This module
parses the file once (via ``parse.markdown``), normalizes text (``oft:off``
blocks blanked), and fans out to every module.
"""

from __future__ import annotations

from pathlib import Path

from sdd_tools import (
    lint_dimensions,
    lint_id,
    lint_obligations,
    lint_syntax,
    lint_verification,
)
from sdd_tools.models import Finding
from sdd_tools.parse.markdown import parse_text, strip_oft_off_blocks

_RULE_MODULES = (
    lint_syntax,
    lint_id,
    lint_obligations,
    lint_dimensions,
    lint_verification,
)


def lint_file(path: Path, raw_text: str) -> list[Finding]:
    """Run every lint module against one spec file and return all findings."""
    spec_file = parse_text(raw_text, path)
    stripped = strip_oft_off_blocks(raw_text)
    findings: list[Finding] = []
    for module in _RULE_MODULES:
        findings.extend(module.check(spec_file, stripped))
    return findings
