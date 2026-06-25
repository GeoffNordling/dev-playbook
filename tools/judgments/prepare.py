"""The one entry point: turn a judgment into its content key and judge prompt.

``prepare`` reads each evidence/reference file exactly once from ``root / relpath``
and derives, from that single read, both the fingerprint ``key`` and the
self-contained, XML-tagged ``prompt``. ``root`` only locates the bytes; it never
enters the key or the prompt, so the same judgment keyed from any checkout or
worktree produces the identical key.
"""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from judgments import config

# Files read from disk: (canonical relative path, raw bytes), one per evidence/reference.
type Files = list[tuple[str, bytes]]


@dataclass(frozen=True)
class Prepared:
    """The two outputs of ``prepare``: the content fingerprint and the judge prompt."""

    key: str
    prompt: str


def _canonical(relpath: str) -> str:
    """Normalize a declared relative path to a canonical POSIX form."""
    return PurePosixPath(relpath).as_posix()


def _read_each(root: str, relpaths: list[str]) -> Files:
    """Read each file once, returning ``(canonical relpath, raw bytes)`` sorted by path.

    Raises if any path does not resolve to a readable file under ``root`` — a missing
    or unreadable file is a fail-loud error, never treated as empty.
    """
    pairs = [(_canonical(p), (Path(root) / p).read_bytes()) for p in relpaths]
    pairs.sort(key=lambda pair: pair[0])
    return pairs


def _key(claim: str, evidence: Files, reference: Files) -> str:
    """Hash an unambiguous, canonical JSON serialization of the judgment's inputs."""
    payload = {
        "claim": claim,
        "evidence": [[relpath, data.hex()] for relpath, data in evidence],
        "reference": [[relpath, data.hex()] for relpath, data in reference],
    }
    serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _tag(name: str, body: str, path: str | None = None) -> str:
    """Wrap body in an XML tag, the open and close tags on their own lines."""
    attr = f' path="{path}"' if path is not None else ""
    return f"<{name}{attr}>\n{body}\n</{name}>"


def _render(claim: str, evidence: Files, reference: Files) -> str:
    """Build the self-contained, XML-tagged prompt from the already-read bytes."""
    blocks = [_tag("instructions", config.PROMPT), _tag("claim", claim)]
    blocks += [_tag("evidence", data.decode("utf-8"), path) for path, data in evidence]
    blocks += [
        _tag("reference", data.decode("utf-8"), path) for path, data in reference
    ]
    return "\n\n".join(blocks)


def prepare(
    claim: str,
    evidence: list[str],
    reference: list[str] | None,
    model: str,
    effort: str,
    root: str,
) -> Prepared:
    """Read each file once from ``root`` and derive the key and prompt together."""
    evidence_pairs = _read_each(root, evidence)
    reference_pairs = _read_each(root, reference or [])
    return Prepared(
        key=_key(claim, evidence_pairs, reference_pairs),
        prompt=_render(claim, evidence_pairs, reference_pairs),
    )
