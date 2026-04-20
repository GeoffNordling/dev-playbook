"""End-to-end tests for the sdd-tools pytest plugin via pytester.

These tests stand up a minimal project tree, invoke pytest within it, and
inspect the collected/run items. The OFT JAR is stubbed out as a small file
that's only used for existence checks — Java-dependent items are skipped
unless tests specifically exercise them.
"""

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
    def test_four_validators_collected(self, pytester):
        _minimal_project(pytester, VALID_REQ)
        result = pytester.runpytest("--collect-only", "-q")
        out = result.stdout.str()
        assert "spec-lint" in out
        assert "spec-coverage" in out
        assert "spec-interface" in out
        assert "spec-privacy" in out

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


class TestPrivacyItem:
    def test_clean_test_file_passes(self, pytester):
        _minimal_project(pytester, VALID_REQ)
        pytester.makepyfile(test_x="def test_a(): pass\n")
        result = pytester.runpytest("-k", "spec-privacy")
        result.assert_outcomes(passed=1)

    def test_private_import_fails(self, pytester):
        _minimal_project(pytester, VALID_REQ)
        # `from os import _exit` is a real importable private name. The privacy
        # rule flags any leading-underscore import from a non-test module.
        pytester.makepyfile(
            test_x=(
                "from os import _exit\n"
                "def test_a():\n"
                "    assert _exit is _exit\n"
            )
        )
        result = pytester.runpytest("-k", "spec-privacy")
        result.assert_outcomes(failed=1)
        assert "privacy.import-private" in result.stdout.str()
