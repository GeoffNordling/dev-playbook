"""Parse requirement data from spec files and test markers from test files.

Pure data extraction — no validation logic.  Validation lives in
``sdd_trace.validation``.
"""

from pathlib import Path

from sdd_trace.models import (
    DEFINITION_SITE_PATTERN,
    MARKER_PATTERN,
    MULTI_MARKER_PATTERN,
    OBLIGATION_PATTERN,
    REQ_ID_PATTERN,
    STRING_IN_LIST,
    FunctionalReq,
    extract_text_block,
    text_block_boundaries,
)


def parse_functional_reqs(files: list[Path]) -> dict[str, FunctionalReq]:
    """Parse definition sites from functional spec files.

    Returns {req_id: FunctionalReq} with obligation extracted from backtick-wrapped
    keywords.  Only definition sites (**REQ-XXX-NNN**:) are parsed; bare references
    are ignored.

    Populates ``all_obligations`` with every distinct obligation keyword found in
    the text block, and ``obligation`` with the single keyword when exactly one
    exists.
    """
    result: dict[str, FunctionalReq] = {}
    for f in files:
        text = f.read_text()
        file_str = str(f)
        boundaries = text_block_boundaries(text)
        for match in DEFINITION_SITE_PATTERN.finditer(text):
            req_id = match.group(1)
            block = extract_text_block(text, match.start(), boundaries)
            keywords = frozenset(m.group(1) for m in OBLIGATION_PATTERN.finditer(block))
            obligation = next(iter(keywords)) if len(keywords) == 1 else ""
            if req_id in result:
                result[req_id].sources.append(file_str)
            else:
                result[req_id] = FunctionalReq(
                    sources=[file_str],
                    obligation=obligation,
                    all_obligations=keywords,
                )
    return result


def parse_design_refs(files: list[Path]) -> dict[str, list[str]]:
    """Extract REQ-XXX-NNN IDs from design spec files. Returns {id: [source_files]}.

    Finds all bare references — no definition-site formatting required.
    """
    refs: dict[str, list[str]] = {}
    for f in files:
        text = f.read_text()
        file_str = str(f)
        for match in REQ_ID_PATTERN.finditer(text):
            refs.setdefault(match.group(), []).append(file_str)
    return refs


def parse_test_markers(tests_dir: Path) -> dict[str, list[str]]:
    """Parse @pytest.mark.req markers from test files. Returns {req_id: [test_files]}."""
    markers: dict[str, list[str]] = {}
    for f in tests_dir.rglob("*.py"):
        text = f.read_text()
        file_str = str(f)
        for match in MARKER_PATTERN.finditer(text):
            markers.setdefault(match.group(1), []).append(file_str)
        for match in MULTI_MARKER_PATTERN.finditer(text):
            for string_match in STRING_IN_LIST.finditer(match.group(1)):
                markers.setdefault(string_match.group(1), []).append(file_str)
    return markers
