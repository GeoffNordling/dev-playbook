---
type: README
title: Fixtures
description: What the acceptance suite expects from the per-box fixture files
---

# Fixtures

Real fixtures are authored per box, before sealing; this template lists what
the acceptance suite expects:

- `session-small.jsonl` — a real 14-message session containing a Python code
  block (`def hello`) and exactly two tool calls.
- `truncated.jsonl` — valid until line 17, then cut mid-record.
- `expected-small.xml` — the byte-exact anchor: `session-small.jsonl` exported
  with default flags. Exists to catch drift, not to pin style; structure
  assertions in the acceptance suite carry the main load.
