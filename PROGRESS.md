# Progress log

The running memory of this Ralph loop. Each iteration appends one line below —
what it did and what is next — newest at the bottom. A fresh agent reads this
before starting, to see what the iterations before it already did.

## Log

<!-- iterations append one line each below this line -->
- T1 done: scaffolded `tools/transcript_export/` (`__init__.py`, `cli.py` with `main`→usage), thin shim `tools/bin/transcript-export`, added `transcript_export/` to Makefile mypy target, one unit test; `make -C tools check` green. Next: T2 — AgentsView client.
