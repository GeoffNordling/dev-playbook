"""Tests for chain formatting."""

from pathlib import Path

from sdd_chain_text.formatter import format_chains
from sdd_chain_text.oft_xml import SpecItem

ROOT = Path("/project")


def test_format_single_chain():
    items = [
        SpecItem(
            full_id="req~auth~1",
            doctype="req",
            name="auth",
            version=1,
            title="Auth",
            status="approved",
            source_file="/project/specs/auth.md",
            source_line=5,
            description="The system SHALL authenticate.",
            rationale="Security.",
            needs=["dsn"],
            covers=[],
        ),
        SpecItem(
            full_id="dsn~auth~1",
            doctype="dsn",
            name="auth",
            version=1,
            title="Auth Design",
            status="approved",
            source_file="/project/specs/auth_dsn.md",
            source_line=10,
            description="AuthModule.login() SHALL validate.",
            rationale="",
            needs=[],
            covers=["req~auth~1"],
        ),
    ]

    output = format_chains([items], ROOT)
    assert "=== Chain 1: req~auth~1 > dsn~auth~1 ===" in output
    assert "[req] req~auth~1" in output
    assert "Title: Auth" in output
    assert "File: specs/auth.md:5" in output
    assert "The system SHALL authenticate." in output
    assert "Security." in output
    assert "[dsn] dsn~auth~1" in output
    assert "Covers:" in output
    assert "- req~auth~1" in output
    assert "Needs: dsn" in output
