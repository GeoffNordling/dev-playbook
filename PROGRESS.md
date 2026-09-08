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
