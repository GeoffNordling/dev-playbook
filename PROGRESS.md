# Progress log

The running memory of this Ralph loop. Each iteration appends one line below —
what it did and what is next — newest at the bottom. A fresh agent reads this
before starting, to see what the iterations before it already did.

## Log

<!-- iterations append one line each below this line -->

- Task 1: capture hook now keeps `file_path` on Read/Edit/Write and `tool_input`
  whole on Skill, still dropping every `tool_response`; 12 tests in
  `tests/test_measure_event.py` and `docs/measurement-prototype.md` updated to
  match. Next: task 2, the read-only loader in `src/dev_playbook/measure/`.
- Task 2: `src/dev_playbook/measure/store.py` loads the store through a
  `mode=ro` URI into a tidy frame (payload is the authority, not the promoted
  columns); `measure` extra added and pulled into the dev group; 13 tests in
  `tests/test_measure_store.py` against fixture databases. Next: task 3, the
  four row-cleaning functions.
- Task 3: `src/dev_playbook/measure/clean.py` adds the four techniques as
  separate functions, each returning `Cleaning(technique, frame, removed)`;
  19 tests in `tests/test_measure_clean.py` build frames in memory through
  `store.event_row`. Next: task 4, the definitive interval rows.
- Task 4: `src/dev_playbook/measure/intervals.py` derives the definitive rows —
  `claude_active`, `interrupted`, `dormant`, all at confidence 1.0 — through the
  one `interval_frame` constructor; frame builders moved to
  `tests/measure_fakes.py` and 22 tests added; the doc's interval section now
  matches the code and records that an `interrupted` span is a loose upper
  bound. Next: task 5, the `Stop`-to-submit gaps and the fitted mixture.
- Task 5: `src/dev_playbook/measure/presence.py` extracts every
  `Stop`-to-next-submit gap and grades it with a tied-variance two-component
  lognormal mixture fitted by hand-written EM (no new dependency); the fit
  travels with the rows and prints through `MixtureFit.summary`; 22 tests in
  `tests/test_measure_presence.py`, `a_timed_frame` added to the fakes, and the
  doc's section 3 now carries the fitted numbers and why the variance is tied.
  Next: task 6, the global union of the per-session intervals.
- Task 6: `src/dev_playbook/measure/rollup.py` rolls the table up across the
  machine — a sweep cutting at every bound, union for the active and presence
  states, intersection for `dormant`, complement where graded rows overlap — plus
  `state_seconds`/`expected_seconds` for totalling either level; 17 tests in
  `tests/test_measure_rollup.py`, and the doc's section 2 now carries the global
  rule and what the level costs (14.6 session-hours of Claude-active time are
  12.6 machine-hours). Next: task 7, the repo, issue, and skill attribution
  columns.
- Task 7: `src/dev_playbook/measure/attribute.py` adds `repo`, `issue_writes`,
  `issue_reads` and `skill` to a cleaned event frame — repo from the first
  segment under `~/workspace` so worktrees fold into their repo, issues from the
  `gh` verbs with reads and writes never merged and each reference qualified
  `<repo>#<number>`, skills from both invocation paths; 27 tests in
  `tests/test_measure_attribute.py`, and the doc's attribution section now
  carries the parse rule and re-measured coverage. Next: task 8, the Plotly
  timeline view.
- Task 8: `src/dev_playbook/measure/timeline.py` draws the interval table as
  gapped bars — one lane per session, confidence as opacity so inferred presence
  reads faint, dormancy built but switched off in the legend, and `laned` pivoting
  the same table to a repo, issue or skill lane by what was in force at each
  interval's start; plotly added to the `measure` extra and locked, `_human`
  promoted to `presence.human_seconds`, 24 tests in
  `tests/test_measure_timeline.py`, and a real-store run gives 1353 rows over 62
  session lanes in a 5.1 MiB self-contained page. Next: task 9, the console-script
  command that runs the pipeline over a window and rewrites the doc's
  "Work required".
- Task 9: `src/dev_playbook/measure/cli.py` runs the whole pipeline over a chosen
  window and writes the page, wired as the `measure-timeline` console script; the
  run prints what it dropped, how many turns are still open, the fitted model, and
  both levels' wall and expected totals per state; 24 tests in
  `tests/test_measure_cli.py` against a fixture store, and the doc's "Work
  required" is now "The pipeline" (how to run it, plus a stage-by-module table)
  followed by "What remains". Every task in the plan is complete.
