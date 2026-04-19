"""Parse OFT XML output into structured spec items.

Runs the OFT JAR's ``convert`` command to produce XML, then parses it
into a flat list of SpecItem dataclasses. OFT handles all markdown parsing;
this module only deals with XML.
"""

from __future__ import annotations

import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

from pytest_sdd.trace import require_java, resolve_oft_jar


@dataclass
class SpecItem:
    """A single OFT specification item extracted from XML."""

    full_id: str  # "req~meta.cc-version~1"
    doctype: str  # "req"
    name: str  # "meta.cc-version"
    version: int  # 1
    title: str  # from <shortdesc>
    status: str
    source_file: str
    source_line: int
    description: str
    rationale: str
    needs: list[str] = field(default_factory=list)  # downstream types needed
    covers: list[str] = field(default_factory=list)  # upstream full IDs covered


def run_oft_convert(jar_path: Path, spec_dirs: list[Path]) -> str:
    """Run OFT convert and return the raw XML string."""
    java = require_java()
    resolved_jar = resolve_oft_jar(jar_path)

    cmd = [java, "-jar", str(resolved_jar), "convert", "-s"]
    for d in spec_dirs:
        cmd.append(str(d))

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        output = (result.stdout + result.stderr).strip()
        raise RuntimeError(f"OFT convert failed (exit {result.returncode}):\n{output}")

    return result.stdout


def _text(element: ET.Element | None) -> str:
    """Extract text from an XML element, returning '' if absent."""
    if element is None:
        return ""
    return (element.text or "").strip()


def parse_xml(xml_text: str) -> list[SpecItem]:
    """Parse OFT XML output into a list of SpecItem."""
    root = ET.fromstring(xml_text)
    items: list[SpecItem] = []

    for specobjects in root.findall("specobjects"):
        doctype = specobjects.get("doctype", "")

        for obj in specobjects.findall("specobject"):
            name = _text(obj.find("id"))
            version = int(_text(obj.find("version")) or "0")
            full_id = f"{doctype}~{name}~{version}"

            # Parse needs
            needs: list[str] = []
            needs_el = obj.find("needscoverage")
            if needs_el is not None:
                for n in needs_el.findall("needsobj"):
                    if n.text:
                        needs.append(n.text.strip())

            # Parse covers (upstream references)
            covers: list[str] = []
            prov_el = obj.find("providescoverage")
            if prov_el is not None:
                for provcov in prov_el.findall("provcov"):
                    linksto = _text(provcov.find("linksto"))
                    dstversion = _text(provcov.find("dstversion"))
                    if linksto and dstversion:
                        # linksto is "type:name", convert to "type~name~version"
                        parts = linksto.split(":", 1)
                        if len(parts) == 2:
                            covers.append(f"{parts[0]}~{parts[1]}~{dstversion}")

            items.append(
                SpecItem(
                    full_id=full_id,
                    doctype=doctype,
                    name=name,
                    version=version,
                    title=_text(obj.find("shortdesc")),
                    status=_text(obj.find("status")),
                    source_file=_text(obj.find("sourcefile")),
                    source_line=int(_text(obj.find("sourceline")) or "0"),
                    description=_text(obj.find("description")),
                    rationale=_text(obj.find("rationale")),
                    needs=needs,
                    covers=covers,
                )
            )

    return items


def load_spec_items(jar_path: Path, spec_dirs: list[Path]) -> list[SpecItem]:
    """Run OFT convert and parse the result into SpecItems."""
    xml_text = run_oft_convert(jar_path, spec_dirs)
    return parse_xml(xml_text)
