# Plan: cloa-viewer loop 2, the room

A Ralph loop works this file top to bottom. Each iteration, a fresh agent with
no memory reads this plan and the progress log, does the first unchecked task,
checks it off, and commits. Everything it needs to act is here — including the
Working notes below, where earlier iterations leave facts you will need. Add to
them whenever you learn something a future iteration would otherwise rediscover.

Loop 1 built the vertical slice (its plan is in git history at commit
`2f1d7dd`). This loop fixes what the user saw on first use and makes one
server cover the whole workspace: the tree in the two groups the standard
names with excluded files absent, levels told apart by eye, word counts gone,
a `decision-record` link status, and discovery of every checkout under a
directory with a toggle to switch between them. The three CLOA kinds are not
in this loop; the user is designing their panels by hand.

## What you may write

You write code and tests for one task, and the loop's own bookkeeping. The
complete list:

- `src/dev_playbook/cloa_viewer/` and everything under it.
- `tests/dev_playbook/cloa_viewer/` and everything under it, and
  `tests/cloa_viewer_fixtures.py`.
- `src/dev_playbook/md.py`: task 1 adds two constants and one function.
  Never change an existing line.
- `scripts/ref-lint`: task 1 replaces its private records constants with the
  import from `md.py`. Nothing else in the file changes.
- `tests/dev_playbook/test_md.py`: task 1 adds tests for the new function.
- This file: check off your task, and add facts to Working notes.
- `PROGRESS.md`: append your one line.

Everything else is read-only. In particular `worktree-cloa-viewer-tool-working-docs/`
is the design you are implementing: read it, quote it, obey it, and never edit
it. `pyproject.toml`, `Makefile`, `.pre-commit-config.yaml`, `.gitignore`,
`doc-types/`, `standards/`, `docs/`, and every other existing file are out of
scope for this loop. If a task seems to require editing something outside
this list, stop, record the conflict in `PROGRESS.md`, and set `blocker`.

## The design you are implementing

The working documentation set at `worktree-cloa-viewer-tool-working-docs/`
holds every design decision. Read `ROOT.md` first in every iteration, then the
member your task names:

- `ROOT.md`: goal, principles, constraints, terms. The principles bind you:
  no transformation upstream, known kinds only, deterministic, fail loud,
  total accounting, the user owns the room, simple and standard and modular.
  The new constraint: the viewer classifies nothing itself; it calls the
  functions the linters call.
- `contract.md`: the state directory, view file paths, identities, the
  envelope, the refresh record, the failure rules.
- `registry.md`: what `index-tree` and `markdown-file` show after this loop:
  two groups, no word count, the `decision-record` status.
- `viewer.md`: the tree's groups and level guides, the checkout toggle and
  discovery, failure on screen.
- `server-and-stack.md`: the command's path rule, the server's five jobs.

This plan makes every implementation decision the design leaves open. Where
this plan and a member disagree on a detail, this plan wins for this loop,
and you note the disagreement in `PROGRESS.md` so the user can reconcile
the design later. You do not resolve it by editing the design.

## Done when

- `uv run cloa-viewer <directory>` for a directory that is not a checkout
  discovers every git repo directly under it and every linked worktree of
  each, refreshes them all, and serves one page whose top bar offers them in
  a select grouped by repo and labelled by branch. Choosing one swaps the
  tree and the panels without a reload; a reload returns to the chosen one.
  Discovery is proven on fixture repos; the smoke run covers dev-playbook's
  main checkout and this worktree, never the other repos in `~/workspace`.
- The tree shows two groups, `Concept documents` and `Harness-owned files`,
  by `dev_playbook.md.classify`; `PLAN.md` and `PROGRESS.md` appear nowhere
  and have no view file. Levels are separated by guide lines. No row shows a
  word count. A concept document no index reaches sits under a red
  `Not indexed` row.
- A link out of a numbered decision record whose target is gone shows the
  badge `decision-record`, not `broken`, and `scripts/ref-lint` decides which
  files are records through the same function in `md.py`.
- `make check` is green, and no file outside the "What you may write" list
  has changed in the branch's history since this plan was committed.

## Working notes

- **Package location.** The package is `src/dev_playbook/cloa_viewer/`, a
  subpackage of `dev_playbook`. The build standard allows exactly one package
  under `src/`, enforced by repo-lint inside `make check`, so never create
  `src/cloa_viewer/`.
- **Standards that bind the code.** `standards/python/style.md`: empty
  `__init__.py` files (zero bytes), a docstring on every module and public
  function (ruff `D` rules, pep257), module layout order (docstring, imports,
  literal constants, definitions), helpers only when justified. `standards/testing/conventions.md`:
  tests mirror the source path (`src/dev_playbook/cloa_viewer/state.py` is
  tested at `tests/dev_playbook/cloa_viewer/test_state.py`), fixtures in the
  nearest `conftest.py`, expected values written as literals in the test, no
  logic in tests, assert on observable outputs. mypy runs strict-ish on `src`
  and `tests`: annotate every signature.
- **Commands.** `make check` is the gate (ruff, mypy, pytest, the pre-commit
  suite). `make web` builds the page and must be run before the Playwright
  test after any change under `web/src/`. Never chain `cd` with another
  command in a shell call or a Makefile recipe; use `npm --prefix <dir>`.
- **The user's own viewer may be running on port 8765 from this checkout
  while you work.** Never `pkill -f cloa-viewer` or kill anything by name.
  Start your own server on a free port and kill only the PID you started.
  The tests already pick a free port with a bound socket.
- **Existing helpers to reuse, never reimplement.** `dev_playbook.gitrepo`:
  `git_files(root)` (relative paths of tracked and untracked-unignored files,
  sorted), `canonical_repo_name(root)`, `no_git_env()` (pass as `env=` to
  every git subprocess). `dev_playbook.md`: `classify(relpath)` answers
  `"excluded" | "index" | "concept" | "harness"` for a repo-relative path and
  is the one encoding of the file-role boundary; `parse_frontmatter(text)`
  returns `(mapping | None, body)`; `github_slug(heading_text)`;
  `markdown_links(line)` returns `(text, target)` pairs with inline code
  stripped; `lines_outside_fences(body)` yields `(line_number, line)`. Test
  fixtures in `tests/conftest.py`: `init_repo(path)` and `commit_all(repo)`
  build a real git repo; the autouse `_clean_git_env` fixture is in place.
- **`.claude/worktrees/` is gitignored** in this repo (line 12 of
  `.gitignore`), so `git_files` of a main checkout never lists a worktree's
  files, and a worktree found under it is a checkout of its own.
- **inotify budget on this machine.** `fs.inotify.max_user_watches` is
  269696 and `max_user_instances` is 128. One `watchfiles.awatch` per
  checkout uses one instance; `~/workspace` holds about 20 repos and 2
  worktrees today, well inside both. The smoke run watches two checkouts;
  record the numbers you see.
- **Fixture checkout.** `tests/cloa_viewer_fixtures.py` holds
  `build_checkout(tmp_path) -> Path`, which creates `tmp_path / "fixture"`
  (canonical repo name `fixture`) with exactly the files listed in loop 1's
  plan plus whatever tasks 2 and 4 of this plan add. Every test module wraps
  it in its own three-line `checkout` fixture. Do not build a second fixture
  repo; extend this one.
- **State directory in tests.** Every test that touches the state directory
  sets `XDG_STATE_HOME` to `tmp_path` with `monkeypatch.setenv` so nothing
  touches `~/.local/state`.
- **Playwright.** Chromium is cached under `~/.cache/ms-playwright`; the
  end-to-end test in `tests/dev_playbook/cloa_viewer/test_cli.py` starts
  `<repo>/.venv/bin/cloa-viewer` directly (never through `uv run`, which
  orphans the server) from the `address` fixture, which also holds the
  `run make web first` guard and the kill, because `testing-lint` forbids
  `if`/`try` in a `test_*` body (`src/dev_playbook/testing_lint.py`, rule
  `testing.no-logic`). Playwright's `has_text` is a case-insensitive
  substring match; match a row by an exact string or by index.
- **`uv.lock` moves with `pyproject.toml`.** Not expected this loop: no task
  edits `pyproject.toml`.
- **No `__init__.py` anywhere under `tests/`, and only the root
  `tests/conftest.py` may exist.** pytest imports test modules by rootdir, so
  every test module basename must be unique across the whole `tests/` tree,
  and a second `conftest.py` shadows the root one. `tests/` is the only
  directory both pytest and mypy resolve a bare import from, which is why the
  shared fixture module sits there. ruff reads an imported fixture as
  redefined by every test that takes it as a parameter (F811), hence the
  per-module wrapper fixture.
- **The state module is the only writer.** `dev_playbook.cloa_viewer.state`:
  `state_root`, `checkout_dir`, `head_commit`, `branch_name`,
  `write_checkout_json`, `envelope`, `load_schema`, `validate`, `write_json`,
  `ContractError`. `write_json` sorts keys, indents by 2, ends with a newline,
  and stages at `path.with_suffix(".tmp")` before `os.replace`. `validate`
  sorts errors by `(json_path, message)` and raises `ContractError` on the
  first.
- **A kind module never imports `registry`.** `View` and `Kind` live in
  `entry.py`; `registry` imports every kind module to build `KINDS`.
  `registry.kind_by_name` raises `KeyError` naming what was asked.
- **Link targets resolve in one place.** `identity.py` holds
  `resolve_target(source, target, repo)` (drops a `#fragment`, resolves a
  leading `/` against the checkout root and anything else against the source
  file's directory, resolves a same-repo `~/workspace/<repo>/` Citation into
  the checkout, raises `ValueError` for a Citation of another repo, normalizes
  `..`), `is_external(target)` (`http://`, `https://`, `mailto:`),
  `WORKSPACE_PREFIX`, and `citation_repo(target)`. `kinds/markdown_file.py`
  has `_target_identity(source, target)` for the bare `#anchor` case, and a
  `Link` TypedDict `{target, status, identity}`; `_link` answers `external`
  first, then `citation`, then `ok`/`broken` by identity. `links_in` reads
  `link["identity"]`.
- **`refresh` reads the registry at call time.** `refresh.refresh(checkout)`
  is the only thing that writes a checkout directory; a test swaps kinds with
  `monkeypatch.setattr(registry, "KINDS", (...))`. Staging is
  `<checkout_dir>/.staging/<kind>/<view relpath>`; publishing renames the live
  directory to `<staging>/<kind>/retired` and the staged one into place, so
  the watcher never sees per-file deletes. `refresh` validates the record
  against `schemas/refresh.schema.json` before writing `refresh.json`.
- **The Makefile carries a second `.PHONY` line, on purpose.** `scripts/repo-lint`
  compares the canonical fragment verbatim. Not touched this loop.
- **The state watcher and the checkout watcher.** `server.watch_state` fans a
  directory event out into one `changed` per `*.json` below it, treats a
  `deleted` event whose path exists again as `changed`, dedupes within a
  batch, and debounces at `STATE_DEBOUNCE_MS` = 200. `watch.watch_checkout(checkout, *, debounce_ms=300, stop)`
  filters every path with a `.git` component (without it each refresh would
  retrigger itself through `git ls-files`). `build_app`'s `_lifespan` starts
  `watch_state()` plus one `watch_checkout` task per checkout and cancels
  them on shutdown. The closed loop from an edit to the page costs about
  0.17 s on a two-file checkout.
- **Starlette 1.6 has no `on_startup`**; `build_app` passes a `lifespan`
  `asynccontextmanager`. `TestClient` without `with` runs no lifespan, so the
  route tests start no watcher; `with TestClient(app)` runs it and refreshes
  the fixture for real on every edit under it. `httpx.ASGITransport` buffers
  a whole response and hangs on the event stream; exercise the stream through
  `watch_state` plus `publish`, never a test client.
- **The command's two seams are `cli.dist_dir()` and `cli.serve()`.**
  `dist_dir() -> Path` returns `<package>/web/dist`; a test points the
  command at a fake `dist` with `monkeypatch.setattr(cli, "dist_dir", lambda: built)`,
  and the fake needs an `assets/` directory as well as `index.html`.
  `serve(app, port)` holds the `uvicorn.run` call alone; `test_cli.py`'s
  `record_serve(monkeypatch)` replaces it and returns the recorded calls.
  Today `main` sets `app.state.checkouts` to a list of checkout **dir
  names**, and `test_no_checkout_argument_serves_the_repo_holding_the_directory`
  asserts on it; task 7 changes that shape and must move the test with it.
- **The page's seams.** `web/src/api.ts` is the only module that calls
  `fetch` or opens an `EventSource`; `Checkout` there is `{dir, path, repo,
  branch, head}`. `validate.ts` compiles the envelope schema and every kind
  schema once in `loadSchemas()`, so `validateView(json)` is synchronous;
  Ajv must be the 2020 build (`import { Ajv2020 } from "ajv/dist/2020"`).
  `store.ts` `useViewer()` holds all state, is the only place that fetches,
  and exposes `openPanel`, `openError(path, error)`, `closePanel`,
  `refreshNow`, `loaded`, `open` (newest first), `failure`. `kinds/index.ts`
  `RENDERERS` is a `Map`; a renderer is given `{view, viewer}`.
  `components/ViewBody.tsx` resolves a path to a renderer or an `ErrorPanel`
  for the tree region and every panel alike. The connection has three states:
  `connecting`, `connected`, `disconnected`; the banner shows on
  `disconnected` only.
- **The page splits the frontmatter off the source before rendering it**
  (`MarkdownFile.tsx` `split()`), because markdown-it reads the closing `---`
  as a setext underline. `followLink` cancels every anchor click inside
  `.file-source` and looks the `href` up in a map built from `links_out`, so
  the browser resolves no paths.
- **Vite writes `dist/index.html`, `dist/assets/index-<hash>.js`, and
  `dist/assets/index-<hash>.css`.** `build_app` serves `/` and mounts
  `/assets`, so a new asset needs no server change.
- **ref-lint's records policy today.** ~~`scripts/ref-lint` lines 64–113 hold
  `RECORDS_DIR = ("docs", "decisions")`, `_RECORD_NAME = re.compile(r"^\d+-.+\.md$")`,
  `_VALIDATED_RECORDS_FILES`, `UnclassifiedRecordsFile`, and
  `source_files(repo_root)`, which skips a numbered record as a source
  ("immutable, accepted staleness"). ref-lint already does `from dev_playbook import md`
  and is tested by `tests/test_ref_lint.py`, which must stay green when task
  1 moves the predicate.~~ Done in task 1: `md.RECORDS_DIR`,
  `md.RECORD_NAME`, and `md.is_decision_record(relpath)` are the one home;
  ref-lint reads `md.RECORDS_DIR` and calls the predicate, and no longer
  imports `re`. Task 2 calls `md.is_decision_record(source)`.
- **The fixture holds seven markdown files after task 2.** `index.md`,
  `alpha.md`, `docs/index.md`, `docs/beta.md`, `docs/decisions/index.md`,
  `docs/decisions/0001-alpha.md`, `orphan.md`. A directory node's identity is
  the full repo-relative path with a trailing slash, so `docs/`'s third child
  is `docs/decisions/`, not `decisions/` as task 2's wording had it. Word sums
  moved with the new files — `docs/` is 43 and `root` is 85 — and task 3
  deletes those assertions along with `words` itself.
- **A neutral badge needs no CSS.** `app.css` styles only `.badge-ok` and
  `.badge-broken`; `citation` and now `decision-record` fall through to the
  muted `.badge` base, so task 2 changed no CSS. Adding a rule for
  `.badge-decision-record` would be the thing that made it stand out.
- **`Row`'s `count` is optional after task 3.** `IndexTree.tsx`'s `Row` takes
  `count?: string` and renders `.tree-count` only when it is given; the
  `Unindexed` row is the one caller that passes one today. Task 4's group row
  and `Not indexed` row need no new prop for their `N files`.
- **The fixture holds nine markdown files after task 4**, one of every
  `classify` answer: the seven from task 2, plus `CLAUDE.md` (`harness`) and
  `PLAN.md` (`excluded`). `CLAUDE.md` sorts *before* `alpha.md` — capitals
  precede lowercase — so it is the first entry in every sorted view-file list.
  Three counts moved with it and a future task that adds a file must move them
  again: `test_refresh.py`'s `markdown-file` count (now 8),
  `test_server.py::test_the_file_list_holds_every_view_file` (the plan did not
  name this one), and `test_markdown_file.py`'s relpath list.
- **A stand-in payload in a test must satisfy the schema's `required`.**
  `test_refresh.py`'s `bad_payload_generate` breaks `$.root` on purpose and
  asserts the error names `$.root`; `state.validate` sorts errors by json path,
  so `$` (a missing top-level key) would sort first and win. When
  `index-tree.schema.json` gained required `harness`, that stand-in had to gain
  `"harness": []` to keep failing where the test says it fails.
- **`Row` in `IndexTree.tsx` builds its class list from named booleans**
  (`group`, `bad`, `missing`), not a ternary; task 5 pushed
  `tree-row-directory` the same way. `.tree-group` carries the uppercase muted style and
  `.tree-row-bad .tree-title` the red; neither touches `.tree-row` itself, so the
  Playwright selector `.tree .tree-row` still matches every row including the two
  group headers.
- **The tree nests, and nothing computes an indent.** After task 5 every open
  row puts its children in one `<div className="tree-children">` — the two
  group rows, every directory, and the `Not indexed` row alike — and that box
  carries both the step in and the guide line. `Row` takes no `depth` and sets
  no inline style; a task that adds a level adds a box, never a number.
  `.tree-row-directory` (any row whose `open` is not null and is not a group,
  so the `Not indexed` row too) is `font-weight: 600`, with one extra rule the
  plan did not name, `.tree-row-directory .tree-description { font-weight: 400 }`,
  so the heavier setting reads as the title rather than the whole row.
- **This checkout has no unindexed concept document**, so the red `Not indexed`
  row never appears on a server pointed at it — okf-lint is green here. To see
  that row, point the server at a fixture checkout: build one outside the repo
  with `PYTHONPATH=<repo>/tests python -c "from pathlib import Path; from
  cloa_viewer_fixtures import build_checkout; build_checkout(Path('<dir>'))"`,
  which leaves `orphan.md` unreached. Give any such throwaway server its own
  `XDG_STATE_HOME` so it never fights the user's viewer over a checkout
  directory in `~/.local/state`.
- **Discovery mixes resolved and unresolved paths, on purpose.**
  `discover.worktrees` returns what `git worktree list --porcelain` prints,
  `.resolve()`d; `discover.checkouts` returns a source that is itself a
  checkout exactly as it was given. Every caller must therefore resolve its
  sources before handing them over — `cli.main` already does
  (`Path(path).resolve()`), and task 7 must keep that, or `rescan` will see
  the same checkout twice under two spellings and `state.checkout_dir` will
  disagree with itself.
- **The fixture holds ten files after task 6**, the ninth markdown one plus a
  `.gitignore` = `.claude/worktrees/\n`. It is not markdown, so no view-file
  count moved; `git_files` grew by one entry, which only
  `markdown_file.generate`'s `tracked` set sees and nothing asserts on.
  `add_worktree(checkout, name)` puts a linked worktree on a new branch at
  `<checkout>/.claude/worktrees/<name>` and returns that path unresolved —
  equal to git's resolved answer because pytest's `tmp_path` is already real
  (`/tmp` is not a symlink on this machine).
- **The server holds sources, not checkouts, after task 7.**
  `build_app(sources, dist)` sets `app.state.sources` (absolute resolved paths —
  the caller resolves, `build_app` does not), `app.state.checkouts = []`
  (a `list[Path]`, `rescan`'s answer), and `app.state.watchers = {}`
  (`dict[Path, tuple[asyncio.Task[None], asyncio.Event]]`, the type alias
  `server.Watcher`). `_checkout_path` scans the list comparing
  `state.checkout_dir(c).name`. `rescan(app)` runs in `_lifespan` before
  `watch_state` and again in `GET /api/checkouts`. **A `TestClient` used
  without `with` therefore runs no discovery**: the checkout list stays empty
  and every `/api/checkouts/{dir}/…` route answers 404, which is why
  `test_server.py`'s `client` fixture is now a `with TestClient(...)`
  generator and every route test runs the real watchers.
- **`watch.watch_filter(ignore)` builds the watcher's filter closure**;
  `watch_checkout` takes `ignore: Sequence[Path] = ()` and `_start_watcher` in
  `server` fills it with every discovered checkout that `is_relative_to` this
  one. A watcher is started once and never restarted, so a worktree created
  after its parent's watcher started is not in that parent's `ignore`; the
  parent then refreshes on edits inside it, which is waste, not error, because
  `.gitignore` keeps the worktree out of the parent's file list.
- **`refresh.json`'s `finished` cannot prove a refresh did not happen.** It is
  RFC 3339 to the second, so two refreshes inside one second read the same.
  `test_watch.py`'s `refreshed_at` polls the file's `st_mtime_ns` instead.
- **`src/dev_playbook/decisions_lint.py` keeps its own `_RECORD_NAME`**
  (line 63), a *capturing* `^(\d+)-.+\.md$` it reads the number out of. It is
  a different need from the boolean predicate and is out of scope for this
  loop — do not touch it.

## Tasks

- [x] **Task 1: the decision-record predicate, shared.** In
  `src/dev_playbook/md.py`, in the constants block, add
  `RECORDS_DIR = ("docs", "decisions")` and
  `RECORD_NAME = re.compile(r"^\d+-.+\.md$")`, and beside `classify` add
  `is_decision_record(relpath: str) -> bool`: true when the path's first two
  parts equal `RECORDS_DIR` and its name matches `RECORD_NAME`. Its docstring
  states the policy in one sentence: a numbered record is immutable, so its
  outbound references are accepted staleness, and names ref-lint and the
  viewer as the two callers. In `scripts/ref-lint`, delete the private
  `RECORDS_DIR` and `_RECORD_NAME`, read `md.RECORDS_DIR` where the tuple is
  used, and make `source_files` call `md.is_decision_record(str(rel))` in
  place of the regex; keep `_VALIDATED_RECORDS_FILES`, `UnclassifiedRecordsFile`,
  and every message as they are. Tests in `tests/dev_playbook/test_md.py`,
  in that file's style, with three literal cases:
  `docs/decisions/0007-choose.md` is true, `docs/decisions/index.md` is
  false, `standards/decisions/0007-choose.md` is false. Run
  `uv run scripts/ref-lint` on this checkout before and after: the same
  count of references, all ok. Gate green.

- [x] **Task 2: the `decision-record` link status.** In
  `kinds/markdown_file.py`, `_link` answers in this order: `external`;
  `citation`; `ok` when the identity is tracked; `decision-record` when
  `md.is_decision_record(source)`; else `broken`. A `decision-record` link
  keeps its resolved identity like a broken one. In
  `schemas/markdown-file.schema.json` the `status` enum gains
  `decision-record` and the description names the five cases;
  `kind_version` stays 1. In `MarkdownFile.tsx` the badge for
  `decision-record` is neutral, styled like `citation`, never red. Fixture,
  in `tests/cloa_viewer_fixtures.py`: add `docs/decisions/0001-alpha.md` with
  frontmatter `type: Decision-Record`, `title: Alpha decided`,
  `description: The fixture decision` and body
  `# Alpha decided\n\nSee [alpha](/alpha.md) and [gone](/gone.md).\n`; add
  `docs/decisions/index.md` = `# decisions — index\n\nThe fixture decisions.\n\n- [Alpha decided](/docs/decisions/0001-alpha.md) — The fixture decision\n`;
  append to `docs/index.md`'s listing the line
  `- [decisions/](/docs/decisions/index.md) — The decisions directory\n`.
  Tests: in `kinds/test_markdown_file.py` the record's `links_out` are, in
  order, `/alpha.md` `ok` `alpha.md` and `/gone.md` `decision-record`
  `gone.md`; `alpha.md`'s `links_in` becomes
  `["docs/decisions/0001-alpha.md", "index.md"]`; in `test_refresh.py` the
  `markdown-file` count becomes 7; in `kinds/test_index_tree.py` `docs/`'s
  children are `docs/index.md`, `docs/beta.md`, `decisions/` in that order.
  Every payload still validates. Gate green.

- [x] **Task 3: no word counts.** Remove `words` from both node shapes in
  `kinds/index_tree.py` and from the payload in `kinds/markdown_file.py`,
  from both schemas (`kind_version` stays 1), from `IndexTree.tsx` (the
  `count` on directory and file rows goes; the `Unindexed` row's
  `N files` stays until task 4 replaces it) and from `MarkdownFile.tsx`'s
  facts row (`type` and `headings` remain), and from every docstring and
  comment that names it. Tests: drop every word assertion in
  `kinds/test_index_tree.py` and `kinds/test_markdown_file.py`; in
  `test_watch.py` replace `words_of` with `source_of`, reading
  `payload["source"]`, and assert the source after the edit ends with the
  appended text; in `test_cli.py`'s `test_page_shows_tree_and_updates`,
  delete the two word-count expectations and, after the write to
  `alpha.md`, `expect(page.locator(".panel-body")).to_contain_text("nine ten", timeout=5000)`.
  `make web`, then gate green.

- [x] **Task 4: the two groups, by `classify`.** In `kinds/index_tree.py`,
  `generate` takes every `.md` path from `git_files(checkout)` and drops
  those `md.classify` calls `excluded`; the walk runs over the rest; the
  payload becomes `root` (as now), `unindexed` (the `concept` and `index`
  class files the walk never reached, sorted by identity), and `harness`
  (the `harness` class files the walk never reached, sorted by identity),
  all three required in the schema, `harness` an array of file nodes. In
  `kinds/markdown_file.py`, `generate` skips an `excluded` file entirely,
  so it has no view. In `IndexTree.tsx`: two group rows at the top level,
  `Concept documents` and `Harness-owned files`, both expanded at first,
  with the class `tree-group` and a small uppercase muted style in
  `app.css`; the second carries the count `N files`. Under the first: the
  root directory node as today, then, only when `unindexed` is not empty,
  a row titled `Not indexed` with the count `N files`, class
  `tree-row-bad`, its title in `var(--bad)`, collapsed at first, holding
  those file rows. Under the second: the flat list. Fixture: add
  `CLAUDE.md` = `Read the index first.\n` (class `harness`) and `PLAN.md` =
  `# Plan\n\n- [ ] nothing\n` (class `excluded`). Tests: in
  `kinds/test_index_tree.py`, `harness` is exactly `["CLAUDE.md"]`,
  `unindexed` is exactly `["orphan.md"]`, and no node anywhere in the
  payload has identity `PLAN.md`; in `kinds/test_markdown_file.py` no view
  has relpath `markdown-file/PLAN.md.json` and one has
  `markdown-file/CLAUDE.md.json`; in `test_refresh.py` the `markdown-file`
  count becomes 8; in `test_cli.py`'s end-to-end test, expect the tree to
  contain the text `Harness-owned files` and the text `Not indexed`.
  `make web`, then gate green.

- [x] **Task 5: levels told apart by eye.** In `IndexTree.tsx`, stop
  indenting with `paddingLeft` and `depth`: a directory's children render
  inside a `<div className="tree-children">`, one per open directory, and
  the group rows' children the same way. In `app.css`:
  `.tree-children { margin-left: 10px; padding-left: 6px; border-left: 1px solid var(--line); }`
  (add `--line` beside the existing color variables if it does not exist,
  a light gray that reads on `--ground`), directory rows
  (`.tree-row-directory`, a class the `Row` gains when `open` is not
  null and the row is not a group) at `font-weight: 600`, and file rows
  at the normal weight. Remove `INDENT_PX`. Then run a Playwright script
  from the scratchpad against a server you start on a free port over this
  checkout, save a screenshot, look at it, and confirm three things before
  you commit: the guide lines are visible at every open level, the two
  group headers read as headers, and the `Not indexed` row is red. Write
  what you saw in the PROGRESS line. `make web`, then gate green.

- [x] **Task 6: discovery.** Create `src/dev_playbook/cloa_viewer/discover.py`
  with `is_checkout(path: Path) -> bool` (true when `path / ".git"`
  exists, a directory for a main checkout or a file for a linked
  worktree); `worktrees(repo: Path) -> list[Path]`, which runs
  `git worktree list --porcelain` in `repo` with `no_git_env()`, splits
  the output into blank-line-separated blocks, and returns the resolved
  path from each block's `worktree <path>` line except a block that
  carries a `bare` or `prunable` line, the main checkout first as git
  prints it; and `checkouts(sources: list[Path]) -> list[Path]`: for each
  source, when `is_checkout(source)` the result gains that one path, else
  it gains `worktrees(child)` for every immediate child directory, sorted
  by name, that `is_checkout` accepts; a non-checkout source that yields
  nothing raises `ValueError(f"{source}: no checkout found")`; the result
  is deduplicated preserving order. Add `add_worktree(checkout: Path, name: str) -> Path`
  to `tests/cloa_viewer_fixtures.py`, running
  `git worktree add <checkout>/.claude/worktrees/<name> -b <name>` with
  `no_git_env()` and returning the new path (the fixture has no
  `.gitignore`, so also write one containing `.claude/worktrees/\n` in
  `build_checkout` and commit it, so the main checkout's `git_files` does
  not list the worktree's files; adjust any count that changes and say
  so in PROGRESS). Tests at `tests/dev_playbook/cloa_viewer/test_discover.py`,
  with a workspace fixture `ws = tmp_path / "ws"`, `main = build_checkout(ws)`,
  `wt = add_worktree(main, "wt")`: `checkouts([ws]) == [main, wt]`;
  `checkouts([main]) == [main]`; `checkouts([tmp_path / "empty"])` (an
  empty directory you create) raises `ValueError`; `is_checkout(wt)` is
  true and `is_checkout(ws)` is false. Gate green.

- [x] **Task 7: the server discovers, and the command scans.**
  `server.build_app(sources: list[Path], dist: Path) -> Starlette` now
  takes the paths the command was given. `app.state.sources` holds them,
  `app.state.checkouts: list[Path]` the current list, and
  `app.state.watchers: dict[Path, tuple[asyncio.Task[None], asyncio.Event]]`
  the running checkout watchers. Add `async def rescan(app: Starlette) -> list[Path]`:
  it computes `discover.checkouts(sources)` in `asyncio.to_thread`; for a
  checkout not yet in `app.state.checkouts` it refreshes it in a thread
  when `state.checkout_dir(c) / "refresh.json"` does not exist, then
  starts its watcher; for one no longer found it sets the stop event,
  awaits the task, and removes `state.checkout_dir(c)` with
  `shutil.rmtree` when present; then it stores and returns the new list.
  The watcher call becomes `watch.watch_checkout(checkout, *, ignore=[...], ...)`
  where `ignore` is every other discovered checkout under this one, and
  the filter drops a path inside any of them. `_lifespan` calls
  `rescan(app)` once before starting `watch_state`, and stops every
  watcher on shutdown. `GET /api/checkouts` awaits `rescan(app)` first,
  then answers as today. In `cli.py`: the positional argument is renamed
  `path` (help: `a checkout, or a directory of repos to scan; defaults to
  the repo holding the current directory, else the current directory`);
  `main` builds `sources` from the arguments, or from `current_checkout()`
  when there are none and the directory is in a repo, or from `Path.cwd()`
  when `git rev-parse` fails; computes `discover.checkouts(sources)`,
  printing a `ValueError`'s message to stderr and returning 2; refreshes
  each as today; and calls `build_app(sources, dist)`. Tests: move
  `test_no_checkout_argument_serves_the_repo_holding_the_directory` to
  assert on `app.state.sources == [checkout.resolve()]`; add to
  `test_server.py`, using `with TestClient(build_app([ws], dist))` over
  the task 6 workspace fixture: `/api/checkouts` lists two entries whose
  `path`s are `main` and `wt`; after `add_worktree(main, "second")` the
  same request lists three; after `git worktree remove <wt path>` (run
  with `no_git_env()`) it lists two and `state.checkout_dir(wt)` no
  longer exists; and in `test_watch.py`, a watcher over `main` with
  `ignore=[wt]` does not refresh `main` when a file under `wt` changes
  (poll `refresh.json`'s `finished` for two seconds and assert it did not
  move). Gate green.

- [ ] **Task 8: the toggle on the page.** In `store.ts`: `open` becomes
  per checkout, a `Map<string, readonly string[]>` keyed by `dir`, with
  `open` in the returned `Viewer` still the current checkout's list;
  `selectCheckout(dir: string)` sets the selection and writes
  `location.hash = dir`; on load the selection is the checkout whose `dir`
  equals `location.hash.slice(1)` when one matches, else the first; on
  every `refreshed` event, for any checkout, the store fetches the
  checkout list again, replaces `checkouts` and the current `checkout`
  object (so a branch change shows), and, when the selected `dir` is no
  longer listed, selects the first. In `TopBar.tsx` the plain
  `repo · branch` text becomes a `<select className="topbar-checkout">`
  with one `<optgroup label={repo}>` per repo in list order and one
  `<option value={dir} title={path}>{branch}</option>` per checkout, the
  current one selected, calling `selectCheckout` on change. `app.css`
  styles the select to sit in the bar at the same height as the button.
  Test: extend `test_page_shows_tree_and_updates` or add a sibling with
  its own `address`-style fixture that starts the server over the task 6
  workspace fixture (build it in the fixture, kill by PID in `finally`):
  the select has two options; `page.select_option(".topbar-checkout", label="wt")`
  makes the select's value the worktree's `dir`, `location.hash` equal
  `#<dir>`, and the tree still show `Alpha`; `page.reload()` keeps that
  selection. `make web`, then gate green.

- [ ] **Task 9: the smoke run on dev-playbook's checkouts.** The smoke
  run covers dev-playbook only: the other repos under `~/workspace` are
  not maintained to this repo's standard, and their edge cases are not
  this loop's business, so do not point the server at `~/workspace`. Run
  `make web`, then start
  `.venv/bin/cloa-viewer ~/workspace/dev-playbook <this worktree's absolute path> --port <free port>`
  with the real `XDG_STATE_HOME` unset, from this checkout, and time it
  from launch to the printed address. Two checkouts of one repo is the
  case the toggle exists for: one optgroup, two branches. With a
  Playwright script from the scratchpad: load the page, read the select's
  optgroups and options, switch to `main` and then back to this
  worktree's branch, screenshot each, confirm the tree shows the two
  group headers on both, and read `/api/checkouts`. Kill only that PID.
  Record in the PROGRESS line: the startup time, the two entries
  `/api/checkouts` listed, every generator that failed with the first
  line of its error, and the inotify instance count during the run
  (`ls /proc/<pid>/fd | wc -l` is enough). A failed generator on `main`
  is a finding for the user, not a blocker: do not edit a generator to
  tolerate it unless the traceback shows a defect in this package's own
  code, in which case fix the defect with a test. No code change is
  expected from this task otherwise. Gate green.

- [ ] **Task 10: Ctrl-C stops the server while a page is open.** The user
  pressed Ctrl-C four times on `uv run cloa-viewer` with the page open and
  the server did not exit: uvicorn's graceful shutdown waits for the open
  event stream for as long as the page lives (the `start_server` docstring
  in `test_cli.py` already records this). In `cli.serve`, pass
  `timeout_graceful_shutdown=2` to `uvicorn.run`, so an interrupt closes
  the stream and exits within about two seconds. Test in `test_cli.py`:
  refactor so a `server` fixture starts the process and yields it, and
  `address` derives the URL from it (behaviour unchanged for the existing
  end-to-end tests); add
  `test_interrupt_stops_the_server_while_a_page_holds_the_stream(server, address, page)`:
  `page.goto(address)`, wait for `.tree` to be visible, then
  `server.send_signal(signal.SIGINT)` and `server.wait(timeout=10)`, and
  assert `server.returncode == 0`. The fixture's `finally` still calls
  `kill()`, which is a no-op on a process already reaped. Gate green.
