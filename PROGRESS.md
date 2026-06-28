# Progress log

The running memory of this Ralph loop. Each iteration appends one line below —
what it did and what is next — newest at the bottom. A fresh agent reads this
before starting, to see what the iterations before it already did.

## Log

<!-- iterations append one line each below this line -->
- T1 done: scaffolded `tools/transcript_export/` (`__init__.py`, `cli.py` with `main`→usage), thin shim `tools/bin/transcript-export`, added `transcript_export/` to Makefile mypy target, one unit test; `make -C tools check` green. Next: T2 — AgentsView client.
- T2 done: added `transcript_export/client.py` (`session_list`/`session_get`/`session_messages` over an injectable `runner`, `AgentsViewError` fail-loud, page-100 paging on last_ordinal+1) + 6 unit tests in `tests/test_transcript_export_client.py`; `make -C tools check` green (187 passed). Next: T3 — message model + resume dedup.
- T3 done: added `transcript_export/model.py` — frozen `Message`/`ToolCall` dataclasses, `message_from_row`/`tool_call_from_row`, `collapse_resume_duplicates` (rule 1, keep-first by source_uuid), `normalize_messages` (map rows + dedup, order preserved) + 7 unit tests in `tests/test_transcript_export_model.py`; `make -C tools check` green (194 passed). Next: T4 — fork reconstruction (tree from source_parent_uuid, live path, abandoned branches).
- T4 done: added `transcript_export/forks.py` — `reconstruct_forks` returns `ForkReconstruction(live_path, abandoned_branches keyed by fork point)` built from the `source_parent_uuid`→`source_uuid` tree, live path = root→tip ancestor chain of the highest-ordinal message, abandoned heads grouped by parent (root-level forks key on the absent/None parent), `MessageNode` preserves nested forks; 9 unit tests in `tests/test_transcript_export_forks.py`; `make -C tools check` green (203 passed). Next: T5 — record classification + dedup rule 2.
- T5 done: added `transcript_export/classify.py` — `MessageKind` enum, `classify` (keys off source_type/source_subtype, compaction-boundary checked before system->drop, unexpected source_type raises), `collapse_adjacent_repeats` (dedup rule 2), `keep_messages` (drop plumbing then rule 2); 15 unit tests in `tests/test_transcript_export_classify.py`; `make -C tools check` green (218 passed). Next: T6 — render header + turns + thinking.
- T6 done: added `transcript_export/render.py` — `escape` (all five entities, `&` first; reused for text + attrs), `render_session_open` (maps `session get` payload → `<session>` attrs, `id` required/fail-loud, optionals omitted when None, zero counts kept), `render_turn` (classify-dispatched `<user>`/slash/`<assistant>` with `<thinking>`, fails loud on non-turn); live-verified header keys; 17 unit tests (ElementTree round-trip) in `tests/test_transcript_export_render.py`; `make -C tools check` green (235 passed). NOTE: turn-text marker stripping deferred to T7. Next: T7 — render tool calls (+ turn-text marker stripping).
