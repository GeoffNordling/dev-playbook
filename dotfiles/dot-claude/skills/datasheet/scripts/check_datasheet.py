#!/usr/bin/env python3
"""Mechanical conformance checks for a datasheet (standards/datasheet.md).

Checks only the machine-checkable rules:
- the stamp comment opens the file and carries every required field
- the seven H2 sections appear in the standard's order
- both Behavior labels are present
- word budgets: visible layer (outside <details>, excluding the <header>
  stamp block and <style>) <= 1000; collapsed layer (inside <details>) <= 1000

Exit 0 when clean; exit 1 with one finding per line otherwise.
"""

import re
import sys
from html.parser import HTMLParser

REQUIRED_STAMP_FIELDS = ("subject", "scope", "commit", "generated", "generator")
SECTION_ORDER = (
    "Purpose",
    "Behavior",
    "Concepts",
    "Shape",
    "Touch surface",
    "Tests",
    "Assessment",
)
VISIBLE_BUDGET = 1000
COLLAPSED_BUDGET = 1000


class LayerCounter(HTMLParser):
    """Split rendered text into visible/collapsed word counts and collect H2s."""

    def __init__(self) -> None:
        super().__init__()
        self.details_depth = 0
        self.in_header = False
        self.in_style = False
        self.in_h2 = False
        self.h2s: list[str] = []
        self.visible_words = 0
        self.collapsed_words = 0
        self._h2_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag == "details":
            self.details_depth += 1
        elif tag == "header":
            self.in_header = True
        elif tag == "style":
            self.in_style = True
        elif tag == "h2":
            self.in_h2 = True
            self._h2_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "details" and self.details_depth:
            self.details_depth -= 1
        elif tag == "header":
            self.in_header = False
        elif tag == "style":
            self.in_style = False
        elif tag == "h2":
            self.in_h2 = False
            self.h2s.append(" ".join("".join(self._h2_parts).split()))

    def handle_data(self, data: str) -> None:
        if self.in_style:
            return
        if self.in_h2:
            self._h2_parts.append(data)
        words = len(data.split())
        if not words:
            return
        if self.details_depth:
            self.collapsed_words += words
        elif not self.in_header:
            self.visible_words += words


def check(text: str) -> tuple[list[str], LayerCounter]:
    """Return (findings, parser) for one datasheet's full text."""
    findings: list[str] = []

    if not text.startswith("<!--datasheet-stamp"):
        findings.append(
            "stamp: file does not open with the <!--datasheet-stamp comment"
        )
    else:
        stamp = text[: text.index("-->")]
        for field in REQUIRED_STAMP_FIELDS:
            if not re.search(rf"^{field}:", stamp, re.M):
                findings.append(f"stamp: missing field '{field}'")

    parser = LayerCounter()
    parser.feed(text)

    if len(parser.h2s) != len(SECTION_ORDER):
        findings.append(
            f"sections: expected {len(SECTION_ORDER)} H2 sections, found {len(parser.h2s)}: {parser.h2s}"
        )
    else:
        for got, want in zip(parser.h2s, SECTION_ORDER, strict=True):
            if not got.startswith(want):
                findings.append(f"sections: expected '{want}', found '{got}'")

    flat = re.sub(r"\s+", " ", text)
    if not re.search(r"verified: (run|not-run)", flat):
        findings.append("behavior: missing 'verified: run|not-run' label")
    if not re.search(r"exhibit: (captured|constructed)", flat):
        findings.append("behavior: missing 'exhibit: captured|constructed' label")

    if parser.visible_words > VISIBLE_BUDGET:
        findings.append(
            f"budget: visible layer {parser.visible_words} words > {VISIBLE_BUDGET}"
        )
    if parser.collapsed_words > COLLAPSED_BUDGET:
        findings.append(
            f"budget: collapsed layer {parser.collapsed_words} words > {COLLAPSED_BUDGET}"
        )

    return findings, parser


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: check_datasheet.py <datasheet.html>", file=sys.stderr)
        return 2
    with open(argv[1], encoding="utf-8") as f:
        text = f.read()
    findings, parser = check(text)
    for finding in findings:
        print(f"datasheet-check: {finding}")
    if findings:
        return 1
    print(
        f"datasheet-check: clean — visible {parser.visible_words} words, "
        f"collapsed {parser.collapsed_words} words"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
