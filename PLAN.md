# Plan: cloa-viewer loop 1, the vertical slice from disk to browser

A Ralph loop works this file top to bottom. Each iteration, a fresh agent with
no memory reads this plan and the progress log, does the first unchecked task,
checks it off, and commits. Everything it needs to act is here — including the
Working notes below, where earlier iterations leave facts you will need. Add to
them whenever you learn something a future iteration would otherwise rediscover.

## What you may write

You write code and tests for one task, and the loop's own bookkeeping. The
complete list:

- `src/dev_playbook/cloa_viewer/` and everything under it.
- `tests/dev_playbook/cloa_viewer/` and everything under it.
- `pyproject.toml`, `Makefile`, `.pre-commit-config.yaml`, `.gitignore`: only
  the additions a task names. Never change an existing line.
- This file: check off your task, and add facts to Working notes.
- `PROGRESS.md`: append your one line.

Everything else is read-only. In particular `worktree-cloa-viewer-tool-working-docs/`
is the design you are implementing: read it, quote it, obey it, and never edit
it. `doc-types/`, `standards/`, `docs/`, `scripts/`, and every other existing
file are out of scope for this loop. If a task seems to require editing
something outside this list, stop, record the conflict in `PROGRESS.md`, and
set `blocker`.

## The design you are implementing

The working documentation set at `worktree-cloa-viewer-tool-working-docs/`
holds every design decision. Read `ROOT.md` first in every iteration, then the
member your task names:

- `ROOT.md`: goal, principles, constraints, terms. The principles bind you:
  no transformation upstream, known kinds only, deterministic, fail loud,
  total accounting, the user owns the room, simple and standard and modular.
- `contract.md`: the state directory, view file paths, identities, the
  envelope, the refresh record, the failure rules.
- `registry.md`: what a kind is, and what `index-tree` and `markdown-file`
  show.
- `viewer.md`: the page: layout, tree, panels, refresh, failure on screen.
- `server-and-stack.md`: the command, the server's four jobs, live update,
  the stack, the checks.

This plan makes every implementation decision the design leaves open. Where
this plan and a member disagree on a detail, this plan wins for this loop,
and you note the disagreement in `PROGRESS.md` so the user can reconcile
the design later. You do not resolve it by editing the design.

## Done when

- `uv run cloa-viewer` started in this checkout serves a page at
  `http://127.0.0.1:8765/` that shows the index tree: every tracked markdown
  file under the `index.md` hierarchy with title, description, and word
  count, and an "Unindexed" branch holding the files no index reaches.
- Clicking a file in the tree opens a panel showing its frontmatter facts,
  headings, links out with status, links in, and the rendered source. Close
  removes it.
- Editing a markdown file in the checkout changes the affected panel and the
  tree within two seconds, with no page reload.
- A view file that fails its schema renders as a red error panel naming the
  file and the failing field. Stopping the server shows a banner across the
  top of the page.
- Every view file the generators write validates against the envelope schema
  and its kind schema, enforced in code before the write.
- A Playwright test drives the page end to end against a fixture checkout and
  passes inside `make check`.
- `make check` is green, and no file outside the "What you may write" list has
  changed in the branch's history since the plan was committed.

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
  suite). `uv sync` after any `pyproject.toml` edit. `make web` builds the
  page (added in task 9). Never chain `cd` with another command in a shell
  call or a Makefile recipe; use `npm --prefix <dir>` instead.
- **Existing helpers to reuse, never reimplement.** `dev_playbook.gitrepo`:
  `git_files(root)` (relative paths of tracked and untracked-unignored files,
  sorted), `canonical_repo_name(root)`, `no_git_env()` (pass as `env=` to
  every git subprocess). `dev_playbook.md`: `parse_frontmatter(text)` returns
  `(mapping | None, body)`; `github_slug(heading_text)`; `markdown_links(line)`
  returns `(text, target)` pairs with inline code stripped; `content_lines(path)`
  yields `(line_number, line)` outside fenced code. Test fixtures in
  `tests/conftest.py`: `init_repo(path)` and `commit_all(repo)` build a real git
  repo; the autouse `_clean_git_env` fixture is already in place.
- **Fixture checkout.** Task 3 creates the `checkout` fixture in
  `tests/dev_playbook/cloa_viewer/conftest.py`; every later test uses it, and
  its exact file contents are listed in task 3. Do not invent a second
  fixture repo.
- **State directory in tests.** Every test that touches the state directory
  sets `XDG_STATE_HOME` to `tmp_path` with `monkeypatch.setenv` so nothing
  touches `~/.local/state`.
- **Playwright.** Chromium is already cached under `~/.cache/ms-playwright`
  (builds 1234 and 1243). Task 1 installed playwright 1.62.0 with
  pytest-playwright 0.9.0, which may want a build neither of those is. If the
  Playwright test reports a missing browser, run
  `uv run playwright install chromium` once and note the result here.
- **`uv.lock` moves with `pyproject.toml`.** The lock file is tracked and
  `uv sync` rewrites it, so a task that edits `pyproject.toml` also changes
  `uv.lock`. That is expected and committed with the task, not a scope
  violation. Task 1 locked starlette 1.6.0, uvicorn 0.52.4, watchfiles 1.2.0,
  jsonschema 4.26.0, httpx 0.28.1.
- **No `__init__.py` anywhere under `tests/`.** pytest imports test modules by
  rootdir, so every test module basename must be unique across the whole
  `tests/` tree. `tests/dev_playbook/cloa_viewer/test_cli.py` already exists
  (task 1); name new ones so they do not collide with any other suite.
- **The state module is the only writer.** Task 2 built
  `dev_playbook.cloa_viewer.state`. Import from it, never re-derive: `state_root`,
  `checkout_dir`, `head_commit`, `branch_name`, `write_checkout_json`,
  `envelope`, `load_schema`, `validate`, `write_json`, and `ContractError`.
  `load_schema("envelope")` finds `schemas/envelope.schema.json` through
  `importlib.resources.files("dev_playbook.cloa_viewer")`, so a new kind schema
  is one JSON file dropped into that same directory and nothing else.
  `write_json` sorts keys, indents by 2, ends with a newline, and stages at
  `path.with_suffix(".tmp")` before `os.replace` — a caller must not write a
  view file any other way. `validate` sorts the validator's errors by
  `(json_path, message)` and raises `ContractError` on the first, so the same
  bad instance always names the same field.

- **Only the root `tests/conftest.py` may exist.** Task 3 tried the nested
  `tests/dev_playbook/cloa_viewer/conftest.py` the plan asked for and it broke
  the collection of seven existing suites: pytest prepends each collected
  file's directory to `sys.path`, so a second `conftest.py` anywhere under
  `tests/` shadows the root one and `from conftest import init_repo` finds the
  wrong file. The shared fixture lives at `tests/cloa_viewer_fixtures.py`
  instead, as `build_checkout(tmp_path) -> Path` — `tests/` is also the only
  directory both pytest and mypy resolve a bare import from. A test module
  wraps it in its own three-line `checkout` fixture rather than importing a
  fixture, because ruff reads an imported fixture as redefined by every test
  that takes it as a parameter (F811). Never add a `conftest.py` below
  `tests/`, and never build a second fixture repo.
- **A kind module never imports `registry`.** `View` and `Kind` are defined in
  `src/dev_playbook/cloa_viewer/entry.py`; `registry` re-exports both (they are
  in its `__all__`) and imports every kind module to build `KINDS`, so a kind
  importing `registry` back would deadlock the import. Import them from
  `entry`. `registry.kind_by_name` raises `KeyError` naming what was asked.
- **Link targets resolve in one place.** `src/dev_playbook/cloa_viewer/identity.py`
  holds `resolve_target(source, target)` (drops a `#fragment`, resolves a
  leading `/` against the checkout root and anything else against the source
  file's directory, normalizes `..`) and `is_external(target)` (`http://`,
  `https://`, `mailto:`). Task 4's `links_out` uses both; do not write a second
  resolver.
- **A link target resolves in the kind, not only in `identity`.** Task 4 added
  `_target_identity(source, target)` to `kinds/markdown_file.py`: a bare
  `#anchor` target names the file it sits in, and everything else goes to
  `identity.resolve_target`. Without that case `resolve_target("a.md", "#x")`
  answers `"."` — the source's own directory — and 15 files in this repo that
  link to their own headings would every one read as `broken`.
- **`links_out` has three statuses, and a Citation reads as `broken`.** Run on
  this checkout the kind writes 202 views that all validate, scoring 711 `ok`,
  20 `external`, and 195 `broken`; nearly every broken one is a
  `~/workspace/<repo>/...` Citation the cross-reference standard requires for a
  cross-repo target. The rule is the plan's, and correct as written — the target
  names no path in this checkout — but the panel cannot tell a citation from a
  dead link. Telling them apart is a fourth status and so a design change, for
  the user to settle, not a later task to assume.
- **`refresh` reads the registry at call time.** Task 5 built
  `dev_playbook.cloa_viewer.refresh.refresh(checkout)`, the only thing that
  writes a checkout directory. It does `from dev_playbook.cloa_viewer import
  registry` and reads `registry.KINDS` inside the loop, so a test swaps kinds
  with `monkeypatch.setattr(registry, "KINDS", (...))`; a `from ... import
  KINDS` anywhere would break that. Staging is
  `<checkout_dir>/.staging/<kind>/<view relpath>` — nested twice for a
  per-subject kind (`.staging/markdown-file/markdown-file/<identity>.json`), so
  publishing is one `os.replace` of `.staging/<kind>/<kind>` onto
  `<checkout_dir>/<kind>`. The whole `.staging` tree is cleared before the loop
  (a killed run leaves files behind) and after it, so no state directory ever
  holds one at rest. `refresh` also validates the record against
  `schemas/refresh.schema.json` before writing `refresh.json` — an addition to
  the plan's steps, so the writer and the schema the page reads cannot drift.
- **Node.** Node 22 and npm 10 are installed. `node_modules/` and `dist/`
  under the web directory are gitignored (task 9); `package-lock.json` is
  committed.
- **A renamed directory tells the watcher almost nothing, and this shapes both
  `refresh` and `server`.** Task 6 measured it: publishing the `markdown-file`
  kind renames its whole directory into place, and the kernel reports that as
  one event on the directory and **none at all** on the 202 files inside. The
  plan's per-file rule alone therefore announced zero new files, while the old
  `shutil.rmtree` of the live tree announced 202 `removed` ones — the page would
  have closed every panel and never reopened it. Three changes fix it, and all
  three are load-bearing: (1) `refresh._publish` renames the live directory to
  `<staging>/<kind>/retired` instead of deleting it in place, so its per-file
  deletes land under `.staging/` where the watcher ignores them; (2)
  `server.messages_for` fans a directory event out into one `changed` per
  `*.json` below it, which is the only way the page hears about the new files;
  (3) `messages_for` treats a `deleted` event whose path exists again as
  `changed`, because the kernel reports a delete inside a just-renamed directory
  under the directory's **old** name and the two are indistinguishable from the
  event alone. Dropping (3) makes the suite flaky under `-n auto`, not
  deterministically red — it lost the race roughly one run in four. Measured on
  this checkout after the fix: one refresh publishes exactly 203 `changed`, one
  `refreshed`, zero `removed`.
- **The state watcher debounces at 200ms, not watchfiles' 1600ms default.**
  `server.STATE_DEBOUNCE_MS`. The default alone would spend most of the
  two-second budget for an edit reaching the screen, before task 7's checkout
  debounce and the refresh itself.
- **`watch_state` dedupes within a batch.** The same view file is named by both
  the directory fan-out and a stale per-file event, so one refresh published 499
  messages for 203 files before the dedupe.
- **Starlette 1.6 has no `on_startup`.** `Starlette.__init__` takes
  `lifespan` only; `build_app` passes an `asynccontextmanager`. Task 7's checkout
  watchers hang off that same `_lifespan`, beside the state watcher.
- **`TestClient` without `with` runs no lifespan**, so the route tests start no
  watcher. `httpx.ASGITransport` buffers a whole response and hangs forever on
  the event stream, so the stream is exercised by `watch_state` plus `publish`,
  never through a test client.
- **Starlette warns that `httpx` is deprecated for `TestClient`** in favor of
  `httpx2`. It is a warning only, and `make check` is green with it.
- **The checkout watcher's `.git` filter is what stops a refresh loop.** Task 7
  built `dev_playbook.cloa_viewer.watch.watch_checkout(checkout, *, debounce_ms,
  stop)`, and its `outside_git(change, path)` filter drops every path with a
  `.git` component. A refresh runs `git ls-files` and `git rev-parse`, and git
  writes inside `.git` when it does, so without the filter each refresh would
  trigger the watcher that started it and the loop would never settle.
  `CHECKOUT_DEBOUNCE_MS` is 300.
- **The whole live-update loop is closed, and it costs about 0.17 seconds.**
  Measured on a two-file checkout through the app's own `lifespan_context`:
  appending a line to `alpha.md` published `markdown-file/alpha.md.json`,
  `markdown-file/index.md.json`, `index-tree.json`, and one `refreshed`, all
  within 0.17s of the write, against the two-second budget in "Done when".
  Nothing else arrived in the three seconds after, which is also the evidence
  that the `.git` filter holds.
- **`build_app` now starts a watcher per checkout.** `_lifespan` creates
  `watch_state()` plus one `watch.watch_checkout(checkout)` task per entry of
  `app.state.checkouts`, and cancels them all on shutdown. `TestClient` without
  `with` still runs no lifespan, so the route tests start no watcher; a test
  that does use `with TestClient(...)` will refresh its fixture checkout for
  real on every edit under it.

## Tasks

- [x] **Task 1: package skeleton and dependencies.** Create
  `src/dev_playbook/cloa_viewer/__init__.py` (zero bytes) and
  `src/dev_playbook/cloa_viewer/kinds/__init__.py` (zero bytes). In
  `pyproject.toml` add, without touching existing lines: a dependency group
  `viewer = ["starlette>=0.40", "uvicorn>=0.30", "watchfiles>=1.0", "jsonschema>=4.23"]`;
  to the `dev` group `"pytest-playwright>=0.6"` and `"httpx>=0.27"`; a
  `[tool.uv]` table with `default-groups = ["dev", "viewer"]`; and
  `[project.scripts]` with `cloa-viewer = "dev_playbook.cloa_viewer.cli:main"`.
  Create `src/dev_playbook/cloa_viewer/cli.py` with a `main(argv: list[str] | None = None) -> int`
  that parses `checkout` (zero or more paths) and `--port` (int, default
  8765) with argparse and returns 0; the real behavior comes in task 8. Test
  at `tests/dev_playbook/cloa_viewer/test_cli.py`: `main([])` returns 0, and
  `--port 9000` parses to 9000 (expose a `parse_args(argv) -> argparse.Namespace`
  for that). Run `uv sync`, then `uv run cloa-viewer --help` prints usage.
  Gate green.

- [x] **Task 2: the state module.** Create `src/dev_playbook/cloa_viewer/state.py`
  and `src/dev_playbook/cloa_viewer/schemas/envelope.schema.json`. The schema
  is JSON Schema draft 2020-12, `type: object`, `additionalProperties: false`,
  `required` all seven fields: `envelope` (const `1`), `kind` (string,
  pattern `^[a-z][a-z0-9-]*$`), `kind_version` (integer, minimum 1), `title`
  (string, minLength 1), `subject` (string or null), `stamp` (object,
  `additionalProperties: false`, required `commit` (string), `generated_at`
  (string), `generator` (string)), `payload` (object). Functions, all typed
  and docstringed: `state_root() -> Path` returns
  `$XDG_STATE_HOME/cloa-viewer` or `~/.local/state/cloa-viewer`;
  `checkout_dir(checkout: Path) -> Path` returns
  `state_root() / f"{checkout.resolve().name}-{sha256(str(checkout.resolve())).hexdigest()[:8]}"`;
  `head_commit(checkout: Path) -> str` runs `git rev-parse HEAD` with
  `no_git_env()`; `branch_name(checkout: Path) -> str` runs
  `git rev-parse --abbrev-ref HEAD`; `write_checkout_json(checkout: Path) -> Path`
  writes `checkout.json` with keys `path` (absolute string), `repo`
  (`canonical_repo_name`), `branch`, `head`; `envelope(kind: str, kind_version: int, title: str, subject: str | None, payload: dict, *, commit: str, generator: str) -> dict`
  builds the envelope with `generated_at` as UTC RFC 3339 with a `Z` suffix;
  `load_schema(name: str) -> dict` reads `schemas/<name>.schema.json` from the
  package with `importlib.resources`; `validate(instance: dict, schema: dict) -> None`
  raises `ContractError(ValueError)` whose message is
  `f"{error.json_path}: {error.message}"` from the first `jsonschema` error;
  `write_json(path: Path, data: dict) -> None` writes to `path.with_suffix(".tmp")`
  then `os.replace`, creating parents. Tests at
  `tests/dev_playbook/cloa_viewer/test_state.py`: an envelope built by
  `envelope()` validates; an envelope with an extra top-level key raises
  `ContractError` mentioning `$`; `checkout_dir` of two different paths with
  the same basename differ; `write_json` leaves no `.tmp` file behind. Gate
  green.

- [x] **Task 3: the registry and the index-tree kind.** Create
  `src/dev_playbook/cloa_viewer/registry.py` with
  `@dataclass(frozen=True) class Kind: name: str; version: int; per_subject: bool; generate: Callable[[Path], list[View]]`
  where `View` is a frozen dataclass `relpath: str; envelope: dict` (relpath is
  the path under the checkout directory, `index-tree.json` for a per-checkout
  kind, `markdown-file/<identity>.json` for a per-subject kind), the tuple
  `KINDS` listing every kind, and `kind_by_name(name: str) -> Kind` raising
  `KeyError` with the name. Create `src/dev_playbook/cloa_viewer/kinds/index_tree.py`
  exporting `KIND` (name `index-tree`, version 1, per_subject False) and
  `generate(checkout: Path) -> list[View]`, and
  `schemas/index-tree.schema.json`. Payload: `root` (a directory node) and
  `unindexed` (a list of file nodes sorted by identity). A directory node:
  `identity` (repo-relative path with trailing `/`, and `""` for the root),
  `title` (its `index.md` H1 text without `# `, or the directory name when
  the index is missing), `description` (the first sentence of the prose
  between the H1 and the first list item, cut at the first `. `, or `null`),
  `words` (sum of `words` below it), `children` (nodes in listing order, the
  directory's own `index.md` file node first). A file node: `identity`,
  `type`, `title`, `description` (frontmatter values or `null`), `words`
  (`len(body.split())` of the text after frontmatter), `exists` (false when a
  listing entry points at a file `git_files` does not list; then the other
  fields are `null` and `words` is 0). Walk: start at the root `index.md`;
  each listing entry is a markdown link found by `markdown_links` on a line
  starting with `- `; a target ending in `/index.md` recurses into that
  directory; any other target is a file node. Every `.md` path from
  `git_files(checkout)` not reached by the walk goes to `unindexed`. The
  envelope title is `Index tree`, subject `null`. Schema: `additionalProperties: false`
  everywhere, node fields as above, `children` recursive via `$defs`. Create
  `tests/dev_playbook/cloa_viewer/conftest.py` with a `checkout` fixture that
  builds, with `init_repo` and `commit_all`, a repo holding exactly these
  files: `index.md` = `# Fixture — index\n\nThe fixture bundle. Two documents and a directory.\n\n- [Alpha](/alpha.md) — The alpha document\n- [docs/](/docs/index.md) — The docs directory\n`;
  `alpha.md` = frontmatter `type: Guide`, `title: Alpha`, `description: The alpha document`,
  body `# Alpha\n\nOne two three [beta](/docs/beta.md) and [gone](/missing.md).\n\n## Second heading\n\nFour five.\n`;
  `docs/index.md` = `# docs — index\n\nThe docs directory.\n\n- [Beta](/docs/beta.md) — The beta document\n`;
  `docs/beta.md` = frontmatter `type: Guide`, `title: Beta`, `description: The beta document`, body `# Beta\n\nSix.\n`;
  `orphan.md` = `# Orphan\n\nSeven eight.\n` with no frontmatter. Tests at
  `tests/dev_playbook/cloa_viewer/kinds/test_index_tree.py` (with an empty
  `tests/dev_playbook/cloa_viewer/kinds/__init__.py` only if pytest needs it;
  prefer none): the root has children `index.md`, `alpha.md`, `docs/` in
  that order; `alpha.md` has `type` `Guide` and `words` equal to the literal
  count you compute by hand from the body above; `docs/` has `words` equal
  to the sum of its two files; `unindexed` is exactly `orphan.md`; the
  payload validates against the schema; a repo with no root `index.md`
  puts every file in `unindexed`. Gate green.

- [x] **Task 4: the markdown-file kind.** Create
  `src/dev_playbook/cloa_viewer/kinds/markdown_file.py` exporting `KIND`
  (name `markdown-file`, version 1, per_subject True) and `generate`, and
  `schemas/markdown-file.schema.json`. One view per `.md` path in
  `git_files(checkout)`, relpath `markdown-file/<identity>.json`, subject the
  identity, envelope title the frontmatter title or the identity. Payload:
  `type`, `title`, `description` (frontmatter or `null`); `words` as in task
  3; `headings`, a list of `{level, text, slug}` for every line outside
  fences matching `^(#{1,6}) (.+)$`, slug from `github_slug`; `links_out`, a
  list of `{target, status}` for every `markdown_links` hit on lines outside
  fences, in order, where status is `external` when the target starts with
  `http://`, `https://`, or `mailto:`, else `ok` when the target, with any
  `#fragment` removed and a leading `/` resolved against the checkout root
  or a relative path resolved against the file's directory, names a path in
  `git_files`, else `broken`; `links_in`, the sorted identities of the other
  markdown files whose `links_out` contain this file with status `ok`;
  `source`, the full file text. Compute all files' links first, then
  `links_in`. Schema with `additionalProperties: false` throughout. Add the
  kind to `KINDS` after `index-tree`. Tests at
  `tests/dev_playbook/cloa_viewer/kinds/test_markdown_file.py`: `alpha.md`
  has headings `Alpha` (level 1, slug `alpha`) and `Second heading` (level
  2, slug `second-heading`); its `links_out` are `/docs/beta.md` `ok` and
  `/missing.md` `broken`; `docs/beta.md` has `links_in` `["alpha.md"]`;
  `orphan.md` has `type` `null`; every payload validates. Gate green.

- [x] **Task 5: refresh.** Create `src/dev_playbook/cloa_viewer/refresh.py`
  with `refresh(checkout: Path) -> dict` and
  `schemas/refresh.schema.json`. Steps: `write_checkout_json`; record
  `started` (UTC RFC 3339) and `commit` (`head_commit`); for each kind in
  `KINDS`, inside `try`: call `generate`, validate each envelope against the
  envelope schema and then its payload against `load_schema(kind.name)`,
  write every view with `write_json` into a staging directory
  `<checkout_dir>/.staging/<kind>/`, then replace: for a per-checkout kind
  `os.replace` the single file into place; for a per-subject kind remove the
  existing `<checkout_dir>/<kind>/` tree with `shutil.rmtree` (if present)
  and `os.replace` the staged directory into place. On any exception, leave
  the existing files untouched, remove the staging directory, and record
  `status: "failed"`, `error: traceback.format_exc()`. Record per kind
  `{kind, status ("ok" | "failed"), count (files written or 0), error (string or null)}`.
  Write `refresh.json` with `started`, `finished`, `commit`, `generators`
  and return it. Schema: the shape above, `additionalProperties: false`.
  Tests at `tests/dev_playbook/cloa_viewer/test_refresh.py`: after `refresh`,
  `index-tree.json` and `markdown-file/alpha.md.json` exist and each
  validates against the envelope schema; the record has two `ok` entries
  with counts 1 and 5; when a kind's `generate` raises (monkeypatch a
  failing `Kind` into `KINDS`), the record says `failed` with a non-empty
  `error`, the other kind's files still exist, and no `.staging` directory
  remains; `checkout.json` holds the fixture's absolute path. Gate green.

- [x] **Task 6: the server routes and the event stream.** Create
  `src/dev_playbook/cloa_viewer/server.py` with
  `build_app(checkouts: list[Path], dist: Path) -> starlette.applications.Starlette`.
  Routes: `GET /` serves `dist / "index.html"`; mount `/assets` as
  `StaticFiles(directory=dist / "assets")`; `GET /api/kinds` returns
  `[{name, version, per_subject}]` from `KINDS`; `GET /api/schemas/{name}`
  returns `load_schema(name)` or 404; `GET /api/checkouts` returns
  `[{dir, path, repo, branch, head}]` (dir is `checkout_dir(c).name`, the
  rest from `checkout.json`); `GET /api/checkouts/{dir}/files` returns the
  sorted relpaths of every `*.json` under that checkout directory except
  `checkout.json`, `refresh.json`, and anything under `.staging/`;
  `GET /api/checkouts/{dir}/view/{relpath:path}` returns that file's JSON
  or 404; `GET /api/checkouts/{dir}/refresh` returns `refresh.json`;
  `POST /api/checkouts/{dir}/refresh` runs `refresh` in
  `asyncio.to_thread` and returns the record; `GET /api/events` is a
  server-sent events stream (`text/event-stream`, a
  `StreamingResponse` over an `asyncio.Queue` per subscriber) whose
  first message is `data: {"event": "connected"}` and whose later messages
  are `data: {"event": "changed" | "removed", "checkout": dir, "path": relpath}`.
  An unknown `dir` is a 404 everywhere. The state watcher: a startup task
  running `watchfiles.awatch(state_root())` that, for each change to a
  `*.json` file not under `.staging/` and not named `checkout.json` or
  `refresh.json`, publishes `changed` (added or modified) or `removed`
  (deleted) to every subscriber; a change to `refresh.json` publishes
  `{"event": "refreshed", "checkout": dir}`. Keep the subscriber set and a
  `publish(message: dict) -> None` function at module level so tests can
  call it. Tests at `tests/dev_playbook/cloa_viewer/test_server.py` using
  `starlette.testclient.TestClient` after `refresh(checkout)` with a
  temporary `dist` holding a one-line `index.html` and an empty `assets/`:
  `/api/checkouts` lists the fixture with its `head`; `/files` includes
  `index-tree.json` and `markdown-file/alpha.md.json`; `/view/index-tree.json`
  returns an object with `kind` `index-tree`; `/view/nope.json` is 404;
  `/api/schemas/envelope` returns an object with `required`; `POST refresh`
  returns a record with two generators. Test `publish` by subscribing a
  queue and asserting the message arrives. Gate green.

- [x] **Task 7: the checkout watcher.** Create
  `src/dev_playbook/cloa_viewer/watch.py` with
  `async def watch_checkout(checkout: Path, *, debounce_ms: int = 300, stop: asyncio.Event | None = None) -> None`
  that runs `watchfiles.awatch(checkout, debounce=debounce_ms, stop_event=stop, watch_filter=...)`
  ignoring every path with a `.git` component, and on each batch calls
  `await asyncio.to_thread(refresh, checkout)`. Wire it into `build_app`
  as one startup task per checkout, stopped on shutdown. Tests at
  `tests/dev_playbook/cloa_viewer/test_watch.py`: run `watch_checkout` with
  `debounce_ms=50` as a task, append a line to `alpha.md`, wait until
  `markdown-file/alpha.md.json` changes (poll up to 5 seconds on its
  `words`), then set `stop`; the new `words` is the old plus the number of
  words you appended. Gate green.

- [ ] **Task 8: the command.** In `cli.py`, `main` now: resolves each
  `checkout` argument (default: the output of `git rev-parse --show-toplevel`
  in the current directory) to an absolute `Path`; locates `dist` at
  `Path(__file__).parent / "web" / "dist"` and, if `dist / "index.html"`
  is missing, prints `page not built: run make web` to stderr and returns
  2; runs `refresh` for each checkout and prints one line per failed
  generator to stderr as `refresh failed: <kind> in <checkout>`; prints
  `cloa-viewer at http://127.0.0.1:<port>/` to stdout; then calls
  `uvicorn.run(build_app(checkouts, dist), host="127.0.0.1", port=port, log_level="warning")`.
  Split so `main` calls a module-level `serve(app, port)` that tests can
  monkeypatch. Tests in `test_cli.py`: with a fake `dist` directory
  missing `index.html`, `main([str(checkout)])` returns 2 and the message
  is on stderr (`capsys`); with a fake `dist/index.html` present and `serve`
  monkeypatched to record its arguments, `main([str(checkout), "--port", "9001"])`
  returns 0, `refresh.json` exists, and `serve` received port 9001. Gate
  green.

- [ ] **Task 9: the web project, the build target, the type check hook.**
  Create `src/dev_playbook/cloa_viewer/web/` with `package.json` (name
  `cloa-viewer-web`, private, scripts `build` = `tsc --noEmit && vite build`,
  `typecheck` = `tsc --noEmit`, `dev` = `vite`; dependencies `react`,
  `react-dom`, `ajv`, `markdown-it`; devDependencies `typescript`, `vite`,
  `@vitejs/plugin-react`, `@types/react`, `@types/react-dom`,
  `@types/markdown-it`; take the current versions `npm install` resolves and
  commit `package-lock.json`), `tsconfig.json` (strict, `jsx: react-jsx`,
  `target: ES2022`, `module: ESNext`, `moduleResolution: bundler`,
  `noEmit`), `vite.config.ts` (react plugin, `build.outDir: "dist"`,
  `server.proxy` sending `/api` to `http://127.0.0.1:8765`), `index.html`
  mounting `src/main.tsx`, `src/main.tsx` rendering `<App />` from
  `src/App.tsx`, and `src/App.tsx` rendering the text `cloa-viewer` for now.
  Append to `.gitignore`: `src/dev_playbook/cloa_viewer/web/node_modules/`
  and `src/dev_playbook/cloa_viewer/web/dist/`. Append to `Makefile`, after
  the existing targets and added to `.PHONY`: `web:` with recipe
  `npm --prefix src/dev_playbook/cloa_viewer/web ci` then
  `npm --prefix src/dev_playbook/cloa_viewer/web run build`; and
  `web-check:` with recipe `npm --prefix src/dev_playbook/cloa_viewer/web run typecheck`.
  Append to the `- repo: local` block in `.pre-commit-config.yaml` a hook
  `id: web-typecheck`, `name: web typecheck`, `entry: make web-check`,
  `language: system`, `pass_filenames: false`,
  `files: ^src/dev_playbook/cloa_viewer/web/`. Run `make web`; confirm
  `uv run cloa-viewer --port 8765` prints the address (stop it) and
  `curl http://127.0.0.1:8765/` returns the page. Gate green.

- [ ] **Task 10: the page shell.** In the web project create `src/api.ts`
  (typed fetchers for every `/api` route from task 6, and an `EventSource`
  wrapper `subscribe(onMessage, onStateChange)` that reports connected or
  disconnected), `src/validate.ts` (fetch the envelope schema and each kind
  schema once, cache them, `validateView(json): {ok: true, view} | {ok: false, error: string}`
  using Ajv with `allErrors: false`, the error string being the instance
  path and message of the first error), `src/store.ts` (React state: the
  selected checkout, a map from view path to a validated view or an error,
  the refresh record, the connection state, the list of open panel paths),
  `src/components/ErrorPanel.tsx` (red left border, the file path as
  heading, the error text), `src/components/Banner.tsx` (full-width bar at
  the top reading `Disconnected from cloa-viewer` while disconnected),
  `src/components/TopBar.tsx` (the checkout's `repo` and `branch`, a
  `Refresh` button posting to the refresh route, and a status reading
  `Refreshed <finished> at <commit first 7>` in normal color, or in red with
  `N failed` when any generator failed; clicking a red status opens an
  error panel with the error text), `src/components/PanelStack.tsx` (the
  open views in order, newest first, each with a title bar holding the view
  `title` and a close button, the body rendered by the kind's renderer from
  `src/kinds/index.ts`, a map from kind name to component, or an
  ErrorPanel reading `no renderer for kind <kind>`), and `src/App.tsx`
  composing Banner, TopBar, a left column reading `tree` for now, and
  PanelStack. On load: fetch checkouts, select the first, fetch its file
  list, fetch and validate every view, subscribe to events; on `changed`
  refetch and revalidate that path, on `removed` drop it and close its
  panel, on `refreshed` refetch the record. Styles in `src/app.css`: a
  three-region grid, left column 320px, no framework. `make web` succeeds;
  gate green.

- [ ] **Task 11: the tree renderer.** Create
  `src/kinds/index-tree/IndexTree.tsx` rendering the `index-tree` view from
  the store in the left column: a directory row shows a disclosure
  triangle, the title, the description in muted text, and the word count
  right-aligned; a file row shows the title (or identity when title is
  null), the description, and the word count, and is dimmed with the label
  `missing` when `exists` is false; the root starts expanded, other
  directories collapsed, expansion held in component state; the
  `unindexed` list renders last as a directory row titled `Unindexed` with
  the count of entries. Clicking a file row opens `markdown-file/<identity>.json`
  in the panel stack (moving it to the top if already open); when that path
  is not in the store, open an error panel reading `no view file for <identity>`.
  Register the kind in `src/kinds/index.ts`. `make web` succeeds; gate
  green.

- [ ] **Task 12: the file panel and the Playwright test.** Create
  `src/kinds/markdown-file/MarkdownFile.tsx`: a facts row (`type`, `words`,
  heading count), a `Headings` list indented by level, `Links out` as a
  list with the status shown as a badge (`ok`, `broken`, `external`),
  `Links in` as a list, then the source rendered with `markdown-it`
  (`html: false`). A link in `Links out` or `Links in` whose target is a
  markdown file with a view in the store opens that file's panel. Register
  the kind. Then in `tests/dev_playbook/cloa_viewer/test_cli.py` add
  `test_page_shows_tree_and_updates(checkout, page, tmp_path, monkeypatch)`:
  fail immediately with the message `run make web first` if
  `dist/index.html` is missing; pick a free port with a bound socket;
  start `uv run cloa-viewer <checkout> --port <port>` as a subprocess with
  `XDG_STATE_HOME` set to `tmp_path` and `cwd` the repo root; wait up to
  10 seconds for `GET /api/checkouts` to answer; `page.goto` the address;
  expect the text `Alpha` in the tree; click it; expect a panel whose title
  is `Alpha` and whose body contains `Second heading`; append `\nnine ten\n`
  to `alpha.md`; expect the panel's word count to increase by 2 within 5
  seconds without reload; terminate the subprocess in a `finally`. Gate
  green, which now includes this test.
