"""Tests for the transcript-export CLI scaffold."""

import pytest

from transcript_export.cli import main


def test_main_prints_usage_and_returns_zero(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code = main([])
    out = capsys.readouterr().out

    assert code == 0
    assert "transcript-export" in out
