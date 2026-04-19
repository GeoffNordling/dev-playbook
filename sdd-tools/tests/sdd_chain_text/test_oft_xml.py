"""Tests for OFT XML parsing."""

from sdd_chain_text.oft_xml import parse_xml

SAMPLE_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<specdocument>
  <specobjects doctype="req">
    <specobject>
      <id>auth.login</id>
      <shortdesc>Login Validation</shortdesc>
      <status>approved</status>
      <version>1</version>
      <sourcefile>/specs/req/auth.md</sourcefile>
      <sourceline>10</sourceline>
      <description>The system SHALL verify credentials.</description>
      <rationale>Security is important.</rationale>
      <needscoverage>
        <needsobj>dsn</needsobj>
        <needsobj>utest</needsobj>
      </needscoverage>
    </specobject>
  </specobjects>
  <specobjects doctype="dsn">
    <specobject>
      <id>auth.login</id>
      <shortdesc>Login Validator</shortdesc>
      <status>approved</status>
      <version>1</version>
      <sourcefile>/specs/dsn/auth.md</sourcefile>
      <sourceline>20</sourceline>
      <description>LoginValidator.validate() SHALL accept credentials.</description>
      <providescoverage>
        <provcov>
          <linksto>req:auth.login</linksto>
          <dstversion>1</dstversion>
        </provcov>
      </providescoverage>
      <needscoverage>
        <needsobj>utest</needsobj>
      </needscoverage>
    </specobject>
  </specobjects>
</specdocument>
"""


def test_parse_xml_basic():
    items = parse_xml(SAMPLE_XML)
    assert len(items) == 2

    req = items[0]
    assert req.full_id == "req~auth.login~1"
    assert req.doctype == "req"
    assert req.name == "auth.login"
    assert req.version == 1
    assert req.title == "Login Validation"
    assert req.status == "approved"
    assert req.description == "The system SHALL verify credentials."
    assert req.rationale == "Security is important."
    assert req.needs == ["dsn", "utest"]
    assert req.covers == []

    dsn = items[1]
    assert dsn.full_id == "dsn~auth.login~1"
    assert dsn.covers == ["req~auth.login~1"]
    assert dsn.needs == ["utest"]


def test_parse_xml_empty():
    items = parse_xml('<?xml version="1.0"?><specdocument></specdocument>')
    assert items == []
