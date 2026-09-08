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
- Task 3 done: `words` is gone from both node shapes in `kinds/index_tree.py`,
  from the payload in `kinds/markdown_file.py`, from both schemas
  (`kind_version` still 1), and from `IndexTree.tsx` and `MarkdownFile.tsx`;
  `Row`'s `count` became optional so the `Unindexed` row keeps its `N files`.
  Both module docstrings say what replaced the count: size is a kind of its
  own, per `registry.md`. Tests: the two summed-word tests in
  `kinds/test_index_tree.py` are deleted (1297 → 1295) and every other word
  assertion dropped; `test_watch.py` now polls `source_of` and asserts the
  refreshed source ends with the appended line; `test_cli.py` waits for
  `nine ten` in the panel body instead of a count of 20. `make web` rebuilt,
  gate green. Next: task 4, the two groups by `md.classify`.
- Task 4 done: `kinds/index_tree.py` drops every `md.classify` `excluded` path
  before the walk and splits the leftovers into `unindexed` (concept and index)
  and a new `harness` list, all three required in
  `schemas/index-tree.schema.json` (`kind_version` still 1);
  `kinds/markdown_file.py` skips an `excluded` file so it gets no view.
  `IndexTree.tsx` now opens with two group rows, `Concept documents` (holding
  the root hierarchy and, only when it is non-empty, a collapsed red
  `Not indexed` row) and `Harness-owned files` with its `N files`; `Row` builds
  its classes from `group`/`bad`/`missing` booleans and `app.css` gained
  `.tree-group` and `.tree-row-bad .tree-title`. The fixture gained `CLAUDE.md`
  and `PLAN.md`. Three plan slips for the user: the plan did not name
  `test_server.py::test_the_file_list_holds_every_view_file`, which lists view
  paths and needed `markdown-file/CLAUDE.md.json`; nor
  `test_refresh.py`'s `bad_payload_generate`, whose stand-in payload needed
  `"harness": []` so its deliberate failure stays `$.root` rather than a
  missing-key error at `$`; and `CLAUDE.md` sorts before `alpha.md`, so it
  heads every sorted list rather than trailing it. `make web` rebuilt, gate
  green, 1297 tests. Next: task 5, levels told apart by eye.
- Task 5 done: `IndexTree.tsx` dropped `INDENT_PX`, `depth`, and the inline
  `paddingLeft`; every open row — both group rows, every directory, and the
  `Not indexed` row — now wraps its children in one
  `<div className="tree-children">`, and `app.css` gives that box the 10px
  margin, 6px padding and the `var(--line)` guide line, with
  `.tree-row-directory` at `font-weight: 600`. `--line` already existed at
  `#d8d8d8`. One plan slip for the user: the plan set the weight on the whole
  row, which made the description bold too, so a second rule,
  `.tree-row-directory .tree-description { font-weight: 400 }`, keeps the
  heavier setting on the title. Seen on screen, two Playwright screenshots
  from the scratchpad against servers on free ports with their own
  `XDG_STATE_HOME`: on this checkout, four nested guide lines stepping right
  through `Concept documents` → root → `doc-types/` → `doc-types/runbook/`,
  the two group headers small uppercase muted, directory titles bold and file
  titles normal; this checkout has no unindexed document, so the red row was
  confirmed on a fixture checkout instead, where `Not indexed` computes to
  `rgb(179, 38, 30)`, the `--bad` red, over its one `orphan.md` child.
  `make web` rebuilt, gate green, 1297 tests. Next: task 6, discovery.
