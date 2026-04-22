"""Tests for sdd_tools.lint_verification."""

from __future__ import annotations

from pathlib import Path

from sdd_tools.lint import lint_file


def _by_rule(findings, rule: str):
    return [f for f in findings if f.rule == rule]


_ALL_FOUR_HEADERS = "## Data\n\n## API Shape\n\n## Algorithms\n\n## Composition\n"


def _dsn_file(body: str) -> str:
    return "## Data\n\n" + body + "\n## API Shape\n\n## Algorithms\n\n## Composition\n"


class TestMissingVerification:
    def test_dsn_with_needs_passes(self):
        text = _dsn_file(
            "### Foo\n"
            "`dsn~foo~1`\n"
            "Status: approved\n"
            "Needs: utest\n"
            "\n"
        )
        assert _by_rule(lint_file(Path("d.md"), text), "lint.missing-verification") == []

    def test_dsn_with_interface_passes(self):
        text = _dsn_file(
            "### Foo\n"
            "`dsn~foo~1`\n"
            "Status: approved\n"
            "Interface: mod.fn() -> None\n"
            "\n"
        )
        assert _by_rule(lint_file(Path("d.md"), text), "lint.missing-verification") == []

    def test_dsn_with_agent_review_passes(self):
        text = _dsn_file(
            "### Foo\n"
            "`dsn~foo~1`\n"
            "Status: approved\n"
            "AgentReview: The prompt discourages filler.\n"
            "\n"
        )
        assert _by_rule(lint_file(Path("d.md"), text), "lint.missing-verification") == []

    def test_dsn_with_all_three_passes(self):
        text = _dsn_file(
            "### Foo\n"
            "`dsn~foo~1`\n"
            "Status: approved\n"
            "Needs: utest\n"
            "Interface: mod.fn() -> None\n"
            "AgentReview: Something.\n"
            "\n"
        )
        assert _by_rule(lint_file(Path("d.md"), text), "lint.missing-verification") == []

    def test_dsn_with_no_verification_flagged(self):
        text = _dsn_file(
            "### Foo\n"
            "`dsn~foo~1`\n"
            "Status: approved\n"
            "\n"
            "Just prose, no verification.\n"
            "\n"
        )
        findings = _by_rule(
            lint_file(Path("d.md"), text), "lint.missing-verification"
        )
        assert len(findings) == 1
        assert findings[0].spec_id == "dsn~foo~1"

    def test_non_dsn_missing_verification_not_flagged(self):
        """Verification rule is dsn-only; feat/req may rely on Needs: alone
        which is covered by OFT coverage, not this rule."""
        text = (
            "### Req\n"
            "`req~foo~1`\n"
            "Status: approved\n"
            "\n"
            "No extra fields.\n"
        )
        findings = _by_rule(
            lint_file(Path("d.md"), text), "lint.missing-verification"
        )
        assert findings == []


class TestBadAgentReview:
    def test_agent_review_on_req_flagged(self):
        text = (
            "### Req\n"
            "`req~foo~1`\n"
            "Status: approved\n"
            "AgentReview: Should be on a dsn not a req.\n"
            "\n"
            "Needs: dsn\n"
        )
        findings = _by_rule(lint_file(Path("d.md"), text), "lint.bad-agent-review")
        assert len(findings) == 1
        assert findings[0].spec_id == "req~foo~1"

    def test_agent_review_on_dsn_no_finding(self):
        text = _dsn_file(
            "### Foo\n"
            "`dsn~foo~1`\n"
            "Status: approved\n"
            "AgentReview: Something to check.\n"
            "\n"
        )
        assert _by_rule(lint_file(Path("d.md"), text), "lint.bad-agent-review") == []
