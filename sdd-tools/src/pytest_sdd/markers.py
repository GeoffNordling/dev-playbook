"""Extract OFT coverage from pytest markers and generate spec items.

Scans collected pytest items for markers whose names match OFT artifact types
(e.g., @pytest.mark.req, @pytest.mark.dsn). For each unique spec ID referenced,
generates a ``utest`` spec item that covers it. The generated items are written
to a temporary markdown file that OFT can read alongside the real spec dirs.

This bridges the gap between pytest-level traceability markers and OFT's
markdown-only tracing model.
"""

import tempfile
from pathlib import Path

import pytest

from pytest_sdd.models import KNOWN_ARTIFACT_TYPES, SPEC_ID_BARE_RE

# Marker names we scan for: OFT artifact types that appear in test markers
_MARKER_NAMES = KNOWN_ARTIFACT_TYPES


def collect_covered_ids(items: list[pytest.Item]) -> dict[str, set[str]]:
    """Scan pytest items for OFT-related markers and return covered spec IDs.

    Returns a dict mapping each covered spec ID (e.g. "req~auth.login~1")
    to the set of test node IDs that cover it.
    """
    covered: dict[str, set[str]] = {}
    for item in items:
        for marker in item.iter_markers():
            if marker.name not in _MARKER_NAMES:
                continue
            for arg in marker.args:
                if isinstance(arg, str) and SPEC_ID_BARE_RE.fullmatch(arg):
                    covered.setdefault(arg, set()).add(item.nodeid)
    return covered


def generate_coverage_markdown(covered_ids: dict[str, set[str]]) -> str:
    """Generate OFT-compatible markdown with utest items covering the given IDs.

    Each unique covered spec ID gets one ``utest`` item with a Covers: link.
    """
    if not covered_ids:
        return ""

    lines = ["# Generated utest coverage from pytest markers", ""]
    for spec_id in sorted(covered_ids):
        match = SPEC_ID_BARE_RE.fullmatch(spec_id)
        if not match:
            continue
        name = match.group(2)
        revision = match.group(3)
        lines.extend(
            [
                "---",
                "",
                f"### Test coverage for {spec_id}",
                f"`utest~{name}~{revision}`",
                "Status: approved",
                "",
                "Covers:",
                f"  - {spec_id}",
                "",
            ]
        )
    lines.append("---\n")
    return "\n".join(lines)


def write_coverage_file(covered_ids: dict[str, set[str]], tmp_dir: Path) -> Path:
    """Write generated coverage markdown to a file in the given directory.

    Returns the path to the written file.
    """
    content = generate_coverage_markdown(covered_ids)
    coverage_file = tmp_dir / "utest-coverage.md"
    coverage_file.write_text(content, encoding="utf-8")
    return coverage_file


def create_coverage_dir(
    items: list[pytest.Item],
) -> "tempfile.TemporaryDirectory | None":
    """Scan items for markers and create a temp dir with coverage markdown.

    Returns a TemporaryDirectory (caller must manage its lifecycle) or None
    if no markers were found.
    """
    covered_ids = collect_covered_ids(items)
    if not covered_ids:
        return None

    tmp = tempfile.TemporaryDirectory(prefix="pytest-sdd-")
    write_coverage_file(covered_ids, Path(tmp.name))
    return tmp
