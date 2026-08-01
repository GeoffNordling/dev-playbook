# Plan: a utilization and attribution prototype over the local measurement store

A Ralph loop works this file top to bottom. Each iteration, a fresh agent with
no memory reads this plan and the progress log, does the first unchecked task,
checks it off, and commits. Everything it needs to act is here — including the
Working notes below, where earlier iterations leave facts you will need. Add to
them whenever you learn something a future iteration would otherwise rediscover.

## Done when

- `docs/measurement-prototype.md` is still accurate about what the code does; any
  drift is fixed as part of the task that caused it.
- The capture hook keeps `file_path` on Read/Edit/Write rows and `tool_input` on
  Skill rows, while still dropping file contents and diff bodies.
- A read-only loader turns the events table into a tidy dataframe without ever
  writing to the store.
- An interval table exists with columns `start`, `end`, `state`, `session_id`,
  `confidence`, computed in memory on each run and never persisted.
- Every gap between a `Stop` and the next submit carries a fitted presence
  probability rather than a hand-picked threshold.
- Both the session-level and global-level views derive from that one interval
  table, so they cannot disagree.
- Rows carry repo attribution from `cwd`, issue attribution from `gh` commands
  with reads and writes kept separate, and skill attribution from both
  invocation paths.
- One command produces a Plotly timeline: time left to right, one lane per
  session, gapped bars showing activity, with the lane key pivotable to repo or
  issue.
- `make check` is green.

## Working notes

- The store is `~/.local/share/claude-measure/events.db` — SQLite, WAL, one
  `events` table, ~11k rows. **Always open it read-only** via
  `file:...?mode=ro`. It is live: other sessions write to it while you read, so
  row counts drift between queries within one iteration.
- [docs/measurement-prototype.md](/docs/measurement-prototype.md) is the
  authority on what the store contains, the eight assumptions, and the
  attribution findings. Read it before task 2. Do not re-derive it; if you find
  it wrong, fix it in the same commit.
- New code goes in `src/dev_playbook/measure/`. `src/dev_playbook/filegraph/`
  and `src/dev_playbook/transcript_export/` are the nearest existing precedents
  for a multi-module data pipeline in this repo — match their structure.
- Dependencies today are pyyaml only. pandas, plotly, and a mixture-fitting
  library are new. Add them as an optional extra (e.g. a `measure` extra in
  `pyproject.toml`), not to core dependencies — this repo is a linting playbook
  that consumer repos install, and it should not pull pandas for them.
- The check gate is `make check`. It runs pytest plus pre-commit, including
  `playbook-lint`, which enforces doc references, OKF frontmatter, index
  entries, Python style, and testing conventions. New docs need an index entry;
  new modules need tests.
- Conventions to follow: [Python Style](/standards/python/style.md),
  [Testing Conventions](/standards/testing/conventions.md). Fail loud — no
  silent skips or defensive fallbacks around missing or malformed rows.
- The capture hook is `dotfiles/dot-claude/hooks/measure-event`; the trim rule
  lives in its `for_storage` function. It is stdlib-only by design and must stay
  that way — it runs on every event of every session.
- Capture changes are forward-only. Existing rows keep their current shape, so
  any code reading `file_path` or Skill `tool_input` must tolerate its absence
  on older rows — that absence is a fact about capture history, not an error.
- The hook change rides this branch, while the live `~/.claude/hooks/` is stowed
  from the main checkout, so the real store gains no `file_path` row until this
  merges. Expect none when querying it; test attribution against fixtures.
- A Read/Edit/Write row now stores `tool_input` reduced to `file_path` alone. A
  reader meets three shapes: the key absent (an older row, or an input that was
  not a JSON object), `{}` (an input naming no file), or `{"file_path": ...}`.
- Tests load the extensionless hook by path with `SourceFileLoader` — see
  `tests/test_measure_event.py`. Reuse that; do not add a `.py` shim.
- The `measure` extra exists in `pyproject.toml`, and the `dev` group
  self-references `dev-playbook[measure]`, so `uv run` (and therefore
  `make check`) has it. Adding another dependency means `uv lock` + `uv sync`,
  which need the network the sandbox blocks — run those two with the sandbox
  disabled. pandas and numpy are locked; **plotly is not in the uv cache**, so
  task 8's lock is a real download.
- `dev_playbook.measure.store.load_events(db_path=DEFAULT_STORE)` is the one
  door onto the store. Columns: `id`, `received_at` (datetime64[us, UTC]),
  `payload` (the parsed dict, for event-specific fields), `event`,
  `session_id`, `prompt_id`, `cwd`, `transcript_path`. It raises `StoreError`
  on a payload that is not a JSON object or that lacks `hook_event_name`,
  `session_id`, `cwd` or `transcript_path` — all four hold on every row of the
  real store. `prompt_id` is the one that is legitimately None (86 rows).

- `dev_playbook.measure.clean` holds the four techniques, each
  `frame -> Cleaning(technique, frame, removed)`. Compose them in the order
  they appear in the module; each returns a new frame with a fresh
  `RangeIndex`, so an index from before a cleaning step is meaningless after
  it. `collapse_expansions` keeps the **submit** row and folds the expansion's
  `command_name`/`command_args` onto its payload — that is where task 7's
  human-typed skill attribution comes from.
- Store facts the cleaning rests on, measured on the real store: a `Stop`
  carries the same `prompt_id` as its submit, so anything keyed on `prompt_id`
  alone hits both; expansions pair 1:1 with submits (109 of 109, none
  duplicated, none unpaired); and 1312 of 1522 `SubagentStop` rows have an
  empty `agent_type` against only 233 `SubagentStart` rows, so phantoms are
  the majority, not the exception.

- `dev_playbook.measure.intervals` owns the interval table. Build **every** new
  row through `intervals.interval_frame(rows)` — it is the one constructor for
  the schema, and it pins `start`/`end` to `datetime64[us, UTC]` and
  `confidence` to float even when there are no rows, so frames from different
  stages concat cleanly. `definitive_intervals(events, window=None)` returns
  `Intervals(frame, unresolved)`; omit the window and the frame's own span is
  used. Feed it cleaned events — it does not clean.
- Measured over the whole real store, cleaned: 583 `claude_active` rows
  (14 h 34 m), 100 `interrupted`, 110 `dormant`, 5 unresolved turns, across a
  4-day window and 56 sessions. Sanity numbers for any later change.
- **Never sum `interrupted` into Claude-active time.** Median 29 s but maximum
  15.7 h — an interrupt before the human left for the night swallows the night.
  Task 5 should consider that an interrupt's tail is the same unobserved thing
  as a `Stop`-to-submit gap and could take the same fitted probability.
- 102 `Stop` rows in the cleaned store match no submit; that is expected, not a
  defect — dropping the task-notification pseudo-prompts strands their stops.
  Zero submits or stops have a null `prompt_id`, no `prompt_id` carries two
  stops, and no stop precedes its submit, so pairing by `prompt_id` is exact.
- Test frames come from `tests/measure_fakes.py` (`a_payload`, `a_frame`, and
  `at(n)` for the timestamp of the nth payload). `pyproject.toml` already puts
  `tests` on `pythonpath`, so import it bare: `from measure_fakes import ...`.
  `a_timed_frame([(second, payload), ...])` is the one to use when a derivation
  turns on how long something took — `a_frame` is now a wrapper on it.

- `dev_playbook.measure.presence` owns the graded rows. `stop_gaps` pairs each
  `Stop` with the submit *immediately* after it in its session (a `Stop` with
  another `Stop` before that submit opens no gap, or the inner turn would be
  counted twice); `fit_presence(seconds)` returns the `MixtureFit`;
  `presence_intervals(events)` returns `Presence(frame, fit)` with one
  `human_present` row per gap at the fitted confidence, built through
  `intervals.interval_frame`. Feed it cleaned events.
- **No mixture-fitting library was added.** The fit is a hand-written
  tied-variance EM over `math` — so plotly is the only dependency left needing
  a real `uv lock` download, at task 8. The tie is load-bearing, not laziness:
  free variances score better but put the store's shortest gaps in the broad
  component, so presence stops being monotone in gap length. Do not free them.
- Measured on the real store: 533 gaps, 128 hours of them against ~15 h of
  `claude_active`; working mode 73 s carrying 98.3 %, away mode 5.8 h carrying
  1.7 %, even odds at 2 h 14 m, ~36 expected present hours. The store is live,
  so a rerun drifts these by a few minutes.

## Tasks

- [x] Extend the capture hook so a `PostToolUse` for Read, Edit, or Write keeps
      only `file_path` from `tool_input`, and one for Skill keeps `tool_input`
      whole, while every other non-Bash tool keeps behaving as it does today and
      file contents, diff bodies, and tool responses are still dropped. Keep the
      hook stdlib-only. Add tests covering each tool class, and update the
      hook's module docstring and the capture section of
      `docs/measurement-prototype.md` to match.
- [x] Create `src/dev_playbook/measure/` with a read-only loader that opens the
      store via a `mode=ro` URI, reads the `events` table, parses each payload,
      and returns a tidy dataframe with one row per event and the common fields
      promoted to columns. Add the optional dependency extra. Cover the loader
      with tests against a small fixture database built in the test, never
      against the real store.
- [x] Add the four row-cleaning techniques from the prototype doc as separate,
      individually testable functions: collapse expansion/submit pairs sharing a
      `prompt_id`, drop phantom `SubagentStop` rows, drop task-notification
      pseudo-prompts, and drop ghost sessions. Each returns a filtered frame and
      reports how many rows it removed, so a caller can show its own blind spots.
- [x] Build the definitive part of the interval table: Claude-active spans from
      each submit to its `Stop`, dormant spans outside each session's first and
      last event, and interrupt detection where two submits share a session with
      no `Stop` between them. Emit the interval schema `start`, `end`, `state`,
      `session_id`, `confidence`, with confidence 1.0 for these rows.
- [x] Extract every `Stop`-to-next-submit gap, fit a two-component mixture to
      the observed durations, and attach a presence probability to each gap.
      Emit those gaps as interval rows with confidence set to the fitted
      probability. Record the fitted parameters in the run's output so the model
      is inspectable rather than hidden.
- [ ] Add the global level: union the per-session intervals across the machine
      so a moment counts as Claude-active if any session is mid-turn, and as
      human-present if any session shows presence. Same interval schema, no
      `session_id`. Test that session and global rollups agree on total
      Claude-active time.
- [ ] Add attribution columns: repo from each row's `cwd`, GitHub issue from
      `gh` commands in Bash `tool_input` with write signals (edit, close,
      comment) and read signals (view) kept as separate columns, and skills from
      both `UserPromptExpansion.command_name` and Skill-tool rows. Never merge
      the read and write issue signals into one column.
- [ ] Build the Plotly timeline view: time on the x axis, one lane per session
      stacked vertically, bars drawn only where there is activity so gaps read as
      gaps, and confidence rendered so inferred presence is visibly weaker than
      observed. Make the lane key a parameter so the same view pivots to repo or
      issue. Write a self-contained HTML file. Design details are the
      implementer's call.
- [ ] Add one command that runs the whole pipeline over a chosen time window and
      writes the HTML view, wired as a console script in `pyproject.toml`.
      Document how to run it in `docs/measurement-prototype.md`, replacing the
      "Work required" section with what now exists and what remains.
