"""Pure-Python parsers for spec files.

The markdown parser produces SpecFile objects (sections + items) without the
OFT JAR. It is the parse tier shared by lint, sdd-index, sdd-atlas, and
sdd-review. Coverage, interface validation, and sdd-chain continue to use the
OFT-JAR-backed parser in ``sdd_tools.oft``.
"""
