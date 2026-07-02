from pathlib import Path
from xml.etree import ElementTree

FIXTURES = Path(__file__).parent.parent.parent / "fixtures"


def test_structure(run_cli, tmp_path):
    out = tmp_path / "out.xml"
    r = run_cli(str(FIXTURES / "session-small.jsonl"), "-o", str(out))
    assert r.returncode == 0
    assert r.stdout == ""  # pinned: silence
    msgs = ElementTree.parse(out).findall(".//message")
    assert len(msgs) == 14  # pinned: count
    assert msgs[0].get("role") == "user"  # pinned: order and roles
    assert "def hello" in msgs[3].findtext("content")  # pinned: fidelity


def test_byte_anchor(run_cli, tmp_path):
    out = tmp_path / "out.xml"
    run_cli(str(FIXTURES / "session-small.jsonl"), "-o", str(out))
    assert out.read_bytes() == (FIXTURES / "expected-small.xml").read_bytes()


def test_default_output_name(run_cli, tmp_path):
    r = run_cli(str(FIXTURES / "session-small.jsonl"))
    assert r.returncode == 0
    assert (tmp_path / "session-small.xml").exists()


def test_tool_calls_gated_by_flag(run_cli, tmp_path):
    out = tmp_path / "out.xml"
    run_cli(str(FIXTURES / "session-small.jsonl"), "-o", str(out))
    assert not ElementTree.parse(out).findall(".//tool-call")
    run_cli(str(FIXTURES / "session-small.jsonl"), "-o", str(out), "--include-tools")
    assert len(ElementTree.parse(out).findall(".//tool-call")) == 2


def test_malformed_input(run_cli):
    r = run_cli(str(FIXTURES / "truncated.jsonl"))
    assert r.returncode == 1
    assert "17" in r.stderr  # names the offending line
    assert r.stderr.count("\n") <= 1  # single-line diagnostic


def test_missing_file(run_cli):
    r = run_cli("nope.jsonl")
    assert r.returncode == 1
