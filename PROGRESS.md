# Progress log

The running memory of this Ralph loop. Each iteration appends one line below —
what it did and what is next — newest at the bottom. A fresh agent reads this
before starting, to see what the iterations before it already did.

## Log

<!-- iterations append one line each below this line -->
- F1 done: `render_session` now parses the full document with ElementTree.fromstring and raises a clear ValueError on malformed XML (`_assert_well_formed`); added pass/raise tests. Next: F2 forks conservation guard.
- F2 done: `reconstruct_forks` now runs `_assert_conserved` — the multiset of output `source_uuid`s (live path + every abandoned-branch tree node) must equal the input set, else it raises; added multi-fork conservation test and a constructed-violation test. Next: F3 render interrupts.
- F3 done: `classify` now recognizes interrupts (`source_subtype="interrupted"` or content marker) BEFORE the system→DROP rule, so real system-typed interrupts render `<interrupted/>` instead of being dropped (verified: session 4a157204 yields 3 tags); fixed classify/render fixtures to the real `source_type="system"` shape and added a survives-keep_messages test + a live interrupt-tag assertion. Next: F4 marker-stripping bare markers + fail-loud mismatch.
- F4 done: broadened `_TOOL_MARKER` to catch TitleCase bare markers (`[TaskList]`, `[Exiting Plan Mode]`) while excluding lowercase heredoc brackets; `strip_tool_markers` now raises on marker-count != tool_call_count instead of silently leaking (verified 0 mismatches across 5064 real messages); fixed ANSI + subagent fixtures to carry markers; added bare-marker/heredoc/mismatch unit tests + a live no-leak assertion. Next: F5 dedup rule 2 (match whole message, not just text).
- F5 done: `collapse_adjacent_repeats` now compares a fingerprint of every distinguishing field (role, content, tool_calls incl. result content, thinking_text, source_parent_uuid), so a same-prose/different-tool-result retry is preserved while re-emitted doubles still collapse; extended `msg` test helper with tool_calls/thinking/source_parent_uuid and added triple-collapse + retry-preserved tests. Next: F6 live tests fail (not skip) when daemon unreachable.
- F6 done: removed the `skipif(not _RECENT, …)` pytestmark and the exception-swallowing in `_recent_ids` from `test_transcript_export_live.py` — `_recent_ids` now calls `session_list()` directly so an unreachable daemon raises and the live suite fails loudly instead of skipping. Next: F7 document transcript-export in tools/README.md.
