"""OFT JAR adapter: java check, JAR resolution, trace, convert+parse.

The OFT JAR (https://github.com/itsallcode/openfasttrace) handles all
markdown parsing, coverage graph computation, and recursive directory scan.
This module is the only sdd_tools entry to the JAR.

Two operations:
    run_oft_trace   -- pass/fail coverage check; output is the JAR's report.
    load_spec_items -- run JAR convert and parse XML into SpecItem list.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from sdd_tools.models import SpecItem

_OFT_TIMEOUT_SECONDS = 120

# Interface: lines inside a description body. Captures everything after the
# colon up to end-of-line.
_INTERFACE_LINE_RE = re.compile(r"^\s*Interface:\s*(.+?)\s*$", re.MULTILINE)


def resolve_oft_jar(jar_path: Path) -> Path:
    """Validate that the OFT JAR exists at the given path."""
    if not jar_path.is_file():
        raise FileNotFoundError(
            f"OFT JAR not found: {jar_path}\n"
            "Download from https://github.com/itsallcode/openfasttrace/releases"
        )
    return jar_path


def require_java() -> str:
    """Return the path to the java executable, or raise."""
    java = shutil.which("java")
    if java is None:
        raise RuntimeError(
            "java not found on PATH; required for OFT.\n"
            "Install a JDK or JRE and ensure java is on your PATH."
        )
    return java


def run_oft_trace(
    jar_path: Path,
    input_paths: list[Path],
) -> subprocess.CompletedProcess[str]:
    """Run OFT trace across all input paths.

    Raises subprocess.CalledProcessError on non-zero exit.
    """
    java = require_java()
    resolved_jar = resolve_oft_jar(jar_path)

    cmd = [java, "-jar", str(resolved_jar), "trace"]
    for path in input_paths:
        cmd.append(str(path))

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=_OFT_TIMEOUT_SECONDS,
    )
    if result.returncode != 0:
        output = (result.stdout + result.stderr).strip()
        raise subprocess.CalledProcessError(
            result.returncode,
            result.args,
            output=output,
        )
    return result


def run_oft_convert(jar_path: Path, spec_dirs: list[Path]) -> str:
    """Run OFT convert and return the raw XML."""
    java = require_java()
    resolved_jar = resolve_oft_jar(jar_path)

    cmd = [java, "-jar", str(resolved_jar), "convert", "-s"]
    for d in spec_dirs:
        cmd.append(str(d))

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=_OFT_TIMEOUT_SECONDS,
    )
    if result.returncode != 0:
        output = (result.stdout + result.stderr).strip()
        raise RuntimeError(f"OFT convert failed (exit {result.returncode}):\n{output}")
    return result.stdout


def parse_xml(xml_text: str) -> list[SpecItem]:
    """Parse OFT convert XML into SpecItem instances."""
    root = ET.fromstring(xml_text)
    items: list[SpecItem] = []

    for specobjects in root.findall("specobjects"):
        doctype = specobjects.get("doctype", "")

        for obj in specobjects.findall("specobject"):
            name = _text(obj.find("id"))
            revision = int(_text(obj.find("version")) or "0")
            full_id = f"{doctype}~{name}~{revision}"

            needs: list[str] = []
            needs_el = obj.find("needscoverage")
            if needs_el is not None:
                for n in needs_el.findall("needsobj"):
                    if n.text:
                        needs.append(n.text.strip())

            covers: list[str] = []
            prov_el = obj.find("providescoverage")
            if prov_el is not None:
                for provcov in prov_el.findall("provcov"):
                    linksto = _text(provcov.find("linksto"))
                    dstversion = _text(provcov.find("dstversion"))
                    if linksto and dstversion:
                        # OFT writes "type:name"; convert to "type~name~revision"
                        parts = linksto.split(":", 1)
                        if len(parts) == 2:
                            covers.append(f"{parts[0]}~{parts[1]}~{dstversion}")

            description = _text(obj.find("description"))
            interfaces = (
                parse_interfaces(description) if doctype == "dsn" else []
            )

            items.append(
                SpecItem(
                    id=full_id,
                    doctype=doctype,
                    name=name,
                    revision=revision,
                    title=_text(obj.find("shortdesc")),
                    status=_text(obj.find("status")),
                    description=description,
                    rationale=_text(obj.find("rationale")),
                    covers=covers,
                    needs=needs,
                    source_file=Path(_text(obj.find("sourcefile"))),
                    source_line=int(_text(obj.find("sourceline")) or "0"),
                    interfaces=interfaces,
                )
            )

    return items


def load_spec_items(jar_path: Path, spec_dirs: list[Path]) -> list[SpecItem]:
    """Run OFT convert and parse the result into SpecItems."""
    xml_text = run_oft_convert(jar_path, spec_dirs)
    return parse_xml(xml_text)


def _text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return (element.text or "").strip()


def parse_interfaces(description: str) -> list[str]:
    """Extract Interface: signature lines from a dsn item description.

    Each line starting with `Interface:` contributes one signature.
    """
    return [m.group(1).strip() for m in _INTERFACE_LINE_RE.finditer(description)]
