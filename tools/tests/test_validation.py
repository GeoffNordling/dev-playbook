"""Tests for sdd_trace.validation — spec-linting functions."""

from pathlib import Path

from sdd_trace.models import FunctionalReq
from sdd_trace.validation import validate_obligations, validate_req_ids


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


# ---------------------------------------------------------------------------
# validate_req_ids (operates on files)
# ---------------------------------------------------------------------------


class TestValidateReqIds:
    def test_clean_file(self, tmp_path: Path) -> None:
        _write(tmp_path / "reqs.md", "- REQ-AUT-001: Login\n- REQ-ERR-002: Error\n")
        errors = validate_req_ids([tmp_path / "reqs.md"])
        assert errors == []

    def test_clean_file_long_area(self, tmp_path: Path) -> None:
        _write(tmp_path / "reqs.md", "- REQ-TRANS-001: OK\n- REQ-ABCDEF-001: OK\n")
        errors = validate_req_ids([tmp_path / "reqs.md"])
        assert errors == []

    def test_catches_seven_letter_area(self, tmp_path: Path) -> None:
        _write(tmp_path / "reqs.md", "- REQ-ABCDEFG-001: Bad\n")
        errors = validate_req_ids([tmp_path / "reqs.md"])
        assert len(errors) == 1
        assert "REQ-ABCDEFG-001" in errors[0]
        assert "7 letters" in errors[0]

    def test_catches_two_letter_area(self, tmp_path: Path) -> None:
        _write(tmp_path / "reqs.md", "- REQ-AB-001: Bad\n")
        errors = validate_req_ids([tmp_path / "reqs.md"])
        assert len(errors) == 1
        assert "REQ-AB-001" in errors[0]
        assert "2 letters" in errors[0]

    def test_catches_no_prefix(self, tmp_path: Path) -> None:
        _write(tmp_path / "reqs.md", "- ERR-001: Bad\n")
        errors = validate_req_ids([tmp_path / "reqs.md"])
        assert len(errors) == 1
        assert "ERR-001" in errors[0]
        assert "missing REQ- prefix" in errors[0]

    def test_catches_no_prefix_long_area(self, tmp_path: Path) -> None:
        _write(tmp_path / "reqs.md", "- TRANS-001: Bad\n")
        errors = validate_req_ids([tmp_path / "reqs.md"])
        assert len(errors) == 1
        assert "TRANS-001" in errors[0]
        assert "missing REQ- prefix" in errors[0]

    def test_no_prefix_not_triggered_by_valid_id(self, tmp_path: Path) -> None:
        _write(tmp_path / "reqs.md", "- REQ-ERR-001: Good\n")
        errors = validate_req_ids([tmp_path / "reqs.md"])
        assert errors == []


# ---------------------------------------------------------------------------
# validate_obligations (operates on parsed FunctionalReq dict)
# ---------------------------------------------------------------------------


def _req(
    obligation: str = "SHALL",
    all_obligations: frozenset[str] | None = None,
    source: str = "reqs.md",
) -> FunctionalReq:
    if all_obligations is None:
        all_obligations = frozenset({obligation}) if obligation else frozenset()
    return FunctionalReq(
        sources=[source], obligation=obligation, all_obligations=all_obligations
    )


class TestValidateObligations:
    def test_clean(self) -> None:
        func_reqs = {
            "REQ-AUT-001": _req("SHALL"),
            "REQ-AUT-002": _req("MAY"),
        }
        errors = validate_obligations(func_reqs)
        assert errors == []

    def test_missing_obligation(self) -> None:
        func_reqs = {
            "REQ-AUT-001": _req("", all_obligations=frozenset()),
        }
        errors = validate_obligations(func_reqs)
        assert len(errors) == 1
        assert "REQ-AUT-001" in errors[0]
        assert "no backtick-wrapped" in errors[0]

    def test_mixed_obligations(self) -> None:
        func_reqs = {
            "REQ-AUT-001": _req("", all_obligations=frozenset({"SHALL", "MAY"})),
        }
        errors = validate_obligations(func_reqs)
        assert len(errors) == 1
        assert "REQ-AUT-001" in errors[0]
        assert "mixed" in errors[0]

    def test_repeated_same_keyword_is_valid(self) -> None:
        func_reqs = {
            "REQ-AUT-001": _req("SHALL", all_obligations=frozenset({"SHALL"})),
        }
        errors = validate_obligations(func_reqs)
        assert errors == []

    def test_source_file_in_error_message(self) -> None:
        func_reqs = {
            "REQ-AUT-001": _req(
                "", all_obligations=frozenset(), source="specs/auth.md"
            ),
        }
        errors = validate_obligations(func_reqs)
        assert "auth.md" in errors[0]
