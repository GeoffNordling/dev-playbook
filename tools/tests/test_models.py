"""Tests for sdd_trace.models — shared types and helpers."""

from pathlib import Path

from sdd_trace.models import FunctionalReq, extract_area_code, find_md_files


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


# ---------------------------------------------------------------------------
# FunctionalReq
# ---------------------------------------------------------------------------


class TestFunctionalReq:
    def test_shall_is_mandatory(self) -> None:
        req = FunctionalReq(sources=["f.md"], obligation="SHALL")
        assert req.mandatory is True

    def test_shall_not_is_mandatory(self) -> None:
        req = FunctionalReq(sources=["f.md"], obligation="SHALL NOT")
        assert req.mandatory is True

    def test_should_is_not_mandatory(self) -> None:
        req = FunctionalReq(sources=["f.md"], obligation="SHOULD")
        assert req.mandatory is False

    def test_should_not_is_not_mandatory(self) -> None:
        req = FunctionalReq(sources=["f.md"], obligation="SHOULD NOT")
        assert req.mandatory is False

    def test_may_is_not_mandatory(self) -> None:
        req = FunctionalReq(sources=["f.md"], obligation="MAY")
        assert req.mandatory is False

    def test_all_obligations_default_empty(self) -> None:
        req = FunctionalReq(sources=["f.md"])
        assert req.all_obligations == frozenset()

    def test_all_obligations_stored(self) -> None:
        req = FunctionalReq(
            sources=["f.md"],
            obligation="SHALL",
            all_obligations=frozenset({"SHALL"}),
        )
        assert req.all_obligations == frozenset({"SHALL"})


# ---------------------------------------------------------------------------
# extract_area_code
# ---------------------------------------------------------------------------


class TestExtractAreaCode:
    def test_basic(self) -> None:
        assert extract_area_code("REQ-ERR-001") == "ERR"

    def test_different_area(self) -> None:
        assert extract_area_code("REQ-AQD-042") == "AQD"

    def test_long_area(self) -> None:
        assert extract_area_code("REQ-TRANS-001") == "TRANS"


# ---------------------------------------------------------------------------
# find_md_files
# ---------------------------------------------------------------------------


class TestFindMdFiles:
    def test_single_file(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        _write(specs / "design.md", "content\n")
        files = find_md_files(specs, "design")
        assert len(files) == 1
        assert files[0].name == "design.md"

    def test_split_dir_with_index(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        split = specs / "design"
        _write(split / "index.md", "index\n")
        _write(split / "auth.md", "auth\n")
        files = find_md_files(specs, "design")
        assert len(files) == 2

    def test_split_dir_without_index_raises(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        split = specs / "design"
        _write(split / "auth.md", "auth\n")
        import pytest

        with pytest.raises(FileNotFoundError, match="index.md"):
            find_md_files(specs, "design")

    def test_no_structure_returns_empty(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        specs.mkdir()
        files = find_md_files(specs, "design")
        assert files == []

    def test_split_dir_takes_precedence(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        _write(specs / "design.md", "flat\n")
        split = specs / "design"
        _write(split / "index.md", "index\n")
        _write(split / "auth.md", "auth\n")
        files = find_md_files(specs, "design")
        names = {f.name for f in files}
        assert "index.md" in names
        assert "design.md" not in names
