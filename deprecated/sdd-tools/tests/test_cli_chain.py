"""Tests for sdd_tools.cli.chain."""

from pathlib import Path

import pytest

from sdd_tools.cli import chain as cli
from sdd_tools.models import SpecItem


def _write_pyproject(root: Path, body: str) -> None:
    (root / "pyproject.toml").write_text(body, encoding="utf-8")


def _valid_pyproject(root: Path) -> None:
    _write_pyproject(
        root,
        '[tool.pytest-sdd]\n'
        'spec_dirs = ["specs"]\n'
        'oft_jar = "oft.jar"\n',
    )
    (root / "specs").mkdir()
    (root / "oft.jar").write_bytes(b"PK")


def _item(spec_id: str, doctype: str, covers: tuple[str, ...] = ()) -> SpecItem:
    name = spec_id.split("~")[1]
    return SpecItem(
        id=spec_id,
        doctype=doctype,
        name=name,
        revision=1,
        title=name,
        status="approved",
        description="",
        rationale="",
        covers=list(covers),
        needs=[],
        source_file=Path(f"specs/{name}.md"),
        source_line=1,
    )


class TestBuildParser:
    def test_defaults_are_none(self):
        args = cli.build_parser().parse_args([])
        assert args.id_pattern is None
        assert args.doctype is None
        assert args.source_file is None
        assert args.feature is None
        assert args.root is None

    def test_flag_mapping(self):
        args = cli.build_parser().parse_args(
            [
                "--id", "*auth*",
                "--type", "dsn",
                "--file", "design",
                "--feature", "*user*",
                "--root", "/tmp/proj",
            ]
        )
        assert args.id_pattern == "*auth*"
        assert args.doctype == "dsn"
        assert args.source_file == "design"
        assert args.feature == "*user*"
        assert args.root == Path("/tmp/proj")


class TestMainErrorPaths:
    def test_no_pyproject_exits_2(self, tmp_path, capsys):
        code = cli.main(["--root", str(tmp_path)])
        assert code == 2
        assert "no [tool.pytest-sdd]" in capsys.readouterr().err

    def test_no_pytest_sdd_section_exits_2(self, tmp_path, capsys):
        _write_pyproject(tmp_path, '[project]\nname = "x"\n')
        code = cli.main(["--root", str(tmp_path)])
        assert code == 2
        assert "no [tool.pytest-sdd]" in capsys.readouterr().err

    def test_malformed_config_exits_2(self, tmp_path, capsys):
        _write_pyproject(tmp_path, '[tool.pytest-sdd]\noft_jar = "x.jar"\n')
        code = cli.main(["--root", str(tmp_path)])
        assert code == 2
        assert "spec_dirs" in capsys.readouterr().err

    def test_missing_jar_exits_2(self, tmp_path, capsys, monkeypatch):
        _valid_pyproject(tmp_path)

        def _boom(*_args, **_kwargs):
            raise FileNotFoundError("OFT JAR not found")

        monkeypatch.setattr(cli, "load_spec_items", _boom)
        code = cli.main(["--root", str(tmp_path)])
        assert code == 2
        assert "OFT JAR not found" in capsys.readouterr().err

    def test_runtime_error_exits_2(self, tmp_path, capsys, monkeypatch):
        _valid_pyproject(tmp_path)

        def _boom(*_args, **_kwargs):
            raise RuntimeError("convert failed")

        monkeypatch.setattr(cli, "load_spec_items", _boom)
        code = cli.main(["--root", str(tmp_path)])
        assert code == 2
        assert "convert failed" in capsys.readouterr().err


class TestMainSuccessPaths:
    def test_no_chains_prints_message(self, tmp_path, capsys, monkeypatch):
        _valid_pyproject(tmp_path)
        monkeypatch.setattr(cli, "load_spec_items", lambda *_a, **_k: [])
        code = cli.main(["--root", str(tmp_path)])
        captured = capsys.readouterr()
        assert code == 0
        assert "No chains found." in captured.err
        assert captured.out == ""

    def test_renders_chains_to_stdout(self, tmp_path, capsys, monkeypatch):
        _valid_pyproject(tmp_path)
        items = [
            _item("feat~auth~1", "feat"),
            _item("req~login~1", "req", covers=("feat~auth~1",)),
        ]
        monkeypatch.setattr(cli, "load_spec_items", lambda *_a, **_k: items)
        code = cli.main(["--root", str(tmp_path)])
        captured = capsys.readouterr()
        assert code == 0
        assert "Chain 1: feat~auth~1 > req~login~1" in captured.out

    def test_filter_narrows_output(self, tmp_path, capsys, monkeypatch):
        _valid_pyproject(tmp_path)
        items = [
            _item("feat~auth~1", "feat"),
            _item("feat~billing~1", "feat"),
        ]
        monkeypatch.setattr(cli, "load_spec_items", lambda *_a, **_k: items)
        code = cli.main(["--root", str(tmp_path), "--feature", "*auth*"])
        captured = capsys.readouterr()
        assert code == 0
        assert "feat~auth~1" in captured.out
        assert "feat~billing~1" not in captured.out


class TestEntrypoint:
    def test_module_main_invocable(self, tmp_path, capsys, monkeypatch):
        _valid_pyproject(tmp_path)
        monkeypatch.setattr(cli, "load_spec_items", lambda *_a, **_k: [])
        # main accepts argv list; invoking with explicit root mirrors the
        # console_script entry (sys.argv-based) but avoids global state.
        assert cli.main(["--root", str(tmp_path)]) == 0


def test_parser_help_includes_pytest_sdd(capsys):
    parser = cli.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--help"])
    assert "pytest-sdd" in capsys.readouterr().out
