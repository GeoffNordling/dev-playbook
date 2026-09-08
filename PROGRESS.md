# Progress log

The running memory of this Ralph loop. Each iteration appends one line below —
what it did and what is next — newest at the bottom. A fresh agent reads this
before starting, to see what earlier iterations did.

Loop 1 (the vertical slice, 13 tasks) finished at commit `2f1d7dd`; its log is
in git history there. This file starts over for loop 2, the room.

- Task 1 done: `md.RECORDS_DIR`, `md.RECORD_NAME`, and `md.is_decision_record`
  added to `src/dev_playbook/md.py` with three cases in
  `tests/dev_playbook/test_md.py`; `scripts/ref-lint` now reads them and
  dropped its private constants and its `re` import. `uv run scripts/ref-lint`
  says `767 references, all ok` both before and after. Gate green, 1295 tests.
  Next: task 2, the `decision-record` link status in `kinds/markdown_file.py`.
- Task 2 done: `_link` in `kinds/markdown_file.py` now answers
  `decision-record` — not `broken` — for an unresolved target of a file
  `md.is_decision_record` accepts, keeping the resolved identity; the status
  enum and its description grew in `schemas/markdown-file.schema.json`
  (`kind_version` still 1) and `LinkStatus` in `MarkdownFile.tsx`, which needs
  no CSS because `.badge` is already neutral. The fixture gained
  `docs/decisions/index.md` and `docs/decisions/0001-alpha.md` and a listing
  line in `docs/index.md`, so `markdown-file` writes 7 views. Two plan slips
  for the user: `docs/`'s third child identity is `docs/decisions/`, not
  `decisions/` (a directory node carries its full path), and the fixture's
  word sums had to move with it (`docs/` 43, root 85) to keep the gate green
  until task 3 deletes them. `make web` rebuilt, gate green, 1297 tests.
  Next: task 3, removing word counts everywhere.
