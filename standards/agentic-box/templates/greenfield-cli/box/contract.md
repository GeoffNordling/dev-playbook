---
type: Box Artifact
title: "Contract: sessionxml"
description: The sessionxml CLI's external surface — usage, exit codes, output shape, pinned and unpinned behavior
---

# Contract

NAME

    sessionxml — export a Claude Code session transcript (.jsonl) to XML

USAGE

    sessionxml FILE.jsonl [-o OUT.xml] [--include-tools]

BEHAVIOR

    Reads exactly one session file. Writes XML to OUT
    (default: input filename with .xml extension, in cwd).
    stdout: silent on success.
    stderr: single-line diagnostics only.

EXIT CODES

    0  success
    1  input missing, unreadable, or malformed
       (report the offending line number when one exists)
    2  internal error (a bug in sessionxml)

OUTPUT SHAPE

    <session id="..." model="...">
      <message role="user|assistant" ts="ISO8601">
        <content>...</content>
        <tool-call name="...">...</tool-call>   <!-- only if --include-tools -->
      </message>
    </session>

PINNED (bug if violated)

    message count and order; roles; content text fidelity
    (code blocks, unicode, whitespace inside content survive exactly);
    exit codes; stdout silence

UNPINNED (your choice, record in DEVIATIONS.md if notable)

    inter-element whitespace; attribute order; additional attributes;
    element names not listed above; encoding declaration
