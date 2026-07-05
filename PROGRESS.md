# Progress log

The running memory of this Ralph loop. Each iteration appends one line below —
what it did and what is next — newest at the bottom. A fresh agent reads this
before starting, to see what the iterations before it already did.

## Log

<!-- iterations append one line each below this line -->
- Task 1 done: consolidated `tools/` into the standard layout (src/dev_playbook package, scripts/, tests/, one root pyproject/Makefile/uv.lock), rewrote imports/path-shims/docs; `make check` green (405 pass, 2 deselected). Surprise recorded in Working notes: python-lint/ref-check use a `python3` shebang that trips repo-audit's script-shebang rule (task 6 must resolve). Next: task 2 — drop canonical ci.yml and .python-version.
- Task 2 done: replaced `.github/workflows/ci.yml` and created root `.python-version`, both `cmp`-verified byte-identical to `standards/canonical/`. repo-audit down to 11 findings (all mapping to tasks 4/5/6); `make check` green (405 pass, 2 deselected). Next: task 3 — rewrite scripts/README.md.
- Task 3 done: rewrote scripts/README.md for the post-move reality (heading `# Scripts`, root `uv sync`, `src/dev_playbook/` shared libs + subpackages, generic `entry:` mechanism, `judgments-run` added to the utility table); no `tools/`/`lib/` paths remain; `make check` green (405 pass, 2 deselected). Discovered `.pre-commit-hooks.yaml` is still stale at `tools/bin/` with no task covering it — recorded in Working notes. Next: task 4 — CLAUDE.md `## Build` + CONTEXT.md missing sections.
- Task 4 done: added `## Build` to CLAUDE.md (after the H1; make targets, uv basics, code/test layout, single-test invocation) and `## Example dialogue` + `## Flagged ambiguities` to CONTEXT.md (after `## Relationships`, matching the standard's order). repo-audit dropped 11→8 (all three doc-shape findings cleared); `make check` green (405 pass, 2 deselected). Next: task 5 — declare two judgments, fill the cache, drop the two Makefile `--deselect` flags for a full green pytest.
