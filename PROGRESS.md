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
- Task 6 done: `src/dev_playbook/cloa_viewer/discover.py` holds `is_checkout`
  (the `.git` marker exists, directory or file alike), `worktrees` (the
  `worktree <path>` line of every `git worktree list --porcelain` block that
  carries no `bare` or `prunable` line, resolved, main checkout first), and
  `checkouts` (a checkout source is itself; any other source scans its
  immediate child directories in name order, `ValueError` when none yields a
  checkout; deduplicated with `dict.fromkeys`). `tests/cloa_viewer_fixtures.py`
  gained `add_worktree(checkout, name)` and a `.gitignore` holding
  `.claude/worktrees/`, its tenth file — not markdown, so no view-file count
  moved and no existing test needed touching. Five tests in
  `tests/dev_playbook/cloa_viewer/test_discover.py` over three chained
  fixtures (`ws`, `main`, `wt`), because `testing-lint` forbids logic in a test
  body. One note for the user, not a plan slip: `checkouts` returns a checkout
  source unresolved and a `worktrees` path resolved, so task 7's callers must
  resolve their sources first — `cli.main` already does. Gate green, 1302
  tests. Next: task 7, the server discovers and the command scans.
- Task 7 done: `server.build_app(sources, dist)` now keeps the paths the
  command was given, and `server.rescan(app)` turns them into checkouts again
  in `_lifespan` and on every `GET /api/checkouts` — refreshing and watching a
  checkout that appeared, and stopping the watcher and `shutil.rmtree`ing the
  state directory of one that vanished. `watch.watch_filter(ignore)` builds the
  watcher's filter so a worktree inside a checkout is the outer watcher's
  business no longer. `cli`'s positional is `path`, `cli.default_source()`
  falls back to `Path.cwd()` when `git rev-parse` fails, and a source yielding
  no checkout prints `<path>: no checkout found` and returns 2. Four plan
  slips for the user. (1) `build_app` cannot fill `app.state.checkouts`
  eagerly any more — `rescan` diffs against it, so a pre-filled list would
  start no watchers at all — which means a `TestClient` without `with` now
  404s every checkout route, so `test_server.py`'s `client` fixture became a
  `with TestClient(...)` generator and every route test runs the lifespan.
  (2) Renaming the positional moved two parse tests the plan did not name,
  `test_checkout_arguments_collect_into_a_list` and
  `test_no_checkout_argument_is_an_empty_list`. (3) The plan's removal test
  says the list holds two afterwards; as an independent test with its own
  fixtures it holds one, `main` alone, and it is two tests because the list and
  the state directory are two observations. (4) `refresh.json`'s `finished` is
  a whole-second timestamp and cannot tell "did not refresh" from "refreshed
  twice in one second", so the ignore test polls the record's `st_mtime_ns`;
  proved by mutation — with `ignore=[]` it fails. Gate green, 1311 tests.
  Next: task 8, the toggle on the page.
- Task 8 done: `store.ts` keeps the open panels per checkout (`panels`, a
  `Map<dir, readonly string[]>`; `Viewer.open` is the current one's entry) and
  no longer clears them on a switch, `selectCheckout(dir)` sets the selection
  and writes `window.location.hash`, the load effect reads that hash back
  through the new `byDir` (match, else first, else null), and a `refreshed`
  event for any checkout now refetches the checkout list and replaces the
  selected object, so a branch change shows and a vanished checkout falls back
  to the first. `TopBar.tsx` has a `<select className="topbar-checkout">` with
  one `<optgroup>` per repo in list order and one `<option value={dir}
  title={path}>{branch}</option>` per checkout; `app.css` gives it `.button`'s
  box (padding `1px 6px` — `2px` made it 27px against the button's 25px) and
  `.topbar-none` styles the "no checkout" text that stands in before the first
  answer. Three Playwright tests in `test_cli.py` over a new `workspace` /
  `in_workspace` / `worktree` / `workspace_address` fixture chain, on the `ws`
  directory holding the fixture checkout and a `wt` worktree; the old `address`
  fixture and the new one now share one `serving()` contextmanager. Two notes,
  not plan slips: an `<option>` is never "visible" to Playwright (wait with
  `state="attached"`), and "the tree still shows Alpha" proves nothing because
  both checkouts hold `alpha.md`, so the worktree fixture writes an extra
  `only-here.md` and the test reads the `Not indexed` row's count going 1 → 2,
  then clicks it open for the title. Proved by mutation twice: the option count
  and the hash read. Seen on screen — the toggle reads `main`, switches to `wt`,
  and the tree redraws under it. `make web` rebuilt, gate green, 1314 tests.
  Next: task 9, the smoke run on dev-playbook's checkouts.
- Task 9 done, no code changed: `.venv/bin/cloa-viewer` given the repo's main
  checkout and this worktree as its two arguments, `--port 8791`, with the real
  `XDG_STATE_HOME`, 6.65 s from launch to the printed address, stderr empty. `/api/checkouts` listed the two
  entries the toggle exists for, one repo and two branches:
  `dev-playbook-342af143` / `main` / `/home/geoff/workspace/dev-playbook` at
  `0467d7dc`, and `cloa-viewer-tool-9d5ec20d` / `worktree-cloa-viewer-tool` /
  the worktree at `faf07aca`. No generator failed: both `refresh.json` records
  say `ok` for `index-tree` (1 view each) and `markdown-file` (194 views on
  `main`, 200 here). inotify during the run: the server held 16 file
  descriptors, 3 of them inotify instances, machine-wide 74 of the 128
  `max_user_instances`. Playwright from the scratchpad: one optgroup
  `dev-playbook` with options `main` and `worktree-cloa-viewer-tool`, both
  group headers `Concept documents` and `Harness-owned files` present on every
  checkout and after a reload, switching to `main` and back rewrote the hash
  and redrew the tree (69 rows against 70) and the refresh stamp followed the
  branch's HEAD, reload kept the worktree selected, console clean. One finding
  for the user, not a defect and no plan slip: the address line is
  block-buffered when stdout is redirected, so the first attempt looked hung
  for 2m20 while the server was already answering — `PYTHONUNBUFFERED=1`, or
  polling the port as `test_cli.start_server` does, is the way to wait for it.
  Next: task 10, `timeout_graceful_shutdown` so Ctrl-C stops the server while
  a page holds the stream.
- Task 10 done, the last task in the plan: `cli.serve` passes
  `timeout_graceful_shutdown=SHUTDOWN_SECONDS` (a new constant, 2) to
  `uvicorn.run`, and its docstring says why — a graceful shutdown waits for
  every open connection and the page's event stream never closes on its own.
  `test_cli.py`'s `serving` contextmanager now takes a `port` and yields the
  `Popen` instead of a URL, and the fixture chain is `port` → `server` →
  `address`, so a test can signal the process and read its exit status;
  `workspace_address` builds its URL from the same `port` fixture. The new
  `test_interrupt_stops_the_server_while_a_page_holds_the_stream` loads the
  page, waits for `.tree`, sends SIGINT and asserts `returncode == 0`. Proved
  by mutation: with the argument removed the test fails with
  `subprocess.TimeoutExpired` after 10 s, which is the user's four-Ctrl-C
  report exactly. Two docstrings that claimed the old behaviour were corrected
  — `start_server`'s (uv swallows the signal, rather than the shutdown
  blocking forever) and the Playwright working note, which still named the
  `address` fixture as the holder of the guard and the kill. No plan slips.
  Gate green, 1315 tests. Next: nothing — every task in this plan is complete.
