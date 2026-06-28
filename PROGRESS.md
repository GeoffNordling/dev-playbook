# Progress log

The running memory of this Ralph loop. Each iteration appends one line below —
what it did and what is next — newest at the bottom. A fresh agent reads this
before starting, to see what the iterations before it already did.

## Log

<!-- iterations append one line each below this line -->
- T1 done: scaffolded `tools/transcript_export/` (`__init__.py`, `cli.py` with `main`→usage), thin shim `tools/bin/transcript-export`, added `transcript_export/` to Makefile mypy target, one unit test; `make -C tools check` green. Next: T2 — AgentsView client.
- T2 done: added `transcript_export/client.py` (`session_list`/`session_get`/`session_messages` over an injectable `runner`, `AgentsViewError` fail-loud, page-100 paging on last_ordinal+1) + 6 unit tests in `tests/test_transcript_export_client.py`; `make -C tools check` green (187 passed). Next: T3 — message model + resume dedup.
- T3 done: added `transcript_export/model.py` — frozen `Message`/`ToolCall` dataclasses, `message_from_row`/`tool_call_from_row`, `collapse_resume_duplicates` (rule 1, keep-first by source_uuid), `normalize_messages` (map rows + dedup, order preserved) + 7 unit tests in `tests/test_transcript_export_model.py`; `make -C tools check` green (194 passed). Next: T4 — fork reconstruction (tree from source_parent_uuid, live path, abandoned branches).
