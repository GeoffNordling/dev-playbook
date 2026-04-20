"""Tests for sdd_tools.oft."""

from pathlib import Path

from sdd_tools.oft import _parse_interfaces, parse_xml


def _xml(specobjects: str) -> str:
    return f'<specdocument>{specobjects}</specdocument>'


class TestParseXml:
    def test_minimal_item(self):
        xml = _xml(
            '<specobjects doctype="req">'
            "<specobject>"
            "<id>area.x</id>"
            "<version>1</version>"
            "<shortdesc>X</shortdesc>"
            "<status>approved</status>"
            "<sourcefile>specs/x.md</sourcefile>"
            "<sourceline>10</sourceline>"
            "<description>The system shall do X.</description>"
            "<rationale></rationale>"
            "</specobject>"
            "</specobjects>"
        )
        items = parse_xml(xml)
        assert len(items) == 1
        item = items[0]
        assert item.id == "req~area.x~1"
        assert item.doctype == "req"
        assert item.name == "area.x"
        assert item.revision == 1
        assert item.title == "X"
        assert item.status == "approved"
        assert item.source_file == Path("specs/x.md")
        assert item.source_line == 10
        assert item.description == "The system shall do X."
        assert item.rationale == ""
        assert item.needs == []
        assert item.covers == []
        assert item.interfaces == []

    def test_needs_and_covers(self):
        xml = _xml(
            '<specobjects doctype="dsn">'
            "<specobject>"
            "<id>m.fn</id>"
            "<version>2</version>"
            "<shortdesc>Fn</shortdesc>"
            "<status>approved</status>"
            "<sourcefile>specs/d.md</sourcefile>"
            "<sourceline>5</sourceline>"
            "<description>desc</description>"
            "<rationale>why</rationale>"
            "<needscoverage><needsobj>utest</needsobj></needscoverage>"
            "<providescoverage>"
            "<provcov><linksto>req:area.x</linksto><dstversion>1</dstversion></provcov>"
            "</providescoverage>"
            "</specobject>"
            "</specobjects>"
        )
        items = parse_xml(xml)
        assert items[0].needs == ["utest"]
        assert items[0].covers == ["req~area.x~1"]
        assert items[0].rationale == "why"

    def test_dsn_interface_extracted(self):
        description = (
            "The parser exposes one entry point.\n"
            "\n"
            "Interface: parser.parse_session(path: pathlib.Path) -> parser.Session\n"
            "Interface: parser.SessionParser.parse(self) -> parser.Session\n"
        )
        xml = _xml(
            '<specobjects doctype="dsn">'
            "<specobject>"
            "<id>m.parser</id>"
            "<version>1</version>"
            "<shortdesc>Parser</shortdesc>"
            "<status>approved</status>"
            "<sourcefile>d.md</sourcefile>"
            "<sourceline>1</sourceline>"
            f"<description>{description}</description>"
            "<rationale></rationale>"
            "</specobject>"
            "</specobjects>"
        )
        items = parse_xml(xml)
        assert items[0].interfaces == [
            "parser.parse_session(path: pathlib.Path) -> parser.Session",
            "parser.SessionParser.parse(self) -> parser.Session",
        ]

    def test_non_dsn_does_not_parse_interface(self):
        description = (
            "Body.\n"
            "Interface: this.is(ignored: str) -> None\n"
        )
        xml = _xml(
            '<specobjects doctype="req">'
            "<specobject>"
            "<id>area.r</id>"
            "<version>1</version>"
            "<shortdesc>R</shortdesc>"
            "<status>approved</status>"
            "<sourcefile>r.md</sourcefile>"
            "<sourceline>1</sourceline>"
            f"<description>{description}</description>"
            "<rationale></rationale>"
            "</specobject>"
            "</specobjects>"
        )
        items = parse_xml(xml)
        assert items[0].interfaces == []


class TestParseInterfaces:
    def test_single_line(self):
        body = "Interface: foo.bar(x: int) -> None\n"
        assert _parse_interfaces(body) == ["foo.bar(x: int) -> None"]

    def test_indented_line(self):
        body = "    Interface: foo.bar(x: int) -> None\n"
        assert _parse_interfaces(body) == ["foo.bar(x: int) -> None"]

    def test_multiple(self):
        body = (
            "Interface: m.A.__init__(self, x: int) -> None\n"
            "Interface: m.A.run(self) -> None\n"
        )
        assert _parse_interfaces(body) == [
            "m.A.__init__(self, x: int) -> None",
            "m.A.run(self) -> None",
        ]

    def test_no_interface_returns_empty(self):
        assert _parse_interfaces("Just prose, no Interface line.\n") == []
