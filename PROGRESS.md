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
