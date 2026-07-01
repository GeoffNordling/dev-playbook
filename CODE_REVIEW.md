# Code Review — commit 3857c00 "OKF phase G: consolidate pre-commit to 6 hooks / 2 shared libraries"

**Work order for the fixing agent: fix ONLY the items under "Fix these" below.**
Everything under "Reviewed — do NOT fix" was found, verified, and deliberately
accepted by the human reviewer. The acceptance criterion is: **silent failures get
fixed; loud failures are acceptable** (fail fast and loud is this workspace's
convention — a traceback or a false positive that blocks a commit is annoying but
self-announcing; a validator that quietly stops validating is not).

Review scope: the full HEAD~1..HEAD diff (22 files, +1684/−905). Every finding below
was verified — reproduced against constructed repro repos, compared with the old
behavior via `git show HEAD~1:`, or confirmed by direct inspection.

**Baseline health (verified in this worktree):** `ref-check` 151 refs ok, `okf-lint`
clean across 37 concept docs / 9 indexes, `python-lint` clean across 60 files, tools
suite 375 passed with only the 2 pre-existing judgment-gate cache misses documented
in PLAN.md. The commit's PLAN.md claims check out. The consolidation is well built —
the findings below don't change that verdict.

---

## Fix these — silent failures

### F1. ref-check silently stopped validating citations inside link text — regression
`tools/bin/ref-check:168` — CONFIRMED by repro

`remainder = md.MD_LINK_PATTERN.sub("", stripped)` deletes the *entire*
`[text](target)` span — link text included — before the bare-citation pass runs.

- Repro: doc containing `[see ~/workspace/dev-playbook/does-not-exist.md now](https://example.com)`
  → old ref-check: exit 1, citation reported broken; new: exit 0, "no cross-references
  found". A stale `~/workspace` path in link text now passes forever, silently.
- Currently latent: no tracked markdown in the workspace has a bare citation in link
  text today (the one candidate, `standards/README.md:11`, carries the citation in the
  link *target*, which the in-link branch still validates). Fix it before it isn't.
- Fix: substitute link spans with their text — `md.MD_LINK_PATTERN.sub(r"\1", stripped)`
  — so link text stays visible to `WORKSPACE_REF_PATTERN` while targets (already handled
  by the first pass) are removed. Add a regression test to `tools/tests/test_ref_check.py`
  for a citation inside link text.

### F2. okf-lint: one malformed frontmatter silently unlints the rest of the bundle
`tools/bin/okf-lint:278` (mechanism at `frontmatter_of`, line 108) — CONFIRMED by repro

`check_types`/`check_indexes` run outside main's `try`. A concept doc whose frontmatter
YAML is malformed (e.g. `type: [unclosed`) raises `yaml.parser.ParserError` out of
`frontmatter_of`; a non-UTF-8 doc raises `UnicodeDecodeError`.

- Repro: raw traceback, exit 1, **zero findings emitted, offending file never named,
  and every other file in the bundle goes unlinted**. The crash is loud; the mass
  un-linting and the missing filename are the silent part.
- Fix: catch the parse failure per file (in `frontmatter_of` or its two call sites —
  `check_types` line 117 and the description compare in `check_indexes` line 218) and
  emit a `Finding(rel, "okf.frontmatter", <error summary>)`, then continue scanning the
  remaining files. Exit stays 1 with findings, the file is named, nothing else is
  skipped. Add a test: bundle with one malformed-frontmatter doc → finding names that
  doc, sibling docs still validated.

### F3. Shared walk silently exempts trees the old hooks policed — regression
`tools/lib/pyast.py:15` (`EXCLUDE_DIRS`) — CONFIRMED by repro

The shared walk's exclusions apply to all three merged rules. The retired empty-init
had *no* directory exclusions (every tracked `__init__.py` was policed); old
test-privacy's exclude set did not include `deprecated`, `build`, `dist`, `.agents`,
`.dhub`.

- Repro: tracked non-empty `deprecated/pkg/__init__.py` → old empty-init exit 1; new
  python-lint passes **silently**. Same for privacy violations in `.agents`/`.dhub`
  test trees.
- Currently latent: verified there are zero tracked `__init__.py` / `test_*.py` files
  under those directories in any workspace repo today. The hole is real but empty.
- Fix: restore old coverage with per-rule exclusion sets (empty-init: no directory
  exclusions beyond what git ls-files already drops; test-privacy: the old, smaller
  set) — or, if the narrowing is actually wanted, state it in
  `standards/python-conventions.md` so it's a documented decision instead of an
  accident. Either way, pin the choice with a test.

### F4. okf-lint index checks silently accept junk and duplicate bullets
`tools/bin/okf-lint:169` (`parse_index`) and `:204` (`check_indexes`) — CONFIRMED by inspection

- A bullet whose target classifies as harness/excluded (`- [Plan](/PLAN.md) — …`,
  `- [Claude](/CLAUDE.md) — …`) is silently dropped by `parse_index`'s
  `elif md.classify(target) == "concept"` — neither listed nor flagged as extra —
  despite the INDEX_BULLET comment ("caught, not silently skipped") and the "lists
  exactly the concept documents it owns" contract.
- `dict(listed_concepts)` collapses duplicate bullets for the same target last-wins:
  a doc listed twice (first with a wrong description) is reported clean, and the
  duplication itself is never surfaced.
- Currently latent: no index bullet in the repo points at a harness/excluded target
  today.
- Fix: emit findings for non-concept bullet targets (e.g. "lists X which is not a
  concept document") and for duplicate targets. Add tests for both.

---

## Reviewed — do NOT fix

Verified findings, deliberately accepted. Loud failures are acceptable here; consumer
repos that haven't adopted OKF are not a concern; cleanup is not this pass's job.

**Loud failures (acceptable by convention):**
- Exit-contract violations: uncaught `CalledProcessError` from the git walk → traceback,
  exit 1 instead of documented 2, git stderr swallowed (`tools/bin/python-lint:238`,
  also with a file argument at `:234`; `tools/bin/okf-lint:271` — `OSError` doesn't
  cover `CalledProcessError`).
- `pyast.parse` lets `UnicodeDecodeError` escape, contradicting its docstring
  (`tools/lib/pyast.py:102`) — non-UTF-8 `.py` → traceback.
- The walk includes `--others`: an untracked scratch `__init__.py` blocks commits
  (`tools/lib/pyast.py:73`; old contract asserted by the deleted
  `test_untracked_init_is_not_scanned`), and the self-scan tests fail on any untracked
  scratch `.md`/`.py` in the working tree.
- ref-check false positive on protocol-relative URLs: `[cdn](//host/lib.js)` resolved
  as a repo path, reported broken (`tools/bin/ref-check:158`).
- `parse_frontmatter` misses CRLF / EOF-without-trailing-newline frontmatter → false
  "no OKF frontmatter" (`tools/lib/md.py:114`).
- test-privacy misflags relative imports — `node.level` ignored
  (`tools/bin/python-lint:140`); pre-existing, ported verbatim. Sibling parity gap:
  `conftest.py` / `tests/helpers.py` are never privacy-scanned themselves.

**Out of scope (consumer repos):**
- okf-lint resolves `standards/document-types.md` against the consumer's root and
  `always_run`s → exit 2 on every commit in a non-OKF repo (`tools/bin/okf-lint:79`).
  Not a concern: repos without OKF won't run it.
- Retired exported ids (`test-privacy`, `no-future-annotations`, `empty-init`) hard-error
  pinned consumers on rev bump (writing-style-corpus and spec-tools pin them today);
  no migration note. Loud, consumers' problem, accepted.
- ref-check now validates every root-absolute `[text](/path)` link in pinned consumers
  (old: prose). Intended for OKF repos; loud where it bites.

**Cleanup / latent (leave for a dedicated pass):**
- Link extraction defined three ways: `md.markdown_links` has zero production callers;
  ref-check re-inlines its body (`:142-148`); okf-lint's INDEX_BULLET embeds a third
  regex copy.
- git-walk duplicated verbatim across `md.find_md_files`/`pyast.find_python_files`;
  `ToolError`/`Finding`/report-tail copy-pasted across okf-lint/python-lint (third
  variant in internal-skill-audit); okf-lint parses each concept doc's frontmatter
  twice (`frontmatter_of` uncached); `make_repo` fixture re-implemented in two test
  files alongside `conftest.py:13`.
- Docstring rule violations (python-conventions.md "Docstrings") across the new
  functions/classes and test helpers.
- `always_run: true` on okf-lint/python-lint pays the full walk on commits that touch
  no markdown/Python; `types:` filters would skip them.
- `RESOURCE_REQUIRED_TYPES` hardcodes registry knowledge (`tools/bin/okf-lint:47`);
  `classify()` hardcodes transient `PLAN.md` (`tools/lib/md.py:151`).
- Mixed-fence toggling: a ``` line inside a ~~~ fence wrongly closes it
  (`tools/lib/md.py:68`); pre-existing, no tracked file nests mixed fences.
- Doc nits: commit message says "6 hooks" but the new manifest exports 5 (the old one
  exported 6); tools/README.md:38's blanket claim is inaccurate for judgments-lint
  (no repo-root argument) and internal-skill-audit (glob discovery, not git ls-files).

---

## Machine-readable fix list

Only the silent failures — the fixing agent's queue:

```json
[
  {"id": "F1", "file": "tools/bin/ref-check", "line": 168, "summary": "Citations inside markdown link text are no longer validated: MD_LINK_PATTERN.sub('', ...) removes the whole [text](target) span before the bare-citation pass (regression).", "fix": "Substitute link spans with their text (sub(r'\\1', ...)) so link text stays scannable; add a regression test for a citation inside link text.", "failure_scenario": "[see ~/workspace/dev-playbook/does-not-exist.md now](https://example.com) → old: exit 1 broken; new: exit 0 — stale citation passes forever."},
  {"id": "F2", "file": "tools/bin/okf-lint", "line": 278, "summary": "One malformed-YAML (or non-UTF-8) frontmatter aborts the scan: offending file never named, every other file silently unlinted.", "fix": "Catch the parse failure per file and emit Finding(rel, 'okf.frontmatter', ...) at both frontmatter_of call sites; continue scanning; test that siblings still get linted.", "failure_scenario": "Concept doc with 'type: [unclosed' → ParserError traceback, exit 1, zero findings, rest of bundle unchecked."},
  {"id": "F3", "file": "tools/lib/pyast.py", "line": 15, "summary": "EXCLUDE_DIRS applies to all three merged rules, silently exempting trees the old hooks policed (old empty-init had no directory exclusions; old test-privacy's set was smaller).", "fix": "Per-rule exclusion sets restoring old coverage (or document the narrowing as a decision in python-conventions.md); pin with a test.", "failure_scenario": "Tracked non-empty deprecated/pkg/__init__.py → old exit 1, new passes silently."},
  {"id": "F4", "file": "tools/bin/okf-lint", "line": 169, "summary": "parse_index silently drops bullets whose target classifies harness/excluded, and dict(listed_concepts) collapses duplicate bullets last-wins (line 204).", "fix": "Emit findings for non-concept bullet targets and for duplicate targets; add tests for both.", "failure_scenario": "Index listing '- [Plan](/PLAN.md) — x' or the same doc twice with one wrong description → okf-lint clean."}
]
```
