"""The judgement model and the fixed judge configuration.

A judgement is a single yes/no question about one or more files, ruled on by an
LLM judge. This module owns the judgement vocabulary -- claim, evidence,
reference -- the ``Judgement`` verdict type, and the two fixed pieces of judge
configuration (``PROMPT`` and ``SCHEMA``) that the downstream layer must run the
judge under verbatim, because they are folded into the content key.
"""

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any, NamedTuple

# The general judge prompt. It is part of the content key, so editing it re-keys
# (and therefore re-runs) every judgement everywhere -- by design.
PROMPT = """\
You are a careful and fair judge. You are given a single CLAIM — a proposition
stated in prose — and you must decide whether it holds.

You are given the material to judge it against:
- EVIDENCE — the material the claim is about. This is what you are ruling on.
- REFERENCE — optional additional material you may consult for context. It is not
  itself under judgement; use it only to interpret or corroborate the evidence.

Each piece of material is delivered in its own XML tag: the claim in <claim>, each
evidence file in an <evidence> tag, and each reference file in a <reference> tag. Every
<evidence> and <reference> tag carries the file's path in a path attribute, so you can
match file names mentioned in the claim to the right material.

Decide by these rules:
1. Base your verdict only on the CLAIM, the EVIDENCE, and the REFERENCE provided. Do
   not assume facts about this material that it does not show, and do not rely on
   remembered knowledge of these specific files or systems. You may use general
   knowledge to read and interpret the material, but not to supply evidence that is
   absent.
2. Judge the substance of the claim. It holds (verdict true) when the material
   supports it on the points that matter; it does not hold (false) when the material
   contradicts it or leaves a load-bearing part of it unsupported. Do not fail a claim
   that is true in substance over trivial or immaterial gaps.
3. Judge what the material says or commits to, not how it is written. Ignore cosmetic
   or stylistic matters unless the claim is specifically about them.
4. If the claim is too ambiguous to decide, or the material provided is not enough to
   decide it, return false and explain why — prefer a clear false over a confident
   guess.

Return:
- verdict — true if the material supports the claim in substance; false if it
  contradicts the claim or leaves a material part unsupported.
- opinion — one paragraph. On a false verdict, name the specific defect and where it
  occurs (quote or cite it). On a true verdict, briefly state why the evidence
  supports the claim.

The CLAIM, EVIDENCE, and any REFERENCE follow, each in its own XML tag."""


# The structured-output contract the judge must fill: the JSON schema of Judgement.
SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "verdict": {"type": "boolean"},
        "opinion": {"type": "string"},
    },
    "required": ["verdict", "opinion"],
    "additionalProperties": False,
}


class Judgement(NamedTuple):
    """A judge's ruling on a claim: a verdict plus one paragraph of reasoning."""

    verdict: bool
    opinion: str


class Prepared(NamedTuple):
    """What prepare() hands the caching layer: a content key and the judge prompt."""

    key: str
    prompt: str


def prepare(
    claim: str,
    evidence: list[str],
    reference: list[str] | None,
    model: str,
    effort: str,
    root: str | Path,
) -> Prepared:
    """Derive the content key and the judge prompt for one judgement.

    ``evidence`` and ``reference`` are paths relative to ``root``; each is read
    exactly once, and both outputs come from that single read. ``root`` only
    locates the files -- it enters neither the key nor the prompt, so the same
    judgement under different roots yields the identical key and prompt. Raises if
    a declared path is absolute, contains a ``..`` segment, or does not resolve
    to a readable file under ``root``.
    """
    root_path = Path(root)
    evidence_files = _read_all(evidence, root_path)
    reference_files = _read_all(reference or [], root_path)
    key = _content_key(claim, model, effort, evidence_files, reference_files)
    prompt = _render_prompt(claim, evidence_files, reference_files)
    return Prepared(key=key, prompt=prompt)


class _ReadFile(NamedTuple):
    """One file read once: its canonical relpath, raw bytes, and decoded text.

    The key hashes ``data``; the prompt renders ``text``. Both come from the
    same read, so the judge rules on exactly the bytes that were fingerprinted.
    """

    relpath: str
    data: bytes
    text: str


def _read_all(paths: list[str], root: Path) -> list[_ReadFile]:
    """Read each declared path once as a sorted list of _ReadFile, validated first.

    Each declared path is canonicalized *before any file is read*, so a path that
    is absolute, contains ``..``, or is empty rejects the whole list without
    reading anything. Containment under ``root`` is then checked per file, right
    before that file is read -- a symlink whose target escapes ``root`` is
    rejected rather than followed, so its bytes never enter the key or prompt
    (though a valid earlier path may be read before a later escaping symlink is
    rejected). Canonical relpaths are de-duplicated, so a file declared twice
    (e.g. ``a.md`` and ``./a.md``) is read and keyed once. Each file's bytes must decode as
    UTF-8 (the prompt's domain); a non-decodable file is rejected at read time
    with its path named, so the key and the prompt agree on what a valid file is.
    """
    relpaths = sorted({_canonical_relpath(p) for p in paths})
    root_resolved = root.resolve()
    files: list[_ReadFile] = []
    for relpath in relpaths:
        target = root / relpath
        if not target.resolve().is_relative_to(root_resolved):
            raise ValueError(f"path escapes root via a symlink: {relpath!r}")
        data = target.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError(f"file is not valid UTF-8: {relpath!r}") from error
        files.append(_ReadFile(relpath, data, text))
    return files


def _canonical_relpath(declared: str) -> str:
    """Normalize a declared path to a canonical relative POSIX form under root.

    Collapses ``./`` and repeated slashes; raises on an absolute path, any
    ``..`` segment, or a path with no real component (``""`` or ``.``), so reads
    stay strictly under ``root`` and each file keys under exactly one path.
    """
    pure = PurePosixPath(declared)
    if pure.is_absolute():
        raise ValueError(f"path must be relative to root, got absolute: {declared!r}")
    if ".." in pure.parts:
        raise ValueError(f"path must stay under root, got '..' segment: {declared!r}")
    canonical = pure.as_posix()
    if canonical == ".":
        raise ValueError(f"path must name a file under root, got empty: {declared!r}")
    return canonical


def _content_key(
    claim: str,
    model: str,
    effort: str,
    evidence_files: list[_ReadFile],
    reference_files: list[_ReadFile],
) -> str:
    """Hex SHA-256 over a canonical, unambiguous serialization of the judgement.

    Each file contributes its canonical relpath paired with the SHA-256 of its
    raw bytes; ``root`` and absolute paths never enter. The serialization is
    canonical JSON (sorted keys); JSON string quoting plus the fixed-width hex
    digests keep the fields unambiguous, so distinct judgements cannot collide
    into a false skip.
    """
    payload = {
        "claim": claim,
        "model": model,
        "effort": effort,
        "prompt": PROMPT,
        "schema": SCHEMA,
        "evidence": [[f.relpath, _digest(f.data)] for f in evidence_files],
        "reference": [[f.relpath, _digest(f.data)] for f in reference_files],
    }
    serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _digest(data: bytes) -> str:
    """Hex SHA-256 of raw file bytes -- an unambiguous stand-in for the content."""
    return hashlib.sha256(data).hexdigest()


def _render_prompt(
    claim: str,
    evidence_files: list[_ReadFile],
    reference_files: list[_ReadFile],
) -> str:
    """Build the self-contained, XML-tagged prompt from the already-read files."""
    blocks = [_tag("instructions", PROMPT), _tag("claim", claim)]
    blocks += [_tag("evidence", f.text, f.relpath) for f in evidence_files]
    blocks += [_tag("reference", f.text, f.relpath) for f in reference_files]
    return "\n\n".join(blocks)


def _tag(name: str, content: str, path: str | None = None) -> str:
    """Wrap content in an XML tag, carrying a relative path attribute when given."""
    attribute = f' path="{path}"' if path is not None else ""
    return f"<{name}{attribute}>\n{content}\n</{name}>"
