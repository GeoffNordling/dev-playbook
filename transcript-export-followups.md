# Transcript Export — Follow-ups / Open Questions

Deferred from the design conversation. **None block the Ralph plan** — they are
either pre-launch checks or refinements to revisit after a first working tool.

## Must settle before launching the loop

- **Q-GATE** — Confirm `make -C tools check` passes **green on the current
  (pre-T1) tree** and the git tree is clean. The ralph-loop stops on iteration 1
  if the gate is red on entry. May require `uv sync` in `tools/`. This is the
  ralph-setup "verify loop-ready" step.

## Revisit after a first working tool

- **Q-NAMING** — Output file naming / location / idempotency. The plan assumes
  `<out_dir>/<id>.xml`; decide overwrite-vs-skip on re-run and whether sub-agent
  files are ever emitted separately (currently always nested inline).
- **Q-VIEWER** — Which XML GUI to standardize on. Browser native tree (Firefox)
  is the zero-install default; QXmlEdit handles very large files.
- **Q-NESTDEPTH** — Sub-agent nesting deeper than 1 was never observed in the
  corpus. Recursion is generic, but confirm against a real depth>1 session if one
  ever appears (and that the depth guard is set sensibly).

## Retired by the messages-only decision (kept for the record)

- **Q-EXPORT** (empty raw file handling), **Q-IMAGES** / **Q-UNKNOWNBLOCK** (raw
  content-block interpretation), **Q-FULLOUTPUT** (full tool-output capture /
  sidecar) — all dissolved: with no `export` and no raw-JSONL parsing, none of
  these conditions can arise. We consume AgentsView's parsed output and accept
  the losses listed in PLAN.md (Design).
