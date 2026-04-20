"""Tests for sdd_tools.privacy."""

from pathlib import Path

from sdd_tools.privacy import validate_files


def _write(tmp_path: Path, name: str, source: str) -> Path:
    f = tmp_path / name
    f.write_text(source, encoding="utf-8")
    return f


def _by_rule(findings, rule):
    return [f for f in findings if f.rule == rule]


# ---------------------------------------------------------------------------
# Imports of private names
# ---------------------------------------------------------------------------


class TestImportPrivate:
    def test_clean_import_no_finding(self, tmp_path):
        f = _write(tmp_path, "test_x.py", "from myproject import public_thing\n")
        assert validate_files([f]) == []

    def test_import_private_name_flagged(self, tmp_path):
        f = _write(tmp_path, "test_x.py", "from myproject import _internal\n")
        findings = _by_rule(validate_files([f]), "privacy.import-private")
        assert len(findings) == 1
        assert "_internal" in findings[0].message

    def test_import_private_module_segment_flagged(self, tmp_path):
        f = _write(tmp_path, "test_x.py", "import myproject._internal\n")
        findings = _by_rule(validate_files([f]), "privacy.import-private")
        assert len(findings) == 1
        assert "_internal" in findings[0].message

    def test_from_through_private_segment_flagged(self, tmp_path):
        f = _write(
            tmp_path,
            "test_x.py",
            "from myproject._internal import helper\n",
        )
        findings = _by_rule(validate_files([f]), "privacy.import-private")
        assert len(findings) == 1

    def test_dunder_allowed(self, tmp_path):
        f = _write(tmp_path, "test_x.py", "from myproject import __version__\n")
        assert validate_files([f]) == []

    def test_test_module_allowed(self, tmp_path):
        f = _write(tmp_path, "test_x.py", "from tests.helpers import _make_thing\n")
        assert validate_files([f]) == []

    def test_conftest_allowed(self, tmp_path):
        f = _write(tmp_path, "test_x.py", "from conftest import _fixture\n")
        assert validate_files([f]) == []


# ---------------------------------------------------------------------------
# Attribute access on imported names
# ---------------------------------------------------------------------------


class TestAttributeAccess:
    def test_clean_attribute_access_no_finding(self, tmp_path):
        source = (
            "import myproject\n"
            "\n"
            "def test_a():\n"
            "    myproject.public_fn()\n"
        )
        f = _write(tmp_path, "test_x.py", source)
        assert _by_rule(validate_files([f]), "privacy.attribute-access") == []

    def test_attribute_access_to_private_flagged(self, tmp_path):
        source = (
            "import myproject\n"
            "\n"
            "def test_a():\n"
            "    myproject._private_helper()\n"
        )
        f = _write(tmp_path, "test_x.py", source)
        findings = _by_rule(
            validate_files([f]), "privacy.attribute-access"
        )
        assert len(findings) == 1
        assert "_private_helper" in findings[0].message

    def test_dunder_attr_allowed(self, tmp_path):
        source = (
            "import myproject\n"
            "\n"
            "def test_a():\n"
            "    myproject.__version__\n"
        )
        f = _write(tmp_path, "test_x.py", source)
        assert _by_rule(validate_files([f]), "privacy.attribute-access") == []

    def test_attribute_on_test_module_allowed(self, tmp_path):
        source = (
            "import tests.helpers\n"
            "\n"
            "def test_a():\n"
            "    tests.helpers._make_thing()\n"
        )
        f = _write(tmp_path, "test_x.py", source)
        assert _by_rule(validate_files([f]), "privacy.attribute-access") == []

    def test_local_underscore_helper_passes(self, tmp_path):
        source = (
            "def _helper():\n"
            "    return 1\n"
            "\n"
            "def test_a():\n"
            "    assert _helper() == 1\n"
        )
        f = _write(tmp_path, "test_x.py", source)
        assert validate_files([f]) == []

    def test_alias_imports_tracked(self, tmp_path):
        source = (
            "import myproject as mp\n"
            "\n"
            "def test_a():\n"
            "    mp._secret\n"
        )
        f = _write(tmp_path, "test_x.py", source)
        findings = _by_rule(validate_files([f]), "privacy.attribute-access")
        assert len(findings) == 1


# ---------------------------------------------------------------------------
# File-level error handling
# ---------------------------------------------------------------------------


class TestFileHandling:
    def test_missing_file_returns_empty(self, tmp_path):
        assert validate_files([tmp_path / "no_such.py"]) == []

    def test_syntax_error_returns_empty(self, tmp_path):
        f = _write(tmp_path, "test_x.py", "def broken(:\n")
        assert validate_files([f]) == []

    def test_multiple_files_aggregated(self, tmp_path):
        a = _write(tmp_path, "test_a.py", "from myproject import _x\n")
        b = _write(tmp_path, "test_b.py", "from myproject import _y\n")
        findings = validate_files([a, b])
        assert len(findings) == 2
