"""TEMPORARY: the six pseudocode blocks match the reference model's one.

The doc-type system's pseudocode is split across six pages, the base in
`doc-types/doc-type.md` and one class per `contract-shape.md`, and the
reference model in the working set holds the same text whole. This test
fails when they differ. It parses nothing as Python: the pseudocode is a
picture, not code. Delete this test when
`working-docs/doc-type-system/doc-type-system/reference-model.md` is
deleted; it fails with that instruction if the file is missing.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "working-docs/doc-type-system/doc-type-system/reference-model.md"
PAGES = [
    ROOT / "doc-types/doc-type.md",
    ROOT / "doc-types/runbook/contract-shape.md",
    ROOT / "doc-types/standard/contract-shape.md",
    ROOT / "doc-types/explanation/contract-shape.md",
    ROOT / "doc-types/guide/contract-shape.md",
    ROOT / "doc-types/loop/contract-shape.md",
]
OPEN = "```python\n"
CLOSE = "\n```"


def python_blocks(text: str) -> list[str]:
    """Every ```python fence's content, in order."""
    blocks = []
    at = 0
    while (start := text.find(OPEN, at)) != -1:
        end = text.index(CLOSE, start + len(OPEN))
        blocks.append(text[start + len(OPEN) : end])
        at = end + len(CLOSE)
    return blocks


def the_one_block(path: Path, text: str) -> str:
    blocks = python_blocks(text)
    assert len(blocks) == 1, (
        f"{path.relative_to(ROOT)} holds {len(blocks)} python fences, expected 1"
    )
    return blocks[0]


def test_the_six_pages_concatenated_are_the_reference_models_block() -> None:
    assert REFERENCE.exists(), (
        f"{REFERENCE.relative_to(ROOT)} is gone: delete this test, it has no job left"
    )
    text = REFERENCE.read_text()
    language = text[text.index("### The language") : text.index("### The toolchain")]
    reference = the_one_block(REFERENCE, language)
    pages = "\n\n\n".join(the_one_block(p, p.read_text()) for p in PAGES)
    assert pages == reference
