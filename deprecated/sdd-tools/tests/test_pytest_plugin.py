"""Tests for sdd_tools.pytest_plugin."""

VALID_REQ = """\
---

### My Requirement
`req~area.item~1`
Status: approved

The system `SHALL` do something.

Needs: utest

---
"""

BARE_OBLIGATION_SPEC = """\
---

### Item
`req~area.item~1`
Status: approved

The system SHALL do something without backticks.

Needs: utest

---
"""


def _minimal_project(pytester, spec_content: str, jar_exists: bool = True) -> None:
    """Set up a minimal project tree the plugin can read."""
    pytester.makefile(
        ".toml",
        pyproject="""\
[tool.pytest-sdd]
spec_dirs = ["specs"]
oft_jar = "tools/oft.jar"
""",
    )
    (pytester.path / "specs").mkdir()
    (pytester.path / "specs" / "requirements.md").write_text(
        spec_content, encoding="utf-8"
    )
    (pytester.path / "tools").mkdir()
    if jar_exists:
        (pytester.path / "tools" / "oft.jar").write_bytes(b"PK")


class TestCollection:
    def test_three_validators_collected(self, pytester):
        _minimal_project(pytester, VALID_REQ)
        result = pytester.runpytest("--collect-only", "-q")
        out = result.stdout.str()
        assert "spec-lint" in out
        assert "spec-coverage" in out
        assert "spec-interface" in out
        assert "spec-privacy" not in out

    def test_no_config_no_items(self, pytester):
        pytester.makefile(".toml", pyproject="[project]\nname = 'p'\n")
        result = pytester.runpytest("--collect-only", "-q")
        out = result.stdout.str()
        assert "spec-lint" not in out

    def test_marker_filter_includes_spec_only(self, pytester):
        _minimal_project(pytester, VALID_REQ)
        pytester.makepyfile(test_normal="def test_a(): pass\n")
        result = pytester.runpytest("--collect-only", "-q", "-m", "spec")
        out = result.stdout.str()
        assert "spec-lint" in out
        assert "test_normal" not in out

    def test_marker_filter_excludes_spec(self, pytester):
        _minimal_project(pytester, VALID_REQ)
        pytester.makepyfile(test_normal="def test_a(): pass\n")
        result = pytester.runpytest("--collect-only", "-q", "-m", "not spec")
        out = result.stdout.str()
        assert "spec-lint" not in out
        assert "test_normal" in out

    def test_spec_marker_registered_no_warning(self, pytester):
        _minimal_project(pytester, VALID_REQ)
        result = pytester.runpytest("-m", "spec", "--collect-only", "-q")
        assert "PytestUnknownMarkWarning" not in result.stdout.str()
        assert "PytestUnknownMarkWarning" not in result.stderr.str()


class TestLintItem:
    def test_clean_spec_passes(self, pytester):
        _minimal_project(pytester, VALID_REQ)
        result = pytester.runpytest("-k", "spec-lint")
        result.assert_outcomes(passed=1)

    def test_bare_obligation_fails(self, pytester):
        _minimal_project(pytester, BARE_OBLIGATION_SPEC)
        result = pytester.runpytest("-k", "spec-lint")
        result.assert_outcomes(failed=1)

    def test_failure_renders_finding(self, pytester):
        _minimal_project(pytester, BARE_OBLIGATION_SPEC)
        result = pytester.runpytest("-k", "spec-lint", "-v")
        out = result.stdout.str()
        assert "lint.bare-obligation" in out


class TestCoverageItem:
    def test_missing_jar_fails(self, pytester):
        _minimal_project(pytester, VALID_REQ, jar_exists=False)
        result = pytester.runpytest("-k", "spec-coverage")
        result.assert_outcomes(failed=1)


