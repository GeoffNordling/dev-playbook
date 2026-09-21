---
type: General-Sheet
title: Python Family Rule Audit
description: The rule audit over the python/ family — every rule's kind, detector coverage, repo state, and overlap, with escalations for what breaks or is weakly checked
---

# Python Family Rule Audit

The family holds ten rules, all in
[Python Style](/standards/python/style.md). No reclassification is
proposed in either direction: every trailer already carries the kind the
predicate earns. Five rules break: `python.docstrings`,
`python.fail-loudly`, `python.helper-justification`,
`python.helper-placement`, and `python.annotated-signatures`.
`python.helper-placement` is the widest of them — the repo defines its
single-use helpers above their callers, and the predicate asks for
beneath, so 218 of 310 single-caller helpers are false of it. Three
rules are weakly checked, and all three miss the same 23 files: every
`scripts/` entry point and two other Python files carry no `.py`
extension, so neither `ruff check`, nor `ruff format`, nor `mypy` ever
reads one. Five rules are checked by nothing at all, their verifier rows
null. No rule is low value; three of the five that break should be met
by rewriting the predicate, and two by changing the repo.

| id | rule | kind | proposed | check | state | overlap | value | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `python.empty-init` | "A file named `__init__.py` holds no character other than whitespace: no docstring, no import, no re-export, no `__all__` declaration, and no other code." | deterministic | deterministic | full | holds | none | high | Test: read the file, flag any non-whitespace byte. All six tracked `__init__.py` files are zero bytes. `check_empty_init` in `scripts/python-lint:108` is the predicate exactly. |
| `python.docstrings` | "Every module, class, function, and method in the file carries a docstring, except a file named `__init__.py` and a pytest test function, whose name begins with `test_`." | deterministic | deterministic | weak | breaks | `python.docstring-content` | high | ruff's `D` family skips private and nested names, all of `tests/**`, and every extensionless file. 167 members lack one, among them `src/dev_playbook/testing_lint.py:132`. |
| `python.docstring-content` | "A docstring in the file says in plain English what the module, class, function, or method it documents does." | stochastic | stochastic | none | holds | `python.docstrings` | high | Verifier row null. "Says in plain English what it does" judges the text. Every docstring read in `src/dev_playbook/pyast.py`, `prose_lint.py`, and `testing_lint.py` states the behavior. |
| `python.fail-loudly` | "A value the code requires is read directly, so a missing one raises." | stochastic | stochastic | none | breaks | none | high | Verifier row null. "A value that always exists" and "a real runtime state rather than a programming error" both judge. `src/dev_playbook/testing_lint.py:212` breaks it. |
| `python.module-layout` | "A module's top-level statements run in one order:" | deterministic | deterministic | none | holds | none | high | Test: walk `ast.Module.body`, flag an import or a plain-literal `UPPER_SNAKE` assignment after the first `def` or `class`. Zero hits across all 120 members. |
| `python.no-future-annotations` | "`from __future__ import annotations` does not appear in the file, unless one of the file's parent directories is named `build`, `dist`, or `deprecated`." | deterministic | deterministic | full | holds | none | high | `check_no_future` in `scripts/python-lint:94` walks the AST for the import; `FUTURE_EXCLUDE` carries the three named directories. No member holds the import. |
| `python.helper-justification` | "Every helper function in the file is multi-use, substantial in body, a distinct concern at another abstraction level, or an entry in a dispatch table, registry, or strategy map:" | stochastic | stochastic | none | breaks | none | high | Verifier row null; "substantial in body" judges. 105 single-use helpers outside `tests/` have two statements or fewer; `scripts/repo-lint:211` is the plainest. |
| `python.helper-placement` | "A helper function sits directly beneath the function that uses it, or, where two or more functions use it, in a `# ---` banner section." | deterministic | deterministic | none | breaks | none | high | Verifier row null. 218 single-caller helpers sit above their caller with no banner, among them `scripts/python-lint:94` and `src/dev_playbook/workspace_lint.py` (23 of them). |
| `python.formatted-by-ruff-format` | "The file is byte-identical to the output of `ruff format` run under the `line-length` that the canonical pyproject.toml pins." | deterministic | deterministic | weak | unknown | none | high | The `ruff-format` hook takes `types_or: [python, pyi, jupyter]`, and `identify` tags none of the 23 extensionless members python. `make format-check` skips them too. |
| `python.annotated-signatures` | "Every function and method in the file annotates each parameter, except a `self` or `cls` first parameter, and its return." | deterministic | deterministic | weak | breaks | none | high | `make typecheck` runs `mypy src tests`, so `scripts/`, `dotfiles/`, and `working-docs/` are unread. Seven signatures break, six in `scripts/griffe-outline`. |

The population read for this audit is the 120 Python files this repo
tracks: 97 with a `.py` extension, and 23 with none and a Python shebang.
The 23 are the 21 entry points under `scripts/`,
`dotfiles/dot-claude/hooks/measure-event`, and
`working-docs/software-factory/code/traverse-issue`. Every one of the 23
opens `#!/usr/bin/env -S uv run --script`, which
[The Python Project](/standards/build/python.md#shebang-and-inline-metadata)
requires of an executable Python file under `scripts/`. That shebang is
what puts the three tool-checked rules out of reach; the escalations
below say why.

## Escalations

### `python.docstrings` — "Every module, class, function, and method in the file carries a docstring, except a file named `__init__.py` and a pytest test function, whose name begins with `test_`."

The predicate names two exemptions and no others. ruff's `D` family,
named in the verifier table as `ruff-check`, applies three more.

First, `D` is off for every file under `tests/`. The repo's
`pyproject.toml:68` sets `"**/tests/**" = ["D"]`, so the exemption
reaches the whole tree, not the test functions the predicate names.
[Python Explanation](/standards/python/explanation.md#which-docstrings-matter)
is explicit about the difference: "A test module's own helpers, the
factories and fixtures defined as plain functions, carry docstrings:
their names are not similarly load-bearing." Three such helpers carry
none — `tests/transcript_fakes.py:142` `completed`, `:147` `not_found`,
and `:155` `runner` — and neither does the factory at
`tests/conftest.py:80`. Eleven test classes in
`tests/dev_playbook/test_md.py` carry none either, at lines 12, 32, 106,
119, 148, 164, 199, 210, 255, 293, and 300; a class is not a test
function, so no exemption reaches them.

Second, pydocstyle decides `D101`, `D102`, and `D103` over public names
alone, so an underscore-prefixed name and every member of an
underscore-prefixed class are exempt in the tool and bound in the
predicate. `src/dev_playbook/testing_lint.py:132` is the case:

```python
class _PrivacyVisitor(ast.NodeVisitor):
    ...
    def __init__(self, rel: str) -> None:
        self.rel = rel
```

The class carries a docstring; its `__init__` does not, and `D107` never
fires because the enclosing class is private. Fourteen private
definitions under `src/` are unchecked the same way, and six nested
functions on top of that.

Third, the 23 extensionless members are never passed to ruff at all, so
47 public definitions in `scripts/` carry no docstring, among them
`scripts/python-lint:94` `check_no_future`, `:123` `scan_file`, and
`:138` `main`, and 25 definitions in `scripts/repo-lint`.

The three gaps together account for all 167 missing docstrings.

Proposal: change the repo. The predicate states what the repo plainly
wants — the explanation argues the test-helper case in its own words,
and the detector gap over `scripts/` is an accident of file naming, not
a decision. Narrow `pyproject.toml`'s per-file ignore from `"**/tests/**"`
to the test functions and test classes alone, and bring the 23
extensionless files into ruff's reach, which
`python.formatted-by-ruff-format` needs anyway. That is one config change
and a docstring pass over `scripts/`, `tests/`, and the private
definitions under `src/`.

### `python.fail-loudly` — "A value the code requires is read directly, so a missing one raises."

The predicate lists five shapes that hide a missing value, each "over a
value that always exists", and says a legitimate fallback "carries an
inline comment giving that reason".
`src/dev_playbook/testing_lint.py:209-213` is the fourth shape with no
such comment:

```python
    def _add(self, node: ast.AST, message: str) -> None:
        self.findings.append(
            Finding(
                self.rel, getattr(node, "lineno", 0), ACCESS_ONLY_PUBLIC_NAMES, message
            )
        )
```

`_add` has three call sites, at lines 154, 193, and 203. They pass an
`ast.ImportFrom`, an `ast.Attribute`, and whatever `_flag_private_segments`
received, which is an `ast.Import` or an `ast.ImportFrom`. All four node
classes always carry `lineno`. The annotation is the wide `ast.AST`, so
the attribute is unprovable to mypy, but the value always exists at
runtime and the `0` default can only ever hide a defect: a finding
reported at line 0 points at nothing.

The rest of the family passes on inspection. The 121 candidate shapes
outside `tests/` are almost all over genuinely optional values —
`hook.get("entry", "")` at `src/dev_playbook/boundary_table.py:166`
reads a pre-commit hook key that a hook may legitimately omit, and
`data.get("jobs") or {}` at `:245` reads a workflow key the same way.

Proposal: change the repo. One call, one file, and the fix is the
narrower annotation the call sites already satisfy: take
`node: ast.stmt | ast.expr` and read `node.lineno` directly. The
predicate states the repo's own principle, the explanation carries it at
length, and a single unguarded default is an oversight rather than a
decision.

### `python.helper-justification` — "Every helper function in the file is multi-use, substantial in body, a distinct concern at another abstraction level, or an entry in a dispatch table, registry, or strategy map:"

The predicate's own words rule out the case the repo keeps: "A one-line
or two-line helper called once is pure relocation", and "Symmetry with
siblings, prior existence, and speculative reuse justify no helper: a
trivial single-use function beside two siblings of the same shape is
still trivial."

`scripts/repo-lint:204-216` holds the pair:

```python
def canonical_text(name: str) -> str:
    try:
        return (CANONICAL_DIR / name).read_text(encoding="utf-8")
    except OSError as err:
        raise ToolError(f"cannot read canonical artifact: {err}") from err


def canonical_raw(name: str) -> bytes:
    try:
        return (CANONICAL_DIR / name).read_bytes()
    except OSError as err:
        raise ToolError(f"cannot read canonical artifact: {err}") from err
```

`canonical_raw` is one statement and has one call site, at
`scripts/repo-lint:407`. It exists beside `canonical_text` in the same
shape, which is the symmetry the predicate names and refuses.

It is not alone: 105 helpers outside `tests/` have one call site and two
statements or fewer. Some earn their place on the fourth clause —
`src/dev_playbook/cloa_viewer/refresh.py:35` `_now` and `:40` `_clear`
are seams the tests replace — but many do not, such as
`scripts/repo-lint:211` above, `scripts/repo-lint:412`
`gitignore_patterns`, and `src/dev_playbook/cloa_viewer/cli.py:68`
`dist_dir`.

Proposal: rewrite. The count is too large to call an oversight, and the
verifier row is null, so nothing has ever held the repo to it. Keep the
four justifications and add the one the repo actually uses: "Every
helper function in the file is multi-use, substantial in body, a
distinct concern at another abstraction level, an entry in a dispatch
table, registry, or strategy map, or a named seam its tests replace."
That admits `_now` and `_clear` and still refuses `canonical_raw`,
which leaves a real bar rather than one the repo ignores wholesale.

### `python.helper-placement` — "A helper function sits directly beneath the function that uses it, or, where two or more functions use it, in a `# ---` banner section."

The repo orders its modules bottom-up: a helper is defined above the
function that calls it, not beneath. 310 module-level functions in the
population have exactly one caller in their own file. Only 28 of them
sit directly beneath that caller. 262 sit above it, and 218 of those
have no `# ---` banner within 25 lines.

`scripts/python-lint`, the family's own detector, is the pattern in
miniature: `check_no_future` at line 94 and `check_empty_init` at line
108 are called only by `scan_file` at line 123, which is called only by
`main` at line 138. Every helper precedes its user.
`scripts/harness-files-lint` does the same at a larger scale —
`check_disable_model_invocation:311`, `check_arguments:327`,
`body_length_advisory:390`, and `check_references_depth:405` all serve
`audit_skill:442` and all sit above it. The heaviest files are
`src/dev_playbook/workspace_lint.py` with 23 such helpers and
`scripts/repo-lint` with 15.

The banner clause is real and used —
`src/dev_playbook/testing_lint.py:217` opens
`# --- mirror-layout rule ---`, and `scripts/repo-lint:218` opens
`# --- verbatim line-block compares (.pre-commit-config.yaml, Makefile) ---`
— so the second half of the predicate matches the repo. Only the
direction of the first half does not.

Proposal: rewrite. Turn "beneath" into "above": "A helper function sits
directly above the function that uses it, or, where two or more
functions use it, in a `# ---` banner section." Changing the repo would
mean reordering 218 definitions across 40-odd files for no reader's
benefit, and the ordering is not accidental — a module read top to bottom
introduces each name before its use, which is the same discipline
`python.module-layout` applies to constants. The rewrite should also say
what a helper is, since nothing in the family defines the term; "a
module-level function called from another function in the same file" is
the reading this audit used.

### `python.formatted-by-ruff-format` — "The file is byte-identical to the output of `ruff format` run under the `line-length` that the canonical pyproject.toml pins."

The verifier table names `ruff-format`, the pinned
`astral-sh/ruff-pre-commit` hook at `v0.15.20`. Its manifest gives
`types_or: [python, pyi, jupyter]`, so pre-commit passes it only the
files `identify` tags `python`. `identify` tags an extensionless file by
its shebang interpreter, and
`/home/geoff/.local/share/uv/tools/pre-commit/lib/python3.12/site-packages/identify/identify.py`
strips a leading `/usr/bin/env` and an `-S`, leaving `uv` as the command
word. `uv` is absent from `INTERPRETERS` in the sibling
`interpreters.py`, so a file opening `#!/usr/bin/env -S uv run --script`
gets no `python` tag and never reaches the hook.

The second path is no better. `make format-check` runs
`ruff format --check .`, and ruff's default `include` is `["*.py",
"*.pyi", "**/pyproject.toml"]`, so directory discovery passes over a
file with no extension.

All 23 extensionless members are therefore unformatted by any gate:
every entry point under `scripts/`,
`dotfiles/dot-claude/hooks/measure-event`, and
`working-docs/software-factory/code/traverse-issue`. That is 19 percent
of the population. The state is `unknown` rather than `holds` or
`breaks` because this audit runs no detector, and for these 23 files a
run would be informative rather than vacuous — `ruff format --check`
over them is the one command that settles it.

The fix is one key. `[tool.ruff]` accepts `extend-include`, and
`extend-include = ["scripts/*"]` in both `pyproject.toml` and
`standards/build/canonical/pyproject.toml` brings the discovery path
into line with the predicate. The hook path needs `files:` or
`types_or: [python, file]` on the two ruff hooks in
`.pre-commit-config.yaml`. Because the canonical file pins
`tool.ruff.line-length` and the rules around it
([pyproject.toml](/standards/build/canonical.md#pyprojecttoml)), the
canonical copy has to change alongside.

### `python.annotated-signatures` — "Every function and method in the file annotates each parameter, except a `self` or `cls` first parameter, and its return."

The verifier table names `mypy`, and
[Canonical Artifacts](/standards/build/canonical.md#makefile) makes the
Makefile the invocation. `Makefile:11-12` reads:

```make
typecheck:
	uv run mypy src tests
```

Two directories, named literally. `scripts/`, `dotfiles/`, and
`working-docs/` are never typechecked, which is the same 23-file gap as
the two ruff rules plus every `.py` file outside `src/` and `tests/`.
`disallow_untyped_defs` and `disallow_incomplete_defs` are both on in
`pyproject.toml:80-81`, so the tool would decide the predicate in full
over anything it were given.

Seven signatures break the predicate, all in files mypy never reads:

- `scripts/griffe-outline:21` `members_of_kind` — `parent`, `kind`, and the return.
- `scripts/griffe-outline:37` `format_param` — `p` and the return.
- `scripts/griffe-outline:46` `format_function` — `func`, `indent`, and the return.
- `scripts/griffe-outline:63` `format_class` — `indent` and the return.
- `scripts/griffe-outline:96` `format_module` — `mod`, `path`, and the return.
- `scripts/griffe-outline:122` `main` — the return.
- `scripts/harness-files-lint:573` `main` — the return.

Proposal: change the repo. Six of the seven sit in one file, and
`scripts/harness-files-lint:573` is a bare `def main():` beside 20 fully
annotated siblings in the same file, which makes it an oversight rather
than a decision. Widen `make typecheck` to `mypy src tests scripts` and
annotate the seven. The Makefile recipe is compared line by line by
`scripts/repo-lint` against
`standards/build/canonical/Makefile`, so that file changes with it.

## Detectors

**`scripts/python-lint`** decides two of the ten rules and is the only
first-party code in the family. `check_empty_init` at line 108 reads
every `__init__.py` and flags any non-whitespace byte, which is
`python.empty-init` word for word. `check_no_future` at line 94 walks
the AST for an `ImportFrom` naming `__future__` with an `annotations`
alias, and `FUTURE_EXCLUDE` at line 76 skips a file under a directory
named `build`, `dist`, or `deprecated`, matching the predicate's
exception; the cache names it also skips are gitignored and outside the
population either way. `RULES` at line 50 answers `--list-rules` with
the two ids as module constants, so the declared set cannot drift from
what the code emits. `tests/test_python_lint.py` covers both rules over
a `tmp_path` repo, including an extensionless `#!/usr/bin/env python3`
member at line 53 and the repo's own self-scan at line 176.

**`src/dev_playbook/pyast.py`** is the walk behind that script, not a
detector itself. `find_python_files` shells out to
`git ls-files --cached --others --exclude-standard`, so discovery is
gitignore-aware and worktree-scoped, and `looks_python` admits a `.py`
file or an extensionless file whose first line starts with one of the
three prefixes in `PYTHON_SHEBANG_PREFIXES`. That list is what makes
`scripts/` visible to python-lint while it stays invisible to ruff and
mypy.

**`ruff-check`** decides `python.docstrings`. It is the pinned
`astral-sh/ruff-pre-commit` hook at `v0.15.20`, and the rule reaches it
through `DEPENDENCY_RULES` in
`src/dev_playbook/verifier_table.py:87`. The deciding configuration is
`pyproject.toml`: `select` carries `D`, `ignore` carries `D401`,
`convention = "pep257"`, and the per-file ignores drop `D` for
`"**/tests/**"` and `D104` for `__init__.py`. Its scope is narrower than
the predicate on three counts, set out in the escalation above.

**`ruff-format`** decides `python.formatted-by-ruff-format`, mapped at
`src/dev_playbook/verifier_table.py:88`. The hook runs `ruff format
--force-exclude` over the files pre-commit hands it; `make format-check`
runs `ruff format --check .`. Both paths are extension-driven and miss
the 23 extensionless members.

**`mypy`** decides `python.annotated-signatures`, mapped at
`src/dev_playbook/verifier_table.py:85`. The address is a dependency
name rather than a hook id, so the invocation is the Makefile's
`uv run mypy src tests`, run at the push gate alone per
`standards/boundaries.yaml`. `disallow_untyped_defs` and
`disallow_incomplete_defs` in `pyproject.toml` together make a partly
annotated signature an error, so within its two directories the check is
exact.

**`scripts/verifier-table`** decides no rule of this family but holds the
map that binds three of them to their tools. `DEPENDENCY_RULES` in
`src/dev_playbook/verifier_table.py:84-90` names `mypy`, `ruff-check`,
and `ruff-format` with one python rule each, and
`standard.an-emitted-id-is-a-rule-heading` fails the table if any of the
three ids stops being a declared deterministic rule.

The five rules with a null row — `python.docstring-content`,
`python.fail-loudly`, `python.module-layout`,
`python.helper-justification`, and `python.helper-placement` — are
decided by a reviewer. Two of them, `python.module-layout` and
`python.helper-placement`, are deterministic and mechanical: the audit
decided both with a short AST walk over `ast.Module.body`, which is what
a first-party detector would run.
