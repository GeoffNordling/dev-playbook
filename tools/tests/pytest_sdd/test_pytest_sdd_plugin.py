"""End-to-end tests for the pytest-sdd plugin using pytester."""



VALID_SPEC_ITEM = """\
---

### My Requirement
`req~area.item~1`
Status: approved

The system `SHALL` do something.

Needs: utest

---
"""

VALID_DSN_ITEM = """\
---

### Design Item
`dsn~area.design~1`
Status: approved

The function `SHALL` implement the requirement.

Covers:
  - req~area.item~1

Needs: utest

---
"""


def _minimal_project(pytester, spec_content: str, jar_exists: bool = True) -> None:
    """Set up a minimal project with spec files and pyproject.toml."""
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


class TestPluginIntegration:
    def test_spec_items_collected(self, pytester):
        """Plugin collects spec lint items from configured spec dirs."""
        _minimal_project(pytester, VALID_SPEC_ITEM)
        result = pytester.runpytest("--collect-only", "-q")
        result.stdout.fnmatch_lines(["*requirements.md*lint*"])

    def test_spec_trace_item_collected(self, pytester):
        """Plugin collects the OFT trace item when oft_jar is configured."""
        _minimal_project(pytester, VALID_SPEC_ITEM)
        result = pytester.runpytest("--collect-only", "-q")
        result.stdout.fnmatch_lines(["*spec-trace*"])

    def test_m_spec_filter_selects_only_spec_items(self, pytester):
        """Running pytest -m spec collects only spec validation items."""
        _minimal_project(pytester, VALID_SPEC_ITEM)
        # Add a normal test
        pytester.makepyfile(
            test_normal="""\
def test_regular():
    pass
"""
        )
        result = pytester.runpytest("--collect-only", "-q", "-m", "spec")
        output = result.stdout.str()
        assert "::lint" in output
        assert "test_regular" not in output

    def test_m_not_spec_excludes_spec_items(self, pytester):
        """Running pytest -m 'not spec' excludes spec items."""
        _minimal_project(pytester, VALID_SPEC_ITEM)
        pytester.makepyfile(
            test_normal="""\
def test_regular():
    pass
"""
        )
        result = pytester.runpytest("--collect-only", "-q", "-m", "not spec")
        output = result.stdout.str()
        assert "spec-lint" not in output
        assert "test_regular" in output

    def test_no_config_no_spec_items(self, pytester):
        """Without [tool.pytest-sdd], no spec items are injected."""
        pytester.makefile(".toml", pyproject="[project]\nname = 'myproject'\n")
        result = pytester.runpytest("--collect-only", "-q")
        output = result.stdout.str()
        assert "spec-lint" not in output
        assert "spec-trace" not in output

    def test_clean_spec_passes(self, pytester):
        """A valid spec file passes lint checks."""
        _minimal_project(pytester, VALID_SPEC_ITEM)
        result = pytester.runpytest("-m", "spec", "-k", "lint")
        result.assert_outcomes(passed=1)

    def test_bare_obligation_fails_lint(self, pytester):
        """A spec file with bare SHALL fails lint."""
        bad_spec = """\
---

### Item
`req~area.item~1`
Status: approved

The system SHALL do something without backticks.

Needs: utest

---
"""
        _minimal_project(pytester, bad_spec)
        result = pytester.runpytest("-m", "spec", "-k", "lint")
        result.assert_outcomes(failed=1)

    def test_missing_status_fails_lint(self, pytester):
        """A spec file with missing Status fails lint."""
        bad_spec = """\
---

### Item
`req~area.item~1`

The system `SHALL` do something.

Needs: utest

---
"""
        _minimal_project(pytester, bad_spec)
        result = pytester.runpytest("-m", "spec", "-k", "lint")
        result.assert_outcomes(failed=1)

    def test_mixed_obligations_fails_lint(self, pytester):
        """A spec item mixing SHALL and MAY fails lint."""
        bad_spec = """\
---

### Item
`req~area.item~1`
Status: approved

The system `SHALL` do A and `MAY` do B.

Needs: utest

---
"""
        _minimal_project(pytester, bad_spec)
        result = pytester.runpytest("-m", "spec", "-k", "lint")
        result.assert_outcomes(failed=1)

    def test_index_file_passes_lint(self, pytester):
        """An index file with no spec items passes lint (no checks to fail)."""
        index_content = """\
# Index

| File | Scope |
|------|-------|
| requirements.md | Core requirements |
"""
        _minimal_project(pytester, index_content)
        result = pytester.runpytest("-m", "spec", "-k", "lint")
        result.assert_outcomes(passed=1)

    def test_missing_jar_fails_trace(self, pytester):
        """Missing OFT JAR causes spec-trace to fail."""
        _minimal_project(pytester, VALID_SPEC_ITEM, jar_exists=False)
        result = pytester.runpytest("-m", "spec", "-k", "trace")
        result.assert_outcomes(failed=1)

    def test_spec_marker_registered(self, pytester):
        """The 'spec' marker is registered (no PytestUnknownMarkWarning)."""
        _minimal_project(pytester, VALID_SPEC_ITEM)
        result = pytester.runpytest("-m", "spec", "--collect-only", "-q")
        assert "PytestUnknownMarkWarning" not in result.stdout.str()
        assert "PytestUnknownMarkWarning" not in result.stderr.str()
