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

## Tasks

- [ ] Extend the capture hook so a `PostToolUse` for Read, Edit, or Write keeps
      only `file_path` from `tool_input`, and one for Skill keeps `tool_input`
      whole, while every other non-Bash tool keeps behaving as it does today and
      file contents, diff bodies, and tool responses are still dropped. Keep the
      hook stdlib-only. Add tests covering each tool class, and update the
      hook's module docstring and the capture section of
      `docs/measurement-prototype.md` to match.
- [ ] Create `src/dev_playbook/measure/` with a read-only loader that opens the
      store via a `mode=ro` URI, reads the `events` table, parses each payload,
      and returns a tidy dataframe with one row per event and the common fields
      promoted to columns. Add the optional dependency extra. Cover the loader
      with tests against a small fixture database built in the test, never
      against the real store.
- [ ] Add the four row-cleaning techniques from the prototype doc as separate,
      individually testable functions: collapse expansion/submit pairs sharing a
      `prompt_id`, drop phantom `SubagentStop` rows, drop task-notification
      pseudo-prompts, and drop ghost sessions. Each returns a filtered frame and
      reports how many rows it removed, so a caller can show its own blind spots.
- [ ] Build the definitive part of the interval table: Claude-active spans from
      each submit to its `Stop`, dormant spans outside each session's first and
      last event, and interrupt detection where two submits share a session with
      no `Stop` between them. Emit the interval schema `start`, `end`, `state`,
      `session_id`, `confidence`, with confidence 1.0 for these rows.
- [ ] Extract every `Stop`-to-next-submit gap, fit a two-component mixture to
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
