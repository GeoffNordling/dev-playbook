"""Tests for pytest_sdd.trace — OFT JAR resolution and subprocess invocation."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from pytest_sdd.trace import require_java, resolve_oft_jar, run_oft_trace


class TestResolveOftJar:
    def test_existing_jar_returned(self, tmp_path):
        jar = tmp_path / "oft.jar"
        jar.write_bytes(b"PK")  # minimal "jar" content
        result = resolve_oft_jar(jar)
        assert result == jar

    def test_missing_jar_raises(self, tmp_path):
        jar = tmp_path / "nonexistent.jar"
        with pytest.raises(FileNotFoundError, match="OFT JAR not found"):
            resolve_oft_jar(jar)

    def test_error_message_contains_path(self, tmp_path):
        jar = tmp_path / "tools" / "oft.jar"
        with pytest.raises(FileNotFoundError) as exc_info:
            resolve_oft_jar(jar)
        assert str(jar) in str(exc_info.value)


class TestRequireJava:
    def test_java_found_returns_path(self):
        with patch("shutil.which", return_value="/usr/bin/java"):
            result = require_java()
        assert result == "/usr/bin/java"

    def test_java_not_found_raises(self):
        with patch("shutil.which", return_value=None), pytest.raises(RuntimeError, match="java not found"):
            require_java()


class TestRunOftTrace:
    def test_success_returns_result(self, tmp_path):
        jar = tmp_path / "oft.jar"
        jar.write_bytes(b"PK")
        specs = tmp_path / "specs"
        specs.mkdir()

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "ok\n"
        mock_result.stderr = ""

        with patch("shutil.which", return_value="/usr/bin/java"), \
             patch("subprocess.run", return_value=mock_result) as mock_run:
            result = run_oft_trace(jar, specs)

        assert result.returncode == 0
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "/usr/bin/java" in args
        assert str(jar) in args
        assert "trace" in args
        assert str(specs) in args

    def test_oft_failure_raises_called_process_error(self, tmp_path):
        jar = tmp_path / "oft.jar"
        jar.write_bytes(b"PK")
        specs = tmp_path / "specs"
        specs.mkdir()

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "FAILED: missing coverage\n"
        mock_result.stderr = ""

        with patch("shutil.which", return_value="/usr/bin/java"), \
             patch("subprocess.run", return_value=mock_result), \
             pytest.raises(subprocess.CalledProcessError):
            run_oft_trace(jar, specs)

    def test_java_not_found_raises(self, tmp_path):
        jar = tmp_path / "oft.jar"
        jar.write_bytes(b"PK")

        with patch("shutil.which", return_value=None), pytest.raises(RuntimeError, match="java not found"):
            run_oft_trace(jar, tmp_path)

    def test_missing_jar_raises_before_subprocess(self, tmp_path):
        jar = tmp_path / "missing.jar"
        with patch("shutil.which", return_value="/usr/bin/java"), \
             patch("subprocess.run") as mock_run, pytest.raises(FileNotFoundError):
            run_oft_trace(jar, tmp_path)
        mock_run.assert_not_called()
